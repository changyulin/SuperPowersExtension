from __future__ import annotations

import importlib.util
import tempfile
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "memory_cli.py"
SPEC = importlib.util.spec_from_file_location("memory_cli", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
memory_cli = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = memory_cli
SPEC.loader.exec_module(memory_cli)


class BuildPathsTests(unittest.TestCase):
    def test_project_memory_root_uses_docs_experience_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            paths = memory_cli.build_paths(str(project_root))

        expected_root = project_root / "docs" / "experience-memory"
        self.assertEqual(paths.project_memory_root, expected_root)
        self.assertEqual(paths.project_learnings, expected_root / "learnings.jsonl")
        self.assertEqual(paths.project_solutions, expected_root / "solutions")
        self.assertEqual(paths.project_decisions, expected_root / "decisions")


if __name__ == "__main__":
    unittest.main()
