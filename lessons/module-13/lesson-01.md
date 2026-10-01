---
id: "13.1"
module: 13
minutes: 20
practice_minutes: 180
prerequisites: ["12.4", "10.3", "09.2"]
objectives:
  - >-
    Build one private home AI stack on your own hardware and defend every choice with your own
    measurements.
  - Complete each rubric criterion with evidence rather than assertion.
  - Write the one-page write-up that makes the design decisions reviewable by someone else.
volatility: concept
sources:
  - title: "Home Assistant — remote access and why a port is not it"
    url: https://www.home-assistant.io/docs/configuration/remote/
  - title: "Benchmark numbers and where they come from"
    url: https://github.com/geerlingguy/ai-benchmarks
last_verified: "2026-09-30"
---

# 13.1 · Build your own private home AI stack

This is the whole course in one artefact. You already have the stack; this is the day you make it
*yours* — your hardware, your folder, your entities, your numbers — and then write one page
defending every choice with those numbers.

## Why it matters

Everything in this course has been a decision you were handed, or one you made on a machine you
borrowed for the purpose. The capstone is the step that turns it into a system you live with, and
the write-up is what stops it decaying into something you cannot explain six months later.

The rubric is deliberately unfriendly to hand-waving. Every criterion asks for a measurement, a list
or a completed procedure. "My stack is private" is not an answer; "here is how I verified nothing is
reachable from outside, and here is the method" is.

## How it works

### The deliverable

One working stack on your own hardware, meeting nine criteria, plus a one-page write-up. The rubric
is [linked below](../../assessments/capstone-rubric.md) and the write-up template is
[templates/capstone-write-up.md](../../templates/capstone-write-up.md).

The criteria, briefly:

| Criterion | What "meets the bar" means |
|---|---|
| **Sizing** | Prediction and measurement for your models, with the gap explained |
| **Model choice** | An eval set of ≥ 20 tasks; a justified model per job with scores |
| **Private files** | *(only if Module 6)* A real folder, 10 labelled questions, a grounded-answer rate, and deletion that works |
| **Voice pipeline** | Wake word or typed route → STT → intents/LLM → TTS, per-stage latencies, misfire rate on 30 commands |
| **Guardrails** | A written exposed-entity list with reasons; confirmation for risky actions; tool calls read |
| **Security** | Nothing reachable from the internet, checked from outside; VPN-only remote access; versions pinned; an update routine written |
| **Operations** | A backup **and a completed restore drill**; idle power and RAM measured |
| **No cloud** | The outbound-blocked test passes with every feature you use still working |
| **Reproducibility** | One `docker compose up` plus a documented native step rebuilds it from the repo and `.env.example` |

### The three that catch people out

Not the hard ones — the ones that get forgotten.

- **A restore drill that was never run.** A backup you have not restored is a hypothesis. Pick a
  weekend, wipe something on purpose, and put it back.
- **Checking exposure from outside.** Checking from your own network proves nothing, because from
  inside everything looks reachable. Turn off the VPN and check from a phone on mobile data, or ask
  somebody else to look.
- **A write-up that cites numbers.** If a decision in your write-up has no number next to it, either
  measure it or remove the claim.

## Show me

The order that works, and roughly what each step costs in time:

| Step | Time | Rubric criteria it satisfies |
|---|---|---|
| Decide hardware and models from your measure-yours table | 1 h | Sizing, Model choice |
| Build the eval set and score your candidates | 2 h | Model choice |
| Point it at a folder of your own, and evaluate | 2 h | Private files |
| Voice: measure the pipeline, run the 30 commands | 2 h | Voice pipeline |
| Write the exposure list, add confirmations, read tool calls | 1 h | Guardrails |
| Security: pin versions, check from outside, write the routine | 1 h | Security |
| Backup **and restore drill** | 2 h | Operations |
| Block outbound traffic and confirm everything still works | 1 h | No cloud |
| Rebuild from a clean directory and write the steps down | 1 h | Reproducibility |
| The write-up | 1 h | all of them |

About fourteen hours. It is more than a weekend and less than a week, and the ordering matters: the
expensive criteria are in the middle so you do not discover at hour thirteen that your machine is too
slow for the voice path.

## Try it

1. **Fill in your measure-yours tables first.** Every later decision cites them. A capstone defended
   by numbers starts with numbers you already have.

