import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from rayonx.rules import (
    AI_VERBOSITY_RULES,
    MARKDOWN_SLOP_RULES,
    TRIVIAL_COMMENT_RULES,
    IssueKind,
    Rule,
)


@dataclass
class Finding:
    file_path: Path
    line_number: int
    rule: Rule
    line_content: str


@dataclass
class ScanResult:
    total_files: int = 0
    total_lines: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def human_score(self) -> int:
        if self.total_lines == 0:
            return 100
        slop_density = (len(self.findings) * 100.0) / max(self.total_lines, 1)
        score = 100.0 - (slop_density * 8.0)
        return max(0, min(100, int(round(score))))

    @property
    def issues_by_kind(self) -> dict[IssueKind, int]:
        counts: dict[IssueKind, int] = {k: 0 for k in IssueKind}
        for f in self.findings:
            counts[f.rule.kind] = counts.get(f.rule.kind, 0) + 1
        return counts


class PythonAstChecker(ast.NodeVisitor):
    def __init__(self, file_path: Path, lines: Sequence[str]) -> None:
        self.file_path = file_path
        self.lines = lines
        self.findings: list[Finding] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            line_idx = max(0, node.lineno - 1)
            line_content = self.lines[line_idx].strip() if line_idx < len(self.lines) else "except: pass"
            rule = Rule(
                code="RX203",
                kind=IssueKind.GHOST_BLOCK,
                description="Blind empty try/except block suppressing all errors",
                pattern=TRIVIAL_COMMENT_RULES[0].pattern,
                is_removable=False,
            )
            self.findings.append(Finding(self.file_path, node.lineno, rule, line_content))
        self.generic_visit(node)


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    lines = content.splitlines()
    is_markdown = path.suffix.lower() in {".md", ".mdx"}

    active_rules: list[Rule] = []
    if is_markdown:
        active_rules.extend(MARKDOWN_SLOP_RULES)
    else:
        active_rules.extend(TRIVIAL_COMMENT_RULES)
        active_rules.extend(AI_VERBOSITY_RULES)

    for idx, line in enumerate(lines, start=1):
        for rule in active_rules:
            if rule.pattern.search(line):
                findings.append(Finding(path, idx, rule, line.strip()))

    if path.suffix.lower() == ".py":
        try:
            tree = ast.parse(content, filename=str(path))
            checker = PythonAstChecker(path, lines)
            checker.visit(tree)
            findings.extend(checker.findings)
        except SyntaxError:
            return findings

    return findings


def scan_paths(paths: Sequence[Path]) -> ScanResult:
    result = ScanResult()
    for path in paths:
        result.total_files += 1
        try:
            line_count = sum(1 for _ in path.open("rb"))
        except OSError:
            line_count = 0
        result.total_lines += line_count
        result.findings.extend(scan_file(path))
    return result
