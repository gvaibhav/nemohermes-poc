#!/usr/bin/env python3
"""
Unit and integration tests for PoC: Toil Reduction via SKILL.md.

Tests cover:
  - Rogue process lifecycle (spawn → kill → verify dead)
  - SKILL.md creation with valid YAML frontmatter and trigger phrases
  - Full 3-turn simulation end-to-end
  - SKILL.md trigger parsing
"""

import os
import signal
import subprocess
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure usecases is importable
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from usecases.poc_toil_reduction_skill import (
    SKILL_FILE,
    SKILLS_DIR,
    PROJECT_ROOT,
    start_rogue_process,
    simulate_turn_1,
    simulate_turn_2,
    simulate_turn_3,
    parse_skill_triggers,
    cleanup_all_spawned,
    _safe_kill,
    _spawned_pids,
)


class TestRogueProcessLifecycle(unittest.TestCase):
    """Tests for spawning and killing rogue processes."""

    def tearDown(self):
        """Guarantee no leaked processes after each test."""
        cleanup_all_spawned()

    def test_start_rogue_process_returns_valid_pid(self):
        """start_rogue_process() should return a positive PID."""
        pid = start_rogue_process()
        self.assertGreater(pid, 0)

    def test_rogue_process_can_be_killed(self):
        """A spawned rogue process should be killable via SIGKILL."""
        pid = start_rogue_process()
        killed = _safe_kill(pid)
        self.assertTrue(killed)
        # Give OS time to reap
        time.sleep(0.3)


class TestSkillFileOperations(unittest.TestCase):
    """Tests for SKILL.md creation, content, and parsing."""

    def setUp(self):
        """Remove any existing SKILL.md before each test."""
        if SKILL_FILE.exists():
            SKILL_FILE.unlink()

    def tearDown(self):
        """Clean up generated SKILL.md after each test."""
        if SKILL_FILE.exists():
            SKILL_FILE.unlink()
        cleanup_all_spawned()

    def test_skill_directory_creation(self):
        """simulate_turn_2() should create the skills directory."""
        if SKILLS_DIR.exists():
            import shutil
            shutil.rmtree(SKILLS_DIR)
        simulate_turn_2()
        self.assertTrue(SKILLS_DIR.exists())
        self.assertTrue(SKILL_FILE.exists())

    def test_skill_file_has_yaml_frontmatter(self):
        """Generated SKILL.md should contain valid YAML frontmatter."""
        simulate_turn_2()
        content = SKILL_FILE.read_text()
        # Must start with --- and have a second --- delimiter
        self.assertTrue(content.startswith("---"))
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3,
                                "SKILL.md missing YAML frontmatter delimiters")

    def test_skill_file_contains_required_fields(self):
        """Frontmatter should have name, description, triggers, version."""
        simulate_turn_2()
        import yaml
        content = SKILL_FILE.read_text()
        parts = content.split("---", 2)
        meta = yaml.safe_load(parts[1])
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta["name"], "cpu_sweep")
        self.assertIn("triggers", meta)
        self.assertIn("version", meta)
        self.assertIn("description", meta)

    def test_skill_triggers_include_cpu_sweep(self):
        """At least one trigger should match 'cpu sweep' (case-insensitive)."""
        simulate_turn_2()
        triggers = parse_skill_triggers(SKILL_FILE)
        matched = any("cpu sweep" in t.lower() for t in triggers)
        self.assertTrue(matched, f"No 'cpu sweep' trigger found: {triggers}")

    def test_skill_body_contains_action_commands(self):
        """SKILL.md body should document the ps and pkill commands."""
        simulate_turn_2()
        content = SKILL_FILE.read_text()
        self.assertIn("ps aux", content)
        self.assertIn("pkill", content)

    def test_parse_skill_triggers_empty_file(self):
        """parse_skill_triggers on a non-YAML file returns empty list."""
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        SKILL_FILE.write_text("no frontmatter here")
        triggers = parse_skill_triggers(SKILL_FILE)
        self.assertEqual(triggers, [])


class TestTurnSimulations(unittest.TestCase):
    """Integration tests for the full 3-turn PoC sequence."""

    def setUp(self):
        if SKILL_FILE.exists():
            SKILL_FILE.unlink()

    def tearDown(self):
        if SKILL_FILE.exists():
            SKILL_FILE.unlink()
        cleanup_all_spawned()

    def test_turn_1_kills_rogue_process(self):
        """Turn 1 should terminate the provided rogue PID."""
        pid = start_rogue_process()
        simulate_turn_1(pid)
        time.sleep(0.3)
        # Process should no longer be running
        try:
            os.kill(pid, 0)  # signal 0 = check existence
            self.fail(f"PID {pid} still alive after Turn 1")
        except ProcessLookupError:
            pass  # expected — process is dead

    def test_turn_2_creates_skill_file(self):
        """Turn 2 should produce a SKILL.md file."""
        simulate_turn_2()
        self.assertTrue(SKILL_FILE.exists())

    def test_turn_3_requires_skill_file(self):
        """Turn 3 should raise if SKILL.md doesn't exist."""
        # Do NOT run Turn 2 first
        with self.assertRaises(RuntimeError):
            simulate_turn_3()

    def test_full_sequence_end_to_end(self):
        """Full Turn 1 → Turn 2 → Turn 3 should complete without error."""
        pid = start_rogue_process()
        simulate_turn_1(pid)
        simulate_turn_2()
        simulate_turn_3()  # Should not raise


if __name__ == "__main__":
    unittest.main()
