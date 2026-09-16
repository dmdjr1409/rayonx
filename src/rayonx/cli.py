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

    return 0


if __name__ == "__main__":
    sys.exit(main())
