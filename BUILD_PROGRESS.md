# BUILD_PROGRESS — Private Home AI: A CPU-only Home Lab

**Goal:** a course that imports into tals-academy on the first try with `0 problems` from
`npm run check-course`, and that a learner with a 16–32 GB CPU-only laptop can finish with no GPU,
no cloud account and no purchase.

**Binding rules:** `C:\Users\TalGiladi\OneDrive\repos\tals-academy\docs\new-course-instructions.md`
(wins over plan.md). Course shape and numbers come from `plan.md`.

## The one hard check

```bash
cd C:/Users/TalGiladi/OneDrive/repos/tals-academy && npm run check-course -- ../course-creator/private-home-ai
```

Every `warn` and `error` in the adapter log counts as a problem, so this must report `0 problems`.
Run it after every finished module, not only at the end.

## Units

- [x] Scaffolding: `BUILD_PROGRESS.md`, `.gitignore`, `curriculum/`, status logs
- [x] Root: `README.md`, `_sidebar.md`, `glossary.md`, `index.html` (docsify preview only)
- [x] `templates/` — measure-yours tables, security checklist, capstone write-up
- [x] `references/` — pinned model list with licences, pinned versions, source list, troubleshooting
- [x] `assets/` — stack map, Assist pipeline, network zones, bandwidth diagram
- [x] `labs/common/` — `homelab doctor`, `homelab bench`, `compose.yaml`, `.env.example`, samples
- [x] `simulations/sizing/` — offline RAM-bill and tokens/s calculator
- [x] Module 0 — Orientation and setup check (2 lessons + quiz)
- [x] Module 1 — Your first local model (3 lessons + quiz)
- [x] Module 2 — Sizing your machine (4 lessons + quiz)
- [x] Module 3 — Home lab foundations (4 lessons + quiz)
- [x] Module 4 — Serving and the OpenAI-compatible API (3 lessons + quiz)
- [x] Module 5 — Picking models for jobs (3 lessons + quiz)
- [x] Module 6 — Your own files, privately (3 lessons + quiz, optional)
- [x] Module 7 — Home Assistant in a box (3 lessons + quiz)
- [x] Module 8 — Speech in and out (4 lessons + quiz)
- [x] Module 9 — Wake word and satellites (3 lessons + quiz)
- [x] Module 10 — A local LLM as the voice assistant's brain (4 lessons + quiz)
- [x] Module 11 — Securing the home lab (4 lessons + quiz)
- [x] Module 12 — Running it for real (4 lessons + quiz)
- [x] Capstone brief + rubric
- [x] `TODO_FOR_TAL.md` — handoff
- [x] Final QA: `check-course` 0 problems, quiz position spread, git clean

## Lesson inventory (global running number → stable id)

