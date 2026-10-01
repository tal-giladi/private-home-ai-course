# Course outline — Private Home AI: A CPU-only Home Lab

13 modules, 44 lessons, 13 module quizzes, 1 capstone. Derived from `plan.md` §7; the lesson section
shape is fixed for the whole course (see `BUILD_PROGRESS.md`).

| Part | Module | Lessons | Path |
|---|---|---|---|
| 1 — First light | 0 Orientation and setup check | 2 | core |
| 1 | 1 Your first local model | 3 | core |
| 1 | 2 Sizing your machine | 4 | core |
| 2 — Build the stack | 3 Home lab foundations | 4 | core |
| 2 | 4 Serving and the OpenAI-compatible API | 3 | core |
| 2 | 5 Picking models for jobs | 3 | core |
| 2 | 6 Your own files, privately | 3 | core, optional |
| 3 — Voice and Home Assistant | 7 Home Assistant in a box | 3 | voice |
| 3 | 8 Speech in and out | 4 | voice |
| 3 | 9 Wake word and satellites | 3 | voice |
| 3 | 10 A local LLM as the voice assistant's brain | 4 | voice (10.4 needs M6) |
| 4 — Safe and always-on | 11 Securing the home lab | 4 | safe |
| 4 | 12 Running it for real | 4 | safe |
| 5 — Capstone | Capstone brief and rubric | — | all |

## Lesson map (global running number → id → file)

Numbers 01–44 as in `BUILD_PROGRESS.md`. Stable ids are `MM.L` and are frozen: never renumber.

## Section template (all lessons)

`## Why it matters` · `## How it works` · `## Show me` · `## Try it` · `## Break it` · `## Fix it` ·
`## How do I know it works?` · `## Use it when / avoid it` · `## Reflect` · `## Sources`

## Standing content rules

- Every number is either **cited with a URL** (name the machine it was measured on) or labelled
  **to measure on your machine**. Never a bare promise.
- Every lab works on Windows (PowerShell) and Linux; macOS commands appear where they differ and are
  marked "not verified by us".
- No service is published on `0.0.0.0` before M11, and M11 says why.
- Every voice lab has a text-only route: typed Assist or WAV file, never a microphone requirement.
- Language-sensitive parts (voice commands, sample file names, HA custom sentences) sit in marked
  blocks so a Hebrew version can swap them, not rewrite the lesson.
- Labs that can hurt (M11 exposure lab, router/firewall changes, secrets) open with
  `> [!CAUTION]` or `> [!WARNING]`.
