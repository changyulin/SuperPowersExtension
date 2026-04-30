from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

        expected_root = project_root.resolve() / "docs" / "experience-memory"
        self.assertEqual(paths.project_memory_root, expected_root)
        self.assertEqual(paths.project_learnings, expected_root / "learnings.jsonl")
        self.assertEqual(paths.project_solutions, expected_root / "solutions")
        self.assertEqual(paths.project_decisions, expected_root / "decisions")


class ReadJsonlTests(unittest.TestCase):
    def test_read_jsonl_supports_utf8_and_gbk_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "learnings.jsonl"
            utf8_line = {
                "id": "utf8-entry",
                "title": "UTF-8 记录",
            }
            gbk_line = {
                "id": "gbk-entry",
                "title": "GBK 记录",
            }

            path.write_bytes(
                (json.dumps(utf8_line, ensure_ascii=False) + "\n").encode("utf-8")
                + (json.dumps(gbk_line, ensure_ascii=False) + "\n").encode("gbk")
            )

            rows = memory_cli.read_jsonl(path)

        self.assertEqual(rows, [utf8_line, gbk_line])


class ConfigureStdioTests(unittest.TestCase):
    def test_configure_stdio_reconfigures_stdout_and_stderr_to_utf8(self) -> None:
        stdout = mock.Mock()
        stderr = mock.Mock()

        with (
            mock.patch.object(memory_cli.sys, "stdout", stdout),
            mock.patch.object(memory_cli.sys, "stderr", stderr),
        ):
            memory_cli.configure_stdio()

        stdout.reconfigure.assert_called_once_with(
            encoding="utf-8",
            errors="strict",
        )
        stderr.reconfigure.assert_called_once_with(
            encoding="utf-8",
            errors="backslashreplace",
        )


if __name__ == "__main__":
    unittest.main()
