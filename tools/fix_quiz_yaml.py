#!/usr/bin/env python3
"""Repair quiz YAML scalars that are invalid unquoted, and report what it changed.

Two YAML rules bite in this course's quiz files:

1. A plain (unquoted) scalar may not begin with a reserved indicator character. A backtick is
   one of them, so an option that opens with inline code - `docker compose down` stops ... -
   is a parse error, not a style choice.
2. A plain scalar containing ": " (colon-space) inside a block sequence is read as a mapping,
   so an option mentioning `ports: - "8080:8080"` becomes a sequence entry containing a mapping
   and the whole document fails.

Both are fixed the same way: quote the scalar and escape what needs escaping inside double
quotes. Content is preserved byte for byte; only the quoting changes.

Usage:  python tools/fix_quiz_yaml.py [--check]
"""

from __future__ import annotations

import glob
import sys

RESERVED_STARTS = set("`@%&*!|>{}[],\"#?'")
OPTION_RE = ("    - ", "    - ")  # top-level option entry under a question

# Only these files are rewritten. The script never touches lesson markdown.
def quiz_files() -> list[str]:
    return sorted(glob.glob("lessons/**/*.quiz.yaml", recursive=True)) + sorted(
        glob.glob("assessments/*.quiz.yaml")
    )


def option_line(line: str) -> bool:
    return line.startswith("    - ")


def already_quoted(text: str) -> bool:
    return len(text) >= 2 and text[0] in "\"'" and text[-1] == text[0]


def needs_quotes(text: str) -> bool:
    if already_quoted(text):
        return False
    if text[:1] in RESERVED_STARTS:
        return True
    # ": " or a trailing ":" makes a plain scalar read as a mapping.
    if ": " in text or text.endswith(":"):
        return True
    if " #" in text:  # a comment marker preceded by a space
        return True
    return False


def double_quote(text: str) -> str:
    out = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{out}"'


def fix(path: str, check_only: bool) -> list[str]:
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    changes: list[str] = []
    out: list[str] = []
    for n, line in enumerate(lines, start=1):
        if option_line(line):
            body = line[len(OPTION_RE[0]):]
            if needs_quotes(body):
                new = "    - " + double_quote(body)
                changes.append(f"  line {n}: {body[:70]}...")
                out.append(new)
                continue
        out.append(line)
    if changes and not check_only:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(out))
    return changes


def main() -> int:
    check_only = "--check" in sys.argv
    total = 0
    for path in quiz_files():
        changes = fix(path, check_only)
        if changes:
            print(f"{path}  ({len(changes)} line(s))")
            for c in changes:
                print(c)
            total += len(changes)
    print(f"\n{total} line(s) {'would be ' if check_only else ''}fixed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())