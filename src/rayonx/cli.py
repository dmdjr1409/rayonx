import argparse
from pathlib import Path
import sys

from rayonx import __version__
from rayonx.cleaner import clean_paths
from rayonx.engine import scan_paths
from rayonx.reporter import (
    bold,
    cyan,
    generate_badge_markdown,
    green,
    print_scan_report,
    render_banner,
)
from rayonx.walker import walk_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rayonx",
        description="Audit and clean AI code smell and trivial comments from codebases.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"rayonx {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    check_cmd = subparsers.add_parser("check", help="Scan codebase for AI slop and compute Humanity Score.")
    check_cmd.add_argument("path", nargs="?", default=".", help="Target directory or file (default: current directory)")

    clean_cmd = subparsers.add_parser("clean", help="Safely strip removable AI comments in-place.")
    clean_cmd.add_argument("path", nargs="?", default=".", help="Target directory or file (default: current directory)")
    clean_cmd.add_argument("--dry-run", action="store_true", help="Preview deletions as unified diff without writing changes")

    badge_cmd = subparsers.add_parser("badge", help="Generate a Shields.io Markdown badge for your README.")
    badge_cmd.add_argument("path", nargs="?", default=".", help="Target directory (default: current directory)")

    audit_cmd = subparsers.add_parser("git-audit", help="Audit Git commit history for AI co-author leaks.")
    audit_cmd.add_argument("path", nargs="?", default=".", help="Target Git repository (default: current directory)")
    audit_cmd.add_argument("--max-count", type=int, default=50, help="Max commits to inspect (default: 50)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    command = args.command
    if not command:
        command = "check"
        target_path_str = "."
    else:
        target_path_str = getattr(args, "path", ".")

    target = Path(target_path_str).resolve()
    if not target.exists():
        print(f"Error: Target path '{target}' does not exist.", file=sys.stderr)
        return 1

    files = list(walk_paths(target))
    if not files:
        print(f"No supported code or markdown files found in {target}.")
        return 0

    if command == "check":
        result = scan_paths(files)
        print_scan_report(result, base_dir=target if target.is_dir() else target.parent)
        return 0 if len(result.findings) == 0 else 1

    if command == "clean":
        dry_run = getattr(args, "dry_run", False)
        print(render_banner())
        mode_label = cyan("[DRY RUN]") if dry_run else green("[IN-PLACE]")
        print(f"Running cleaner {mode_label} on {len(files)} files...\n")

        removed_total, diffs = clean_paths(files, dry_run=dry_run)
        if removed_total == 0:
            print(f" {green('✔')} No removable AI slop found. Codebase is clean.")
            return 0

        for path, diff in diffs:
            rel = path.relative_to(target) if target.is_dir() and path.is_relative_to(target) else path
            print(f" {bold(str(rel))}:")
            for line in diff.splitlines()[:15]:
                print(f"   {line}")
            print()

        action = "would be stripped" if dry_run else "successfully stripped"
        print(f"Total: {bold(str(removed_total))} trivial lines {action} across {len(diffs)} files.")
        return 0

    if command == "badge":
        result = scan_paths(files)
        badge = generate_badge_markdown(result.human_score)
        print("\n" + bold("Markdown Badge for README.md:"))
        print(f"\n{badge}\n")
        return 0

    if command == "git-audit":
        max_count = getattr(args, "max_count", 50)
        return run_git_audit(target, max_count=max_count)

    return 0


def run_git_audit(repo_path: Path, max_count: int = 50) -> int:
    import subprocess
    import re

    print(render_banner())
    target_dir = repo_path if repo_path.is_dir() else repo_path.parent
    git_dir = target_dir / ".git"
    if not git_dir.exists():
        print(f"Error: '{target_dir}' is not a Git repository.", file=sys.stderr)
        return 1

    cmd = [
        "git",
        "log",
        f"-n{max_count}",
        "--format=%H%x1f%an%x1f%ae%x1f%s%x1f%b%x1e",
    ]
    try:
        proc = subprocess.run(
            cmd, cwd=target_dir, capture_output=True, text=True, check=True
        )
    except (subprocess.SubprocessError, OSError) as e:
        print(f"Error reading git log: {e}", file=sys.stderr)
        return 1

    records = [r for r in proc.stdout.split("\x1e") if r.strip()]
    ai_leak_pattern = re.compile(
        r"(co-authored-by:\s*(claude|codex|chatgpt|copilot|cursor|anthropic|openai)|"
        r"noreply@anthropic\.com|noreply@openai\.com)",
        re.IGNORECASE,
    )

    findings: list[tuple[str, str, str, str]] = []
    for rec in records:
        parts = rec.strip().split("\x1f")
        if len(parts) < 4:
            continue
        commit_hash, author, email, subject = parts[0], parts[1], parts[2], parts[3]
        body = parts[4] if len(parts) > 4 else ""
        full_text = f"{author} {email} {subject}\n{body}"
        match = ai_leak_pattern.search(full_text)
        if match:
            findings.append((commit_hash[:7], author, subject, match.group(0)))

    print(bold(f"Git History Audit ({len(records)} recent commits inspected):"))
    if not findings:
        print(f" {green('✔')} No AI co-authorship leaks detected. Commits are 100% human-attributed.\n")
        return 0

    for short_hash, author, subject, leak in findings:
        print(f"\n  {red('[!]')} Commit {bold(short_hash)} ({author}):")
        print(f"      Subject: {subject}")
        print(f"      {red('Leak   :')} {leak}")

    print("\n" + bold(f"Summary: Found {red(str(len(findings)))} commit(s) with AI co-authorship headers."))
    print(dim("Tip: To remove AI co-authorship from the latest commit, run:"))
    print(cyan("  git commit --amend --no-edit\n"))
    return 1


if __name__ == "__main__":
    sys.exit(main())
