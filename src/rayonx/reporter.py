import sys
from pathlib import Path
from rayonx.engine import ScanResult
from rayonx.rules import IssueKind

USE_COLOR = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return _c(text, "1")


def dim(text: str) -> str:
    return _c(text, "2")


def green(text: str) -> str:
    return _c(text, "32")


def yellow(text: str) -> str:
    return _c(text, "33")


def red(text: str) -> str:
    return _c(text, "31")


def cyan(text: str) -> str:
    return _c(text, "36")


def render_banner() -> str:
    lines = [
        bold(cyan("  ____                              __  __")),
        bold(cyan(" |  _ \\ __ _ _   _  ___  _ __       \\ \\/ /")),
        bold(cyan(" | |_) / _` | | | |/ _ \\| '_ \\ _____ \\  / ")),
        bold(cyan(" |  _ < (_| | |_| | (_) | | | |_____ /  \\ ")),
        bold(cyan(" |_| \\_\\__,_|\\__, |\\___/|_| |_|     /_/\\_\\")),
        bold(cyan("             |___/                        ")),
        dim(" AI Code Smell & Slop Cleaner — v0.1.0"),
        "",
    ]
    return "\n".join(lines)


def render_score_bar(score: int, width: int = 24) -> str:
    filled = int((score / 100.0) * width)
    bar = "█" * filled + "░" * (width - filled)
    if score >= 90:
        return f"{green(bar)} {bold(green(f'{score}% Human'))}"
    if score >= 70:
        return f"{yellow(bar)} {bold(yellow(f'{score}% Human'))}"
    return f"{red(bar)} {bold(red(f'{score}% Human'))}"


def print_scan_report(result: ScanResult, base_dir: Path | None = None) -> None:
    print(render_banner())

    if not result.findings:
        print(f" {green('✔')} No AI slop or redundant filler detected across {bold(str(result.total_files))} files.")
        print(f" Score: {render_score_bar(100)}\n")
        return

    print(bold("Detected AI Slop & Code Smells:"))
    current_file = None

    for finding in result.findings:
        display_path = (
            finding.file_path.relative_to(base_dir)
            if base_dir and finding.file_path.is_relative_to(base_dir)
            else finding.file_path
        )

        if current_file != display_path:
            current_file = display_path
            print(f"\n  {bold(str(display_path))}")

        kind_tag = cyan(f"[{finding.rule.code}]")
        print(f"    {dim(str(finding.line_number))}: {kind_tag} {finding.rule.description}")
        print(f"       {dim('>')} {finding.line_content}")

    print("\n" + bold("Summary:"))
    print(f"  Files scanned : {result.total_files}")
    print(f"  Lines analyzed: {result.total_lines:,}")
    print(f"  Slop findings : {red(str(len(result.findings)))}")

    by_kind = result.issues_by_kind
    if by_kind.get(IssueKind.TRIVIAL_COMMENT):
        print(f"    - Trivial comments  : {by_kind[IssueKind.TRIVIAL_COMMENT]}")
    if by_kind.get(IssueKind.AI_VERBOSITY):
        print(f"    - LLM verbosity     : {by_kind[IssueKind.AI_VERBOSITY]}")
    if by_kind.get(IssueKind.GHOST_BLOCK):
        print(f"    - Blind ghost blocks: {by_kind[IssueKind.GHOST_BLOCK]}")
    if by_kind.get(IssueKind.MARKDOWN_SLOP):
        print(f"    - Markdown slop     : {by_kind[IssueKind.MARKDOWN_SLOP]}")

    print(f"\n  Humanity Index: {render_score_bar(result.human_score)}")
    print(dim("  (Tip: Run with `rayonx clean` to strip auto-removable slop)\n"))


def generate_badge_markdown(score: int, username: str = "dmdjr1409", repo: str = "rayonx") -> str:
    color = "brightgreen" if score >= 90 else ("yellow" if score >= 70 else "red")
    url = f"https://img.shields.io/badge/RayonX-{score}%25%20Human-{color}"
    return f"[![RayonX Humanity Score]({url})](https://github.com/{username}/{repo})"
