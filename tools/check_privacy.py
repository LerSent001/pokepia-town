#!/usr/bin/env python3
"""Fail when tracked files contain common workstation-specific paths or addresses."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "macOS home directory": re.compile(b"/" + rb"Users/[^/\x00\r\n]+/"),
    "Linux home directory": re.compile(b"/" + rb"home/[^/\x00\r\n]+/"),
    "Windows home directory": re.compile(rb"[A-Za-z]:\\\\Users\\\\[^\\\x00\r\n]+\\\\"),
    "file URL": re.compile(rb"file://(?:localhost)?/(?:Users|home)/", re.IGNORECASE),
    "private IPv4 address": re.compile(
        rb"(?<![0-9])(?:10(?:\.[0-9]{1,3}){3}|192\.168(?:\.[0-9]{1,3}){2}|172\.(?:1[6-9]|2[0-9]|3[01])(?:\.[0-9]{1,3}){2})(?![0-9])"
    ),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    )
    return [ROOT / item.decode("utf-8") for item in output.split(b"\0") if item]


def main() -> int:
    failures: list[tuple[Path, str]] = []
    for path in tracked_files():
        if not path.is_file():
            continue
        data = path.read_bytes()
        for label, pattern in PATTERNS.items():
            if pattern.search(data):
                failures.append((path.relative_to(ROOT), label))

    if failures:
        print("Privacy check failed:")
        for path, label in failures:
            print(f"- {path}: {label}")
        return 1

    print("Privacy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
