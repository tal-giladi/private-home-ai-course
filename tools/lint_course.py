#!/usr/bin/env python3
"""Fast local lint for the course repo. Catches the mistakes the import checker also catches.

Run:  python tools/lint_course.py
Exit code 1 if anything is wrong.

What it checks, and why each one is a real failure rather than a style preference:

  structure   every lesson has exactly one H1 matching its front-matter id and its _sidebar.md
              title; every quiz page has exactly one H1; the ten `##` sections are present, in
              order, with none extra.
  front-matter  parses as a YAML mapping and carries id, module, minutes, objectives and
              last_verified (the keys the importer requires).
  quiz        every .quiz.yaml parses; 3-5 questions per lesson quiz and 8-10 per module quiz;
              exactly 4 distinct options; correct in 0..3; explanation present; no
              "all/none of the above"; the correct option is not conspicuously longer than the
              wrong ones; duplicate ids.
  links       every repo-relative link resolves to a file that exists (after the docsify
              root-fallback the importer applies).
  markdown    no disallowed raw HTML; no Knowledge check / Quiz / Assessment / Answers heading;
              no progress-tracker command; exactly one plain paragraph after the H1.
  balance     correct-answer positions spread across 0-3.
"""

from __future__ import annotations

import collections
import glob
import os
import re
import sys

import yaml

REQUIRED_FM = ["id", "module", "minutes", "objectives", "last_verified"]
SECTIONS = [
    "Why it matters",
    "How it works",
    "Show me",
    "Try it",
    "Break it",
    "Fix it",
    "How do I know it works?",
    "Use it when / avoid it",
    "Reflect",
    "Sources",
]
BAD_HTML = re.compile(r"<(div|script|style|iframe|svg|button|form|input|object|embed)\b|\son\w+\s*=", re.I)
QUIZ_HEADING = re.compile(r"^#{1,3}\s*(Knowledge check|Quiz|Assessment|Answers|Answer Key)\b", re.M)
PROGRESS_CMD = re.compile(r"course\.py\s+(complete|done)")
LINK_RE = re.compile(r"(!?)\[((?:[^[\]]|\[[^\]\n]*\])*)\]\(\s*<?([^()\s<>]+)>?\s*\)")
ALL_NONE = re.compile(r"\b(all|none) of the above\b", re.I)

problems: list[str] = []
stats = collections.Counter()


def bad(msg: str) -> None:
    problems.append(msg)


def split_front_matter(text: str):
    m = re.match(r"^---[ \t]*\r?\n([\s\S]*?)^---[ \t]*(?:\r?\n|$)", text, re.M)
    if not m:
        return {}, text, "no front-matter"
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return {}, text, f"YAML error: {str(e).splitlines()[0]}"
    if not isinstance(data, dict):
        return {}, text, "front-matter is not a mapping"
    return data, text[m.end():], None


def strip_code(md: str) -> str:
    """Remove fenced blocks and inline code, the way the importer does before it looks for HTML."""
    return re.sub(r"`[^`\n]*`", "", re.sub(r"```[\s\S]*?```", "", md))


def sidebar_titles() -> dict[str, str]:
    """repo path -> sidebar link text, for lessons and quiz pages."""
    out: dict[str, str] = {}
    try:
        with open("_sidebar.md", encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"^\s*- \[(.+?)\]\(([^)]+)\)", line)
                if m:
                    out[m.group(2).lstrip("/")] = m.group(1)
    except OSError:
        pass
    return out


def check_links(body: str, where: str, from_path: str) -> None:
    base = os.path.dirname(from_path)
    for _, label, target in LINK_RE.findall(body):
        if target.startswith(("http://", "https://", "mailto:", "#", "//")):
            continue
        target = target.split("#")[0].split("?")[0]
        if not target:
            continue
        # The importer falls back to a repo-root path when the relative one misses (docsify).
        direct = os.path.normpath(os.path.join(base, target)) if not target.startswith("/") else target.lstrip("/")
        root = target.lstrip("/")
        if os.path.exists(direct) or os.path.exists(root):
            continue
        if not target.startswith("/") and target.startswith("..") and os.path.normpath(
            os.path.join(base, target)
        ).startswith(".."):
            bad(f"{where}: link {label!r} -> {target!r} points outside the repository")
            continue
        bad(f"{where}: link {label!r} -> {target!r} does not exist")


