#!/usr/bin/env python3
import unittest, subprocess, json, yaml
from pathlib import Path

HOME = Path.home()
SETTINGS = HOME / ".claude/settings.json"
CLAUDE_MD = HOME / ".claude/CLAUDE.md"


class TestImageAssertions(unittest.TestCase):
    def test_rtk_installed(self):
        r = subprocess.run("rtk --version", shell=True, capture_output=True)
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
        for entry in spec["commands"]["startup"]:
            r = subprocess.run(entry["command"])
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
