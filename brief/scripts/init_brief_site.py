#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_template(target: Path, force: bool) -> None:
    skill_dir = Path(__file__).resolve().parents[1]
    template = skill_dir / "assets" / "brief-site-template"

    if not template.exists():
        raise SystemExit(f"Template not found: {template}")

    if target.exists() and any(target.iterdir()):
        if not force:
            raise SystemExit(
                f"Target exists and is not empty: {target}\n"
                "Pass --force to replace it."
            )
        shutil.rmtree(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        template,
        target,
        ignore=shutil.ignore_patterns("node_modules", "dist", ".git", ".DS_Store"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a Brief site from the bundled template.")
    parser.add_argument("target", help="Target project directory")
    parser.add_argument("--force", action="store_true", help="Replace an existing non-empty target")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    copy_template(target, args.force)
    print(f"Brief site initialized at {target}")
    print("Next: cd into the project, run npm install, then npm run dev or npm run build.")


if __name__ == "__main__":
    main()
