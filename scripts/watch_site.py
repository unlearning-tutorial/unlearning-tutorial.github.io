#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WATCH_DIRS = ("content", "templates")
WATCH_FILES = ("index.html", "styles.css", "article.css")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Watch tutorial sources and rebuild the site on save."
    )
    parser.add_argument(
        "--output-dir",
        default="_site",
        help="Directory passed through to scripts/build_site.py.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.75,
        help="Polling interval in seconds.",
    )
    return parser.parse_args()


def watched_paths() -> list[Path]:
    paths: list[Path] = []
    for dirname in WATCH_DIRS:
        paths.extend(sorted((ROOT / dirname).rglob("*")))
    for filename in WATCH_FILES:
        paths.append(ROOT / filename)
    return [path for path in paths if path.is_file()]


def snapshot_mtimes() -> dict[Path, int]:
    snapshot: dict[Path, int] = {}
    for path in watched_paths():
        snapshot[path] = path.stat().st_mtime_ns
    return snapshot


def run_build(output_dir: str) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / "build_site.py")]
    if output_dir != "_site":
        cmd.extend(["--output-dir", output_dir])

    print(f"[watch] rebuilding with {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode == 0:
        print("[watch] build succeeded", flush=True)
    else:
        print(f"[watch] build failed with exit code {result.returncode}", flush=True)
    return result.returncode


def main() -> None:
    args = parse_args()
    previous = snapshot_mtimes()
    run_build(args.output_dir)

    print("[watch] watching for changes. Press Ctrl+C to stop.", flush=True)
    try:
        while True:
            time.sleep(args.interval)
            current = snapshot_mtimes()
            if current != previous:
                changed = sorted(
                    str(path.relative_to(ROOT))
                    for path, mtime in current.items()
                    if previous.get(path) != mtime
                )
                removed = sorted(
                    str(path.relative_to(ROOT))
                    for path in previous
                    if path not in current
                )
                if changed:
                    print(f"[watch] changed: {', '.join(changed)}", flush=True)
                if removed:
                    print(f"[watch] removed: {', '.join(removed)}", flush=True)
                previous = current
                run_build(args.output_dir)
    except KeyboardInterrupt:
        print("\n[watch] stopped", flush=True)


if __name__ == "__main__":
    main()
