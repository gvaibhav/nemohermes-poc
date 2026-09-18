#!/usr/bin/env python3
import unittest
import os
import subprocess
from pathlib import Path
from usecases.poc_toil_reduction_skill import SKILL_FILE, SKILLS_DIR, start_rogue_process


class TestPoCToilReduction(unittest.TestCase):

    def setUp(self):
        if SKILL_FILE.exists():
            SKILL_FILE.unlink()

    def test_skill_file_creation(self):
        self.assertFalse(SKILL_FILE.exists())
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        SKILL_FILE.write_text("test skill")
        self.assertTrue(SKILL_FILE.exists())

    def test_rogue_process_termination(self):
        pid = start_rogue_process()
        self.assertTrue(pid > 0)
        try:
            os.kill(pid, 9)
        except Exception:
            pass
        try:
            res = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            self.assertNotIn(str(pid), res.stdout)
        except PermissionError:
            pass


if __name__ == "__main__":
    unittest.main()
