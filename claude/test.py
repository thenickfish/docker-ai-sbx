#!/usr/bin/env python3
import unittest, subprocess, json, yaml, tempfile
from pathlib import Path

HOME = Path.home()
SETTINGS = HOME / ".claude/settings.json"
CLAUDE_MD = HOME / ".claude/CLAUDE.md"
STATUSLINE = HOME / ".claude/statusline.sh"


class TestImageAssertions(unittest.TestCase):
    def test_rtk_installed(self):
        r = subprocess.run("rtk --version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_devbox_installed(self):
        r = subprocess.run("devbox version", shell=True, capture_output=True)
        self.assertEqual(r.returncode, 0)

    def test_caveman_skills_present(self):
        skills = list((HOME / ".claude/skills").glob("*caveman*"))
        self.assertGreater(len(skills), 0, "no caveman skills found")

    def test_caveman_plugin_registered(self):
        self.assertTrue((HOME / ".claude/plugins/cache/caveman").exists())


class TestSpecYamlStartup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("spec.yaml") as f:
            spec = yaml.safe_load(f)
        # sbx's real startup dispatcher runs with a minimal PATH that
        # excludes /home/agent/.local/bin — a bare `env=` inheriting the
        # build shell's PATH would hide that and let a script depending on
        # e.g. rtk silently pass here while failing 127 in the real sandbox.
        minimal_env = {"PATH": "/usr/bin:/bin", "HOME": str(HOME)}
        for entry in spec["commands"]["startup"]:
            r = subprocess.run(entry["command"], env=minimal_env)
            if r.returncode != 0:
                raise RuntimeError(f"startup command failed with exit {r.returncode}")
        cls.settings = json.loads(SETTINGS.read_text())

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
        self.assertIn("activate /caveman full immediately", CLAUDE_MD.read_text())

    def test_claude_md_sandbox_guidance(self):
        content = CLAUDE_MD.read_text()
        self.assertIn("isolated Docker sandbox", content)
        self.assertIn("Network access is restricted", content)
        self.assertIn("platform-specific build artifacts", content)

    def test_statusline_configured(self):
        status_line = self.settings.get("statusLine", {})
        self.assertEqual(status_line.get("type"), "command")
        self.assertEqual(status_line.get("command"), str(STATUSLINE))

    def test_statusline_script_runs(self):
        self.assertTrue(STATUSLINE.exists())
        self.assertTrue(STATUSLINE.stat().st_mode & 0o111, "statusline.sh is not executable")
        sample = json.dumps({
            "model": {"display_name": "Test Model"},
            "workspace": {"current_dir": str(HOME)},
        })
        r = subprocess.run(
            [str(STATUSLINE)], input=sample, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(HOME)},
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Test Model", r.stdout)

    def test_statusline_cost_and_context_pct(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            # First line simulates a byte-boundary cut mid-record — the
            # script's `tail -c | tail -n +2` must discard it, not choke on it.
            f.write('{"broken":\n')
            f.write(json.dumps({"message": {"usage": {"input_tokens": 100, "output_tokens": 50}}}) + "\n")
            # input + cache_creation + cache_read = 20000 -> 10% of the 200k
            # window. output_tokens is deliberately huge (50000): if the
            # script wrongly folds it into the context total, this would
            # read 35% instead of 10%, so the test catches that regression.
            f.write(json.dumps({"message": {"usage": {
                "input_tokens": 15000, "output_tokens": 50000,
                "cache_creation_input_tokens": 2000, "cache_read_input_tokens": 3000,
            }}}) + "\n")
            transcript_path = f.name
        try:
            sample = json.dumps({
                "model": {"display_name": "Test Model"},
                "workspace": {"current_dir": str(HOME)},
                "cost": {"total_cost_usd": 0.1234},
                "transcript_path": transcript_path,
            })
            r = subprocess.run(
                [str(STATUSLINE)], input=sample, capture_output=True, text=True,
                env={"PATH": "/usr/bin:/bin", "HOME": str(HOME)},
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("$0.1234", r.stdout)
            self.assertIn("10% ctx", r.stdout)
        finally:
            Path(transcript_path).unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