| # | id | Module | File |
|---|---|---|---|
| 01 | 00.1 | 0 Orientation | `lessons/module-00/lesson-01.md` |
| 02 | 00.2 | 0 | `lessons/module-00/lesson-02.md` |
| 03 | 01.1 | 1 First local model | `lessons/module-01/lesson-01.md` |
| 04 | 01.2 | 1 | `lessons/module-01/lesson-02.md` |
| 05 | 01.3 | 1 | `lessons/module-01/lesson-03.md` |
| 06 | 02.1 | 2 Sizing your machine | `lessons/module-02/lesson-01.md` |
| 07 | 02.2 | 2 | `lessons/module-02/lesson-02.md` |
| 08 | 02.3 | 2 | `lessons/module-02/lesson-03.md` |
| 09 | 02.4 | 2 | `lessons/module-02/lesson-04.md` |
| 10 | 03.1 | 3 Home lab foundations | `lessons/module-03/lesson-01.md` |
| 11 | 03.2 | 3 | `lessons/module-03/lesson-02.md` |
| 12 | 03.3 | 3 | `lessons/module-03/lesson-03.md` |
| 13 | 03.4 | 3 | `lessons/module-03/lesson-04.md` |
| 14 | 04.1 | 4 Serving and the API | `lessons/module-04/lesson-01.md` |
| 15 | 04.2 | 4 | `lessons/module-04/lesson-02.md` |
| 16 | 04.3 | 4 | `lessons/module-04/lesson-03.md` |
| 17 | 05.1 | 5 Picking models for jobs | `lessons/module-05/lesson-01.md` |
| 18 | 05.2 | 5 | `lessons/module-05/lesson-02.md` |
| 19 | 05.3 | 5 | `lessons/module-05/lesson-03.md` |
| 20 | 06.1 | 6 Your own files (optional) | `lessons/module-06/lesson-01.md` |
| 21 | 06.2 | 6 | `lessons/module-06/lesson-02.md` |
| 22 | 06.3 | 6 | `lessons/module-06/lesson-03.md` |
| 23 | 07.1 | 7 Home Assistant in a box | `lessons/module-07/lesson-01.md` |
| 24 | 07.2 | 7 | `lessons/module-07/lesson-02.md` |
| 25 | 07.3 | 7 | `lessons/module-07/lesson-03.md` |
| 26 | 08.1 | 8 Speech in and out | `lessons/module-08/lesson-01.md` |
| 27 | 08.2 | 8 | `lessons/module-08/lesson-02.md` |
| 28 | 08.3 | 8 | `lessons/module-08/lesson-03.md` |
| 29 | 08.4 | 8 | `lessons/module-08/lesson-04.md` |
| 30 | 09.1 | 9 Wake word and satellites | `lessons/module-09/lesson-01.md` |
| 31 | 09.2 | 9 | `lessons/module-09/lesson-02.md` |
| 32 | 09.3 | 9 | `lessons/module-09/lesson-03.md` |
| 33 | 10.1 | 10 An LLM as the brain | `lessons/module-10/lesson-01.md` |
| 34 | 10.2 | 10 | `lessons/module-10/lesson-02.md` |
| 35 | 10.3 | 10 | `lessons/module-10/lesson-03.md` |
| 36 | 10.4 | 10 (optional) | `lessons/module-10/lesson-04.md` |
| 37 | 11.1 | 11 Securing the home lab | `lessons/module-11/lesson-01.md` |
| 38 | 11.2 | 11 | `lessons/module-11/lesson-02.md` |
| 39 | 11.3 | 11 | `lessons/module-11/lesson-03.md` |
| 40 | 11.4 | 11 | `lessons/module-11/lesson-04.md` |
| 41 | 12.1 | 12 Running it for real | `lessons/module-12/lesson-01.md` |
| 42 | 12.2 | 12 | `lessons/module-12/lesson-02.md` |
| 43 | 12.3 | 12 | `lessons/module-12/lesson-03.md` |
| 44 | 12.4 | 12 | `lessons/module-12/lesson-04.md` |

## Resume procedure

1. Read this file, then `curriculum/status/*.log` (one line per finished lesson).
2. Run the dry-run import; the first `PROBLEM` line is where to start.
3. Finish one lesson completely — `.md` + `.quiz.yaml` — before the next, and append
   `lesson-MM done` to `curriculum/status/module-NN.log`.
4. Commit after every module.
5. Never rewrite or renumber a finished lesson: paths are the stable ids learners' progress hangs on.

## Who is writing what

Main session owns every shared file (`_sidebar.md`, `glossary.md`, `README.md`, `references/`,
`templates/`, `labs/common/`, `assets/`, `simulations/`). Sub-agents get their own module folder
only, and hand back additions to shared files as inbox notes in `curriculum/inbox/`.

## Decisions taken while building

- **Module numbering starts at 0** (plan uses M0–M12). Folders are `module-00`…`module-12`;
  the sidebar line is `- **Module 0 — …**`, which the importer turns into key `m00`.
- **One fixed `##` section set for every lesson** (see below), per instructions §4.
- **Quiz position spread is tracked in `curriculum/quiz-balance.md`** and fixed before final QA.
- **macOS steps are marked "not verified by us"** (plan §12 Q11 — only Tal's Windows laptop is tested).

## Lesson section template (identical in all 44 lessons)

1. `## Why it matters`
2. `## How it works`
3. `## Show me`
4. `## Try it`
5. `## Break it`
6. `## Fix it`
7. `## How do I know it works?`
8. `## Use it when / avoid it` (includes "If you have a GPU" and "Do it yourself with llama.cpp" notes)
9. `## Reflect`
10. `## Sources`

## Open questions for Tal

See `TODO_FOR_TAL.md`. The plan's phase-1 spike (real `doctor`/`bench` numbers on Tal's laptop) is
**not** done; every number in a lesson is therefore either cited with a source or labelled as the
learner's own measurement to fill in. Nothing is presented as a guarantee.
