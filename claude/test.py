#!/usr/bin/env python3
import unittest, subprocess, json, re, yaml
from pathlib import Path

HOME = Path.home()
SETTINGS = HOME / ".claude/settings.json"
STATUSLINE = HOME / ".claude/statusline/statusline.sh"

# claude-kit/spec.yaml is passed in as the `kit` named context (see docker-bake.hcl)
SPEC_PATH = "kit-spec.yaml"
KIT_IMPORT = "@/home/agent/.claude/kits-agent-context/claude-kit.md"


def load_spec():
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


def capability(spec, type_prefix):
    return next(c for c in spec["capabilities"] if c["type"].startswith(type_prefix))


def startup_commands(spec):
    return capability(spec, "com.docker.sandbox/lifecycle")["config"]["startup"]


def kit_settings(spec):
    """The settings.json fragment embedded as a heredoc in the first startup hook."""
    script = startup_commands(spec)[0]["command"][-1]
    m = re.search(r"<<'KIT_SETTINGS_EOF'[^\n]*\n[^\n]*\n(.*?)\n\s*KIT_SETTINGS_EOF", script, re.S)
    return json.loads(m.group(1))


def kit_claude_md(spec):
    return capability(spec, "com.docker.sandbox/agent-context@2")["config"]["content"]


class TestImageAssertions(unittest.TestCase):
    def test_rtk_installed(self):
        r = subprocess.run("rtk --version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_devbox_installed(self):
        r = subprocess.run("devbox version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_nix_installed(self):
        r = subprocess.run("nix --version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_op_installed(self):
        r = subprocess.run("op --version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_caveman_skills_present(self):
        skills = list((HOME / ".claude/skills").glob("*caveman*"))
        self.assertGreater(len(skills), 0, "no caveman skills found")

    def test_caveman_plugin_registered(self):
        self.assertTrue((HOME / ".claude/plugins/cache/caveman").exists())


class TestKitFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = load_spec()
        cls.settings = kit_settings(spec)
        cls.claude_md = kit_claude_md(spec)

    def test_rtk_hook(self):
        pre_tool_hooks = self.settings.get("hooks", {}).get("PreToolUse", [])
        rtk_hook = any(
            h.get("command") == "rtk hook claude"
            for entry in pre_tool_hooks
            for h in entry.get("hooks", [])
        )
        self.assertTrue(rtk_hook)

    def test_skip_dangerous_mode(self):
        self.assertTrue(self.settings.get("skipDangerousModePermissionPrompt"))

    def test_caveman_plugin_enabled(self):
        self.assertTrue(self.settings.get("enabledPlugins", {}).get("caveman@caveman"))

    def test_claude_md_caveman_line(self):
        self.assertIn("activate /caveman full immediately", self.claude_md)

    def test_claude_md_sandbox_constraints(self):
        self.assertIn("isolated Docker sandbox", self.claude_md)
        self.assertIn("platform-specific build artifacts", self.claude_md)

    def test_claude_md_network_guidance(self):
        self.assertIn("Outbound network is restricted", self.claude_md)
        self.assertIn("stop immediately", self.claude_md)
        self.assertIn("sbx policy approval ls", self.claude_md)

    def test_claude_md_local_dev_tools_section(self):
        self.assertIn("## Local dev tools", self.claude_md)

    def test_claude_md_devbox_guidance(self):
        self.assertIn("devbox", self.claude_md)
        self.assertIn("devbox add", self.claude_md)

    def test_claude_md_op_guidance(self):
        self.assertIn("op", self.claude_md)
        self.assertIn("no authenticated session", self.claude_md)

    def test_statusline_configured(self):
        status_line = self.settings.get("statusLine", {})
        self.assertEqual(status_line.get("type"), "command")
        self.assertEqual(status_line.get("command"), str(STATUSLINE))


class TestKitDeployment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()
        # Simulate a freshly created sandbox: sbx writes a CLAUDE.md before startup hooks run
        (HOME / ".claude").mkdir(parents=True, exist_ok=True)
        (HOME / ".claude/CLAUDE.md").write_text("# sbx generated\n")
        minimal_env = {"PATH": "/usr/bin:/bin", "HOME": str(HOME)}
        for entry in startup_commands(cls.spec):
            r = subprocess.run(entry["command"], env=minimal_env)
            if r.returncode != 0:
                raise RuntimeError(f"startup command failed with exit {r.returncode}")

    def test_schema_version(self):
        self.assertEqual(self.spec["schemaVersion"], "3")
        self.assertEqual(self.spec["kind"], "mixin")

    def test_deployed_rtk_hook(self):
        settings = json.loads(SETTINGS.read_text())
        pre_tool_hooks = settings.get("hooks", {}).get("PreToolUse", [])
        rtk_hook = any(
            h.get("command") == "rtk hook claude"
            for entry in pre_tool_hooks
            for h in entry.get("hooks", [])
        )
        self.assertTrue(rtk_hook, "rtk hook missing from deployed settings.json")

    def test_deployed_caveman_plugin(self):
        settings = json.loads(SETTINGS.read_text())
        self.assertTrue(
            settings.get("enabledPlugins", {}).get("caveman@caveman"),
            "caveman plugin missing from deployed settings.json after startup",
        )

    def test_deployed_statusline_setting(self):
        settings = json.loads(SETTINGS.read_text())
        status_line = settings.get("statusLine", {})
        self.assertEqual(status_line.get("type"), "command")
        self.assertEqual(status_line.get("command"), str(STATUSLINE))

    def test_deployed_claude_md(self):
        claude_md = (HOME / ".claude/CLAUDE.md").read_text()
        self.assertIn(KIT_IMPORT, claude_md.splitlines())

    def test_statusline_script_runs(self):
        self.assertTrue(STATUSLINE.exists())
        self.assertTrue(STATUSLINE.stat().st_mode & 0o111, "statusline.sh is not executable")
        sample = json.dumps({
            "model": {"display_name": "Test Model"},
            "cwd": str(HOME),
        })
        r = subprocess.run(
            [str(STATUSLINE)], input=sample, capture_output=True, text=True,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(HOME)},
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Test Model", r.stdout)

    def test_statusline_context_window(self):
        sample = json.dumps({
            "model": {"display_name": "Test Model"},
            "cwd": str(HOME),
            "context_window": {
                "context_window_size": 200000,
                "current_usage": {
                    "input_tokens": 20000,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                },
            },
        })
        r = subprocess.run(
            [str(STATUSLINE)], input=sample, capture_output=True, text=True,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(HOME)},
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.strip(), "statusline produced no output")


class TestSettingsMergePreservesUserKeys(unittest.TestCase):
    """Regression test: Claude Code rewrites settings.json during normal use
    (theme picker, bypass-permissions accept, etc.) and that rewrite drops
    unknown keys. The every-start merge must reassert kit keys without
    discarding keys Claude Code itself owns.

    The startup command hardcodes /home/agent/.claude (the dispatcher's
    minimal env may not set $HOME), so this operates on the real HOME like
    TestKitDeployment — safe only inside the disposable test-stage container.
    """

    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()
        (HOME / ".claude").mkdir(parents=True, exist_ok=True)
        (HOME / ".claude/settings.json").write_text(json.dumps({
            "themeId": 1,
            "alwaysThinkingEnabled": True,
            "bypassPermissionsModeAccepted": True,
        }))
        minimal_env = {"PATH": "/usr/bin:/bin", "HOME": str(HOME)}
        for entry in startup_commands(cls.spec):
            r = subprocess.run(entry["command"], env=minimal_env)
            if r.returncode != 0:
                raise RuntimeError(f"startup command failed with exit {r.returncode}")
        cls.settings = json.loads(SETTINGS.read_text())

    def test_preserves_claude_code_own_keys(self):
        self.assertEqual(self.settings.get("themeId"), 1)
        self.assertTrue(self.settings.get("alwaysThinkingEnabled"))
        self.assertTrue(self.settings.get("bypassPermissionsModeAccepted"))

    def test_reasserts_kit_statusline(self):
        status_line = self.settings.get("statusLine", {})
        self.assertEqual(status_line.get("type"), "command")
        self.assertEqual(status_line.get("command"), str(STATUSLINE))

    def test_reasserts_kit_rtk_hook(self):
        pre_tool_hooks = self.settings.get("hooks", {}).get("PreToolUse", [])
        rtk_hook = any(
            h.get("command") == "rtk hook claude"
            for entry in pre_tool_hooks
            for h in entry.get("hooks", [])
        )
        self.assertTrue(rtk_hook)

    def test_reasserts_kit_caveman_plugin(self):
        self.assertTrue(self.settings.get("enabledPlugins", {}).get("caveman@caveman"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
