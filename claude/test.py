#!/usr/bin/env python3
import unittest, subprocess, json, yaml
from pathlib import Path

HOME = Path.home()
SETTINGS = HOME / ".claude/settings.json"
STATUSLINE = HOME / ".claude/statusline/statusline.sh"

FILES_HOME = Path("files/home")
KIT_SETTINGS = FILES_HOME / ".claude/kit-settings.json"
KIT_CLAUDE_MD = FILES_HOME / ".claude/CLAUDE.md"


class TestImageAssertions(unittest.TestCase):
    def test_rtk_installed(self):
        r = subprocess.run("rtk --version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_devbox_installed(self):
        r = subprocess.run("devbox version", shell=True, capture_output=True)
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
        cls.settings = json.loads(KIT_SETTINGS.read_text())
        cls.claude_md = KIT_CLAUDE_MD.read_text()

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
        import shutil
        with open("spec.yaml") as f:
            cls.spec = yaml.safe_load(f)
        # Simulate v2 kit delivery: files/home/ applied before startup commands
        shutil.copytree("files/home", str(HOME), dirs_exist_ok=True)
        minimal_env = {"PATH": "/usr/bin:/bin", "HOME": str(HOME)}
        for entry in cls.spec["setup"].get("startup", []):
            r = subprocess.run(entry["command"], env=minimal_env)
            if r.returncode != 0:
                raise RuntimeError(f"startup command failed with exit {r.returncode}")

    def test_schema_version(self):
        self.assertEqual(self.spec["schemaVersion"], "2")

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
        self.assertIn("activate /caveman full immediately", claude_md)
        self.assertIn("Outbound network is restricted", claude_md)

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
        import shutil
        with open("spec.yaml") as f:
            cls.spec = yaml.safe_load(f)
        shutil.copytree("files/home", str(HOME), dirs_exist_ok=True)
        (HOME / ".claude").mkdir(parents=True, exist_ok=True)
        (HOME / ".claude/settings.json").write_text(json.dumps({
            "themeId": 1,
            "alwaysThinkingEnabled": True,
            "bypassPermissionsModeAccepted": True,
        }))
        minimal_env = {"PATH": "/usr/bin:/bin", "HOME": str(HOME)}
        for entry in cls.spec["setup"].get("startup", []):
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