2. **Write your final configuration, then explain it.** One line per choice, with the number:

   ```text
   Chat model:   qwen3:4b        7.1 tok/s, 16 passes of 20 on my eval set
   Tool model:   qwen3:4b        same model - one slot avoids a swap (lesson 04.2)
   Speech:       Whisper base     0.18 real-time factor; small missed my accent
   Voice:        Piper lessac     0.4 s to first audio; household preferred amy
   Context:      4096             enough for chat, halves the KV cache vs 8192
   ```

3. **Run the thirty-command set three times** — intents, model, hybrid — and record four columns
   each. This is your misfire rate and it is a capstone criterion, not a formality.

4. **Verify exposure from outside.** Turn the VPN off, put a phone on mobile data, and try to reach
   every published port. Then try to reach them from the guest network. Record the method, not just
   the result — a criterion without a method is an assertion.

5. **Do the restore drill.** Back up, delete something, restore, verify. Write down what was
   awkward, because that is the part of the procedure that was untested.

6. **Prove no cloud.** Block outbound traffic from the stack and use every feature you rely on. If
   something breaks, that is the finding, and it belongs in the write-up.

7. **Rebuild from clean.** A fresh directory, `compose.yaml` from the repo, `.env` from
   `.env.example`, one documented native step if you use one. If you cannot rebuild it, criterion
   nine is not met and the fix is the rebuild.

8. **Write the page.** One page, eight numbered sections, using the template. Every claim carries a
   number or a procedure. Then read it as someone who knows nothing about your house: can you follow
   the argument?

## Break it

**Break it by skipping the write-up.** Everything works and nobody can tell why. Six months later a
model update changes the speeds, and there is no record of what they were.

**Break it by copying the course's defaults.** The rubric asks for *your* eval set on *your* tasks.
Twenty prompts you wrote from memory are the deliverable; twenty you copied are not, and they will
not tell you anything about your household.

**Break it by exposing everything to the model** to make one criterion easier. The misfire number
gets worse and the guardrails criterion fails, which is the correct outcome.

**Break it by checking exposure only from the house LAN.** From inside, every port looks reachable
and the check passes. This is the single most common way a "verified secure" capstone is not.

**Break it by running the restore drill last, in a hurry.** It is the criterion that most often
fails, and it fails because it was deferred rather than because it is impossible.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| A criterion has no number behind it | Not measured | Measure it, or remove the claim |
| The voice criterion is not met on your machine | Model too big, or chunks too many | Smaller speech model; intents first; report honestly |
| Security cannot be evidenced | Only checked from the LAN | Check from mobile data or ask someone outside |
| Restore drill failed | Models or paths assumed | Fix the procedure and run it again; write down what broke |
| Rebuild from clean fails | Something was configured by hand | Every hand step becomes a documented step in the write-up |
| Private files criterion cannot be met | Module 6 was skipped | It is marked as not applicable — say so, do not fake it |

The last row matters: the rubric marks the private-files criterion as applying only if Module 6 was
taken. "I skipped Module 6 and here is everything else" is a complete and honest capstone.

## How do I know it works?

- [ ] Every one of the nine criteria has evidence: a number, a list, or a completed procedure.
- [ ] Your measure-yours tables are filled in and cited by the write-up.
- [ ] The 30-command set has been run in three modes with four columns recorded.
- [ ] A restore drill was completed, and you know what was awkward about it.
- [ ] Exposure was verified from outside your network, and the method is written down.
- [ ] The stack rebuilds from a clean directory using only the repo and `.env.example`.
- [ ] Someone who knows nothing about your house can follow the write-up.

## Use it when / avoid it

**Do this on your own hardware.** The rubric is about your machine, your folder and your household.

**Do it in the order above.** The expensive criteria sit in the middle so a slow machine is
discovered early, when there is still time to choose a smaller model.

**Keep the write-up.** It is the only artefact that makes the next year cheaper.

**Do not buy hardware to pass a criterion.** Every rubric item is achievable on what you own; the
optional hardware in lesson 09.3 is a convenience, not a requirement.

> [!TIP]
> Do the write-up even if you never publish anything. The version in this repo is the one you will
> consult when a model update halves your speed and you need to know what was fast last time.

## Reflect

1. Which criterion took longest, and was that the one you expected to?
2. Which of your original design choices would you now make differently, and what number changed
   your mind?
3. What would you tell someone starting this course today, given what your own build taught you?

## Sources

- [Capstone rubric](../../assessments/capstone-rubric.md)
- [Capstone write-up template](../../templates/capstone-write-up.md)
- [Measure-yours tables](../../templates/measure-yours.md)
- [Latency budget template](../../templates/latency-budget.md)
- [Security checklist](../../templates/security-checklist.md)
- [Update routine](../../templates/update-routine.md)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)