#!/usr/bin/env python3
"""Normalise the `correct` answer positions across every quiz file.

The import checker fails the course unless the correct option appears at each of positions 0, 1, 2
and 3 for between 15% and 35% of all questions. Keeping that true by hand across 59 files is a
reliable way to end up with every answer at position B.

This script enforces a deterministic rule instead:

  * Quiz files are ordered by module, then lesson, with the module quiz last in its module.
  * File N in that order gets an offset of N mod 4.
  * Question j in that file gets `correct` = (offset + j) mod 4.

It reaches that target by ROTATING the options of a question so the option that is currently
correct moves to the required index, then rewriting `correct:`. Question text, option text,
explanations and ids are never touched: only their order within a question changes.

With 45 lesson quizzes of 4 questions and 14 module quizzes of 9, the result is 77/77/76/76 across
306 questions, or 25.2% / 25.2% / 24.8% / 24.8%.

Usage:  python tools/balance_quiz.py [--check]
"""

from __future__ import annotations

import glob
import re
import sys

RESERVED_STARTS = set("`@%&*!|>{}[],\"#?'")


def quiz_files() -> list[str]:
    """Every quiz file, in the course's reading order."""
    lessons: list[tuple[int, int, str]] = []
    modules: list[tuple[int, str]] = []
    for path in glob.glob("lessons/**/*.quiz.yaml", recursive=True):
        m = re.search(r"lessons/module-(\d+)/lesson-(\d+)\.quiz\.yaml$", path.replace("\\", "/"))
        if m:
            lessons.append((int(m.group(1)), int(m.group(2)), path))
    for path in glob.glob("assessments/*.quiz.yaml"):
        m = re.search(r"assessments/module-(\d+)-quiz\.quiz\.yaml$", path.replace("\\", "/"))
        if m:
            modules.append((int(m.group(1)), path))

    ordered: list[str] = []
    for mod in sorted({m for m, _ in modules} | {m for m, _, _ in lessons}):
        ordered += [p for m, n, p in sorted(lessons) if m == mod]
        ordered += [p for m, p in sorted(modules) if m == mod]
    return ordered


def unquote(text: str) -> str:
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    return text


def requote(text: str) -> str:
    if len(text) >= 2 and text[0] in "\"'" and text[-1] == text[0]:
        return text  # already quoted, keep the author's quoting
    if text[:1] in RESERVED_STARTS or ": " in text or text.endswith(":") or " #" in text:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def parse_questions(lines: list[str]) -> list[dict]:
    """Split the file into blocks: the 4 option lines and the `correct:` line of each question."""
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("    - "):
            opts = []
            while i < len(lines) and lines[i].startswith("    - "):
                opts.append(unquote(lines[i][6:]))
                i += 1
            correct_at = None
            while i < len(lines) and not lines[i].startswith("- id:"):
                m = re.match(r"^  correct:\s*(\d+)\s*$", lines[i])
                if m:
                    correct_at = i
                i += 1
            blocks.append({"opts": opts, "correct_line": correct_at})
        else:
            i += 1
    return blocks


def rebalance(path: str, offset: int, apply: bool) -> int:
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    blocks = parse_questions(lines)
    if not blocks:
        return 0
    changes = 0
    for j, block in enumerate(blocks):
        if block["correct_line"] is None or len(block["opts"]) != 4:
            continue
        line = lines[block["correct_line"]]
        current = int(re.match(r"^  correct:\s*(\d+)\s*$", line).group(1))
        target = (offset + j) % 4
        if current == target:
            continue
        shift = (target - current) % 4
        opts = block["opts"]
        rotated = opts[-shift:] + opts[:-shift] if shift else opts
        out = lines[:]
        start = block["correct_line"] - 4
        for k, text in enumerate(rotated):
            out[start + k] = "    - " + requote(text)
        out[block["correct_line"]] = f"  correct: {target}"
        lines = out
        changes += 1
    if changes and apply:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines))
    return changes


def main() -> int:
    apply = "--check" not in sys.argv
    files = quiz_files()
    total = 0
    for idx, path in enumerate(files):
        n = rebalance(path, idx % 4, apply)
        total += n
        if n:
            print(f"{path:58} offset {idx % 4}  {n} question(s) repositioned")
    print(f"\n{len(files)} quiz file(s); {total} question(s) {'would be ' if not apply else ''}repositioned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())