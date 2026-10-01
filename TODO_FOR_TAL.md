# TODO_FOR_TAL — Private Home AI: A CPU-only Home Lab

Everything here needs a decision or an action from you. Nothing here blocks the import: the course
is written so that it imports cleanly without any of it. Each item says what it affects.

**Repo:** `private-home-ai` (this folder) · **Planned GitHub repo:** `tal-giladi/private-home-ai-course`
· **Slug:** `private-home-ai` · **Free or paid:** free (your call) · **Status:** ready to import
pending the phase-1 spike below.

Full registration details: [`curriculum/course-details.md`](curriculum/course-details.md).

---

## 1. Before this course can be taught end to end: the phase-1 spike

The course plan ([`plan.md`](plan.md) §12, decision 12) says the spike comes first. It has not been
run, and that shapes what the lessons are allowed to claim. **No lesson presents an invented
measurement** — every number is cited with a URL and the machine it came from, or it is presented
as something the learner measures. That is defensible but it is not the finished article.

Run on your Windows laptop (Core Ultra 7 255H, 32 GB DDR5-5600):

- [ ] `py -3 labs/common/homelab.py doctor` — record the tier, and whether memory is dual channel.
      The plan (§12 Q11) says this is unconfirmed, and one answer decides whether the bandwidth
      numbers in Module 2 need revising.
- [ ] `py -3 labs/common/homelab.py bench` on `qwen3:4b`, `llama3.2:3b` and `qwen2.5:7b` — these
      become the tier B figures in `references/benchmarks.md` and in `references/models.md`.
- [ ] The same models capped at 16 GB (WSL2 `memory=16GB` in `.wslconfig`, or a Docker memory
      limit) — this is what tells us whether the tier A defaults in `.env.example` are right.
- [ ] `py -3 labs/common/homelab.py bench --voice` on the sample WAVs — fills the speech-to-text and
      text-to-speech columns for the tier B row of the latency budget.
- [ ] `docker compose --profile voice up -d` and fill in the Module 8.4 latency table for real.
- [ ] Sign off the **default model list**. `references/models.md` says so explicitly and currently
      marks the list provisional.

Once those numbers exist, the honest thing is a pass over the lessons replacing "cited" figures with
"measured by us" ones, naming the machine. That is the biggest remaining piece of work on this repo.

## 2. Things that were flagged as unverified at build time

- [ ] **Verify the `rhasspy/wyoming-*` image tags** in `references/versions.md`. They are the only
      pinned versions not read from a registry; everything else was confirmed on 2026-09-30
      (Ollama 0.35.0, Open WebUI v0.11.4, Home Assistant 2026.9.4, Qdrant v1.19.1).
- [ ] **Re-check every external link.** The linter does not fetch URLs. One link was already found
      and fixed during the build: `home-assistant.io/docs/backup/` is a 404; the live pages are
      `common-tasks/general/#backups` and `common-tasks/os/`. Assume others exist somewhere.
- [ ] **macOS is marked "not verified by us"** throughout, per plan §12 Q11 — one Windows test
      machine. Either find a tester or decide that is permanent.
- [ ] **Module 12.4 describes HA OS migration and Module 12.2 describes backups.** Neither has been
      executed end to end. They are written carefully and clearly labelled, but they are untested
      instructions for a path learners will follow literally.

## 3. Decisions only you can make

- [ ] **Free or paid.** The course is written to be free and public. `plan.md` targets a public
      course. If it goes behind a paywall, simulations are still public by the import contract, so
      `simulations/sizing/` must stay public and nothing paid may live inside it.
- [ ] **The default model list**, after the spike. This is the capstone's "model choice" criterion,
      so the list the course teaches and the list it expects learners to defend must be the same
      one.
- [ ] **A Hebrew version**, later. Nothing in the repo blocks it: `LANG_TAG` in `.env` picks the
      language for Whisper, Piper, Home Assistant and the sample folder, and the samples are
      already under `samples/en/` so a `he/` folder is additive. The blocker is the importer, which
      is English-only today — noted in the plan §8.4 and not solved here.
- [ ] **Hebrew viability.** The plan lists this as a phase-1 question: Whisper accuracy on Hebrew
      commands, available Piper Hebrew voices, Assist intents in Hebrew, and how a small model
      handles Hebrew tool calls. That result goes in `references/` and decides what the Hebrew
      version can promise. It is not answered yet.

## 4. Quality notes worth your attention

- [ ] **Length.** Modules 11 and 12 run long — roughly 1 700–2 200 prose words per lesson against
      the 900–1 500 the build guide targeted. Dense rather than padded, but if you want a
      tightening pass, those two modules are where it would go.
- [ ] **`tools/` is build tooling, not course content.** `lint_course.py`, `fix_quiz_yaml.py` and
      `balance_quiz.py` exist because this repo has real YAML traps in it (a plain scalar cannot
      start with a backtick; `": "` inside a sequence entry turns it into a mapping). They are
      harmless to learners and are not imported, but they are committed. Say the word and they move
      to a branch or a `.gitignore`d folder.
- [ ] **`balance_quiz.py` must be re-run after any lesson is added.** It normalises the correct
      answer position across every quiz file by position in the course order, so adding files at the
      end shifts the rotation. The import check will fail loudly (the checker requires each of
      A–D to be 15–35% of all questions) if you forget.

## 5. Registry work, if you want it

- [ ] Create `tal-giladi/private-home-ai-course` (public) and push.
- [ ] Then, from `C:/Users/TalGiladi/OneDrive/repos/tals-academy`:
      `npm run check-course -- ../course-creator/private-home-ai` should report `0 problems`.
      It does at the commit this file was written into.
- [ ] Register the course from `curriculum/course-details.md`, then import and publish.

---

## Things that are deliberately not here

- **No `PUBLISHING_WARNING.md` is needed.** The course contains no content that could be used to
  harm people, and the exposure lab in Module 11 runs entirely inside an isolated local Docker
  network with no third-party target, no scanning and no internet access.
- **No progress tracker.** The Academy tracks progress itself; no lesson calls a tracking command.
- **No purchased-hardware requirement.** Lessons 03.1 and 09.3 mention optional hardware and no lab
  or capstone criterion depends on it.