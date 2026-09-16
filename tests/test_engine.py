import tempfile
import unittest
from pathlib import Path

from rayonx.cleaner import clean_content, clean_file
from rayonx.engine import scan_file, scan_paths
from rayonx.rules import IssueKind


class TestRayonXEngine(unittest.TestCase):
    def test_detect_trivial_comments(self) -> None:
        sample_code = (
            "# Import all libraries\n"
            "import os\n"
            "# Initialize the variables\n"
            "count = 0\n"
            "# Loop through each item\n"
            "for i in range(10):\n"
            "    count += i\n"
            "# Return the result\n"
            "print(count)\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(sample_code)
            tmp_path = Path(tmp.name)

        try:
            findings = scan_file(tmp_path)
            kinds = [f.rule.kind for f in findings]
            self.assertEqual(kinds.count(IssueKind.TRIVIAL_COMMENT), 4)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_detect_ghost_block(self) -> None:
        sample_code = (
            "try:\n"
            "    risky_operation()\n"
            "except Exception:\n"
            "    pass\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(sample_code)
            tmp_path = Path(tmp.name)

        try:
            findings = scan_file(tmp_path)
            ghost_findings = [f for f in findings if f.rule.kind == IssueKind.GHOST_BLOCK]
            self.assertEqual(len(ghost_findings), 1)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_clean_removes_trivial_comments(self) -> None:
        dirty = (
            "# Import libraries\n"
            "import math\n"
            "\n"
            "# Return the result\n"
            "def calculate():\n"
            "    return math.pi\n"
        )
        cleaned, count = clean_content(dirty)
        self.assertEqual(count, 2)
        self.assertNotIn("# Import libraries", cleaned)
        self.assertNotIn("# Return the result", cleaned)
        self.assertIn("import math", cleaned)
        self.assertIn("def calculate():", cleaned)

    def test_clean_file_dry_run_preserves_content(self) -> None:
        dirty = "# Initialize variables\nx = 1\n"
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(dirty)
            tmp_path = Path(tmp.name)

        try:
            count, diff = clean_file(tmp_path, dry_run=True)
            self.assertEqual(count, 1)
            self.assertIn("-# Initialize variables", diff)
            self.assertEqual(tmp_path.read_text(), dirty)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_markdown_slop_detection(self) -> None:
        doc = (
            "# My Cool Project\n\n"
            "In today's fast-paced digital world, developers need speed.\n"
            "Insert your API key here.\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
            tmp.write(doc)
            tmp_path = Path(tmp.name)

        try:
            findings = scan_file(tmp_path)
            self.assertEqual(len(findings), 2)
            self.assertTrue(all(f.rule.kind == IssueKind.MARKDOWN_SLOP for f in findings))
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