def check_quiz(path: str, is_module: bool) -> None:
    stats["quiz files"] += 1
    try:
        entries = yaml.safe_load(open(path, encoding="utf-8"))
    except yaml.YAMLError as e:
        bad(f"{path}: YAML parse error: {str(e).splitlines()[0]}")
        return
    if not isinstance(entries, list) or not entries:
        bad(f"{path}: not a non-empty list")
        return
    lo, hi = (8, 10) if is_module else (3, 5)
    if not (lo <= len(entries) <= hi):
        bad(f"{path}: {len(entries)} questions, expected {lo}-{hi}")
    ids: set[str] = set()
    dist = collections.Counter()
    for i, e in enumerate(entries, 1):
        tag = f"{path}: q{i}"
        if not isinstance(e, dict):
            bad(f"{tag}: not a mapping")
            continue
        if e.get("id") in ids:
            bad(f"{tag}: duplicate id {e.get('id')!r}")
        ids.add(e.get("id"))
        opts = e.get("options")
        if not isinstance(opts, list) or len(opts) != 4 or not all(
            isinstance(o, str) and o.strip() for o in opts
        ):
            bad(f"{tag}: options must be 4 non-empty strings")
            continue
        if len({o.strip().lower() for o in opts}) != 4:
            bad(f"{tag}: options are not distinct")
        c = e.get("correct")
        if not isinstance(c, int) or not 0 <= c <= 3:
            bad(f"{tag}: correct must be 0-3")
            continue
        dist[c] += 1
        if not isinstance(e.get("explanation"), str) or not e["explanation"].strip():
            bad(f"{tag}: missing explanation")
        for o in opts:
            if ALL_NONE.search(o):
                bad(f"{tag}: 'all/none of the above' option")
        lens = [len(o.strip()) for o in opts]
        longest_wrong = max(lens[k] for k in range(4) if k != c)
        if lens[c] > longest_wrong * 1.5 and lens[c] - longest_wrong > 30:
            bad(f"{tag}: correct option much longer than the wrong ones")
    QUIZ_DIST.update(dist)


QUIZ_DIST: collections.Counter = collections.Counter()


def main() -> int:
    titles = sidebar_titles()
    lessons = sorted(glob.glob("lessons/module-*/lesson-*.md"))
    module_quizzes = sorted(glob.glob("assessments/module-*-quiz.md"))

    for path in lessons:
        text = open(path, encoding="utf-8").read()
        data, body, err = split_front_matter(text)
        if err:
            bad(f"{path}: {err}")
            continue
        for key in REQUIRED_FM:
            if key not in data:
                bad(f"{path}: front-matter has no {key}")
        stats["lessons"] += 1

        plain = strip_code(body)
        h1s = re.findall(r"^# .+$", plain, re.M)
        if len(h1s) != 1:
            bad(f"{path}: {len(h1s)} H1 headings, expected 1")
        else:
            want = f"# {data.get('id')} · "
            if not h1s[0].startswith(want):
                bad(f"{path}: H1 {h1s[0]!r} does not start with {want!r}")
            link_title = titles.get(path.replace("\\", "/"), "")
            if link_title:
                stripped = re.sub(r"^\d+\s*[·-]\s*", "", link_title.replace("**", ""))
                if not h1s[0].endswith(stripped):
                    bad(f"{path}: H1 {h1s[0]!r} does not end with sidebar title {stripped!r}")

        found = [h.strip() for h in re.findall(r"^## (.+)$", plain, re.M)]
        if found != SECTIONS:
            missing = [s for s in SECTIONS if s not in found]
            extra = [s for s in found if s not in SECTIONS]
            bad(f"{path}: section list wrong (missing={missing} extra={extra} order_ok={found == SECTIONS})")

        after = plain.strip().split("\n", 1)[1].strip() if "\n" in plain.strip() else ""
        first = after.split("\n\n")[0].strip()
        if not first or first.startswith(("#", "*", "_", "<", ">", "|", "-")):
            bad(f"{path}: the paragraph after the H1 is not plain text (found {first[:40]!r})")

        if BAD_HTML.search(plain):
            bad(f"{path}: disallowed raw HTML")
        if QUIZ_HEADING.search(plain):
            bad(f"{path}: a Knowledge check / Quiz / Assessment / Answers heading is in the markdown")
        if PROGRESS_CMD.search(body):
            bad(f"{path}: calls a progress tool")
        check_links(body, path, path)

        qp = path.replace(".md", ".quiz.yaml")
        if os.path.exists(qp):
            check_quiz(qp, False)
        else:
            bad(f"{path}: no .quiz.yaml")

    for path in module_quizzes:
        text = open(path, encoding="utf-8").read()
        _, body, _ = split_front_matter(text)
        plain = strip_code(body)
        if len(re.findall(r"^# .+$", plain, re.M)) != 1:
            bad(f"{path}: expected exactly one H1")
        if QUIZ_HEADING.search(plain):
            bad(f"{path}: quiz/answers heading in a quiz page")
        if BAD_HTML.search(plain):
            bad(f"{path}: disallowed raw HTML")
        check_links(body, path, path)
        stats["module quizzes"] += 1
        qp = path.replace(".md", ".quiz.yaml")
        if os.path.exists(qp):
            check_quiz(qp, True)
        else:
            bad(f"{path}: no .quiz.yaml")

    total = sum(QUIZ_DIST.values())
    print(f"lessons {stats['lessons']} · module quizzes {stats['module quizzes']} · "
          f"quiz files {stats['quiz files']} · questions {total}")
    if total:
        shares = {k: f"{QUIZ_DIST[k] * 100 / total:.1f}%" for k in range(4)}
        line = "  A-D " + "/".join(str(QUIZ_DIST[k]) for k in range(4)) + "  (" + ", ".join(
            f"{k}: {shares[k]}" for k in range(4)) + ")"
        if any(QUIZ_DIST[k] / total < 0.15 or QUIZ_DIST[k] / total > 0.35 for k in range(4)):
            bad(f"correct-answer positions not spread: {line}")
        print(line)

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nno problems found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())