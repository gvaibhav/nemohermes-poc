import unittest
import subprocess
from pathlib import Path
import shutil
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "cpu_sweep"
SKILL_FILE = SKILLS_DIR / "SKILL.md"

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        if SKILLS_DIR.exists():
            shutil.rmtree(SKILLS_DIR)

    def tearDown(self):
        if SKILLS_DIR.exists():
            shutil.rmtree(SKILLS_DIR)

    def test_e2e_poc_runner(self):
        # Run the PoC runner in a subprocess
        result = subprocess.run(
            ["python3", str(PROJECT_ROOT / "usecases" / "poc_toil_reduction_skill.py")],
            capture_output=True,
            text=True
        )

        # Assert exit code 0
        self.assertEqual(result.returncode, 0, f"PoC runner failed with output: {result.stdout}\\n{result.stderr}")

        # Assert SKILL.md exists and has frontmatter
        self.assertTrue(SKILL_FILE.exists(), "SKILL.md was not created")
        content = SKILL_FILE.read_text()
        self.assertTrue(content.startswith("---"), "SKILL.md missing frontmatter")

        # Assert no orphan bash processes with "while true"
        ps_result = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True
        )
        orphan_lines = [line for line in ps_result.stdout.splitlines() if "while true" in line and "grep" not in line and "leak" in line]
        self.assertEqual(len(orphan_lines), 0, f"Found orphan processes: {orphan_lines}")

if __name__ == '__main__':
    unittest.main()
