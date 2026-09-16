import difflib
from pathlib import Path
from typing import Sequence

from rayonx.rules import (
    AI_SIGNATURE_RULES,
    AI_VERBOSITY_RULES,
    TRIVIAL_COMMENT_RULES,
    Rule,
)

REMOVABLE_RULES: list[Rule] = [
    r
    for r in (*TRIVIAL_COMMENT_RULES, *AI_VERBOSITY_RULES, *AI_SIGNATURE_RULES)
    if r.is_removable
]


def clean_content(content: str) -> tuple[str, int]:
    lines = content.splitlines(keepends=True)
    cleaned_lines: list[str] = []
    removed_count = 0

    for line in lines:
        stripped = line.strip()
        should_remove = False
        for rule in REMOVABLE_RULES:
            if rule.pattern.search(stripped):
                should_remove = True
                break

        if should_remove:
            removed_count += 1
            continue

        cleaned_lines.append(line)

    return "".join(cleaned_lines), removed_count


def clean_file(path: Path, dry_run: bool = False) -> tuple[int, str]:
    try:
        original = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0, ""

    cleaned, count = clean_content(original)
    if count == 0:
        return 0, ""

    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            cleaned.splitlines(keepends=True),
            fromfile=f"a/{path.name}",
            tofile=f"b/{path.name}",
        )
    )

    if not dry_run:
        path.write_text(cleaned, encoding="utf-8")

    return count, diff


def clean_paths(paths: Sequence[Path], dry_run: bool = False) -> tuple[int, list[tuple[Path, str]]]:
    total_removed = 0
    diffs: list[tuple[Path, str]] = []

    for path in paths:
        if path.suffix.lower() in {".md", ".mdx"}:
            continue
        count, diff = clean_file(path, dry_run=dry_run)
        if count > 0:
            total_removed += count
            diffs.append((path, diff))

    return total_removed, diffs
