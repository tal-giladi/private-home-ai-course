---
id: "08.4"
module: 8
minutes: 13
practice_minutes: 40
prerequisites: ["08.3"]
objectives:
  - Measure each stage of the pipeline separately and fill in the latency budget for your machine.
  - >-
    State honestly whether your machine meets the two-second and five-second targets, and name
    which stage is responsible when it does not.
  - Change one stage at a time and record what it bought.
volatility: implementation
sources:
  - title: "Home Assistant — setting up a fully local voice assistant"
    url: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
  - title: "Benchmark numbers and where they come from"
    url: https://github.com/geerlingguy/ai-benchmarks
last_verified: "2026-09-30"
---

# 08.4 · Measure the voice pipeline

Every voice problem that gets hard to solve started as an unmeasured one. "It feels slow" is not a
diagnosis, and this lesson replaces it with five numbers on one page — your own, on your machine,
which may not match the targets the course proposes.

## Why it matters

The whole difference between an assistant people use and one they stop using is the gap between
finishing a sentence and hearing a reply. For chat that gap is seconds and nobody minds. For voice
it is the product.

The targets this course proposes are **≤ 2 seconds from the end of speech to the first sound of a
reply using built-in intents, and ≤ 5 seconds when a language model has to answer.** Those are
*goals*, not measurements, and the honest outcome on some machines is "the intent target is met and
the LLM target is not". That result is useful: it is the reason the default pipeline is intents
first, and it is a better answer than a promise.

## How it works

### The five stages and what each one costs

| Stage | Budget | What pushes it over |
|---|---|---|
| End-of-speech detection | 0.3–0.5 s | Silence threshold too high; a frame-sized buffer |
| Speech-to-text | ≤ 1.0 s | Model too large; a long audio buffer |
| Built-in intent match | ≤ 0.1 s | Rarely the problem — and only a problem if you use a model here |
| LLM with tools | ≤ 3.0 s | Model too big; a long system prompt; too many exposed entities |
| Text-to-speech to first audio | ≤ 0.5 s | Client buffering rather than streaming |

The single most useful observation in that table: **on a correctly configured stack, built-in
intents take under a second in total and the LLM path is the only one that can blow the budget.**
Everything else is tuning.

### Why the distribution matters more than the median

Voice feels bad when it is *sometimes* slow, not when it is uniformly slow. Run the same command
ten times and count how many exceed the budget. A pipeline with a four-second median and a
consistent distribution is worse than one with a two-second median and one eight-second outlier per
day, because the first is a product and the second is a fault.

This is also why [29's companion lesson](../module-12/lesson-01.md) sets health checks and keeps the
model loaded: an always-on system has a much longer tail than an interactive one.

### How to time it without a stopwatch

Time from a file where you can:

```bash
# Windows PowerShell
Measure-Command { docker compose --profile voice restart wyoming-whisper }

# macOS / Linux
time docker compose --profile voice restart wyoming-whisper
```

And time end to end where you cannot, using the logs. Home Assistant logs the pipeline stages when
assistant debugging is on; the timestamps between them are your five numbers.

## Show me

The template to fill in, from [templates/latency-budget.md](../../templates/latency-budget.md):

| Stage | Sample commands | Your voice | Budget | Within budget? |
|---|---|---|---|---|
| End-of-speech detection | | | 0.3–0.5 s | |
| Speech-to-text | | | 1.0 s | |
| Built-in intent match | | | 0.1 s | |
| LLM with tools | | | 3.0 s | |
| Text-to-speech to first audio | | | 0.5 s | |
| **Total, built-in intents** | | | **2.0 s** | |
| **Total, LLM fallback** | | | **5.0 s** | |

And the derived question that makes the table worth something: **where did your time actually go?**
If the answer is "the language model", the fix is a smaller model or fewer exposed entities. If it
is "speech-to-text", the fix is a smaller speech model or Speech-to-Phrase. Different stages have
different fixes, and a single end-to-end number tells you nothing.

## Try it

1. Turn on assistant debugging in Home Assistant (**Settings → Voice assistants → your assistant →
   Enable assistant debug logging**) and run five commands. Write the five stage timings per
   command into the table.

2. Separate the two paths. Run five commands that built-in intents handle, then five that need the
   model. Two totals, not one.

3. Get the distribution, not the median. Run the same command ten times:

   ```text
   turn on the kitchen light   ×10, recording end-of-speech → first audio each time
   ```

   Count how many exceeded 2 seconds. Write it in the "over budget" row of the template.

4. Find your slowest stage and change exactly one thing:

   | If the slowest stage is | Change one of | Expected effect |
   |---|---|---|
   | Speech-to-text | `STT_MODEL` down a size, or Speech-to-Phrase | Large |
   | LLM with tools | `TOOL_MODEL` down a size, or expose fewer entities | Large |
   | Text-to-speech | Stream instead of buffer | Moderate |
   | End-of-speech detection | The satellite's silence threshold | Moderate |
   | Intent match | Nothing — it is not the problem | none |

5. Re-measure. One change, one measurement, one row in the tuning log. Four changes at once tells
   you nothing about which one mattered, and you will have to do it again.

6. Write the conclusion honestly, in one sentence, in your measure-yours table:

   ```text
   Built-in intents: 1.2 s — meets the 2 s target.
   LLM fallback: 6.8 s — does not meet the 5 s target; the model is the cause, not the pipeline.
   ```

   The second line is a completely acceptable result. It is what Module 10's "intents first, LLM
   as fallback" design is for.

## Break it

**Break it by measuring only the happy path.** Five good runs in a quiet room and the pipeline looks
excellent. Then someone speaks from the other side of the house and the numbers double, and there is
no explanation because the tail was never recorded.

**Break it with the LLM in the loop for a light.** Every "turn on the kitchen light" takes three
seconds through a model that a fixed intent handles in a hundred milliseconds. It works, and it is
much worse than not working.

**Break it by averaging the two paths.** One number for a pipeline that has a fast path and a slow
path describes neither. Report both, separately, forever.

**Break it by trusting the target.** A machine that misses the two-second budget still works, and
the fix is usually a smaller speech model rather than a redesign. Treating the target as a pass or
a fail leads to doing something dramatic when something small would do.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Always slow, evenly | A stage is genuinely slow | Find it in the table; the fix is stage-specific |
| Fast most of the time, slow sometimes | A cold model, or thermal throttling | Longer `keep-alive`; check for throttling |
| Slow only when the chat UI is busy | Two requests sharing one bandwidth | Module 04's concurrency lesson |
| First word late, rest fine | Client buffering | Stream the reply |
| Cuts you off mid-sentence | End-of-speech threshold too eager | Raise the silence threshold on the satellite |
| Nothing at all | A stage is not running | Check each container, then the pipeline config |

## How do I know it works?

- [ ] The latency budget table is filled in with your own numbers, not the course's targets.
- [ ] You have separate totals for the intent path and the LLM path.
- [ ] You have run the same command ten times and can say how many exceeded the budget.
- [ ] You have named your slowest stage and the single change that targets it.
- [ ] You have written one honest sentence about whether you meet the targets.

## Use it when / avoid it

**Measure stages, not the pipeline.** One end-to-end number cannot tell you what to fix, and the
fix is always stage-specific.

**Report the targets as targets.** The course proposes 2 and 5 seconds. On your machine they may be
different, and stating your measured numbers is more useful than claiming you met someone else's.

**Re-measure after a software update.** Model runtimes routinely move speeds by 10–20%, and a
pipeline that quietly doubled is a pipeline you have stopped noticing.

**Do not optimise the intent path.** It is already under a hundred milliseconds. Every minute spent
there is a minute not spent on the stage that is actually slow for you.

> [!TIP]
> **Write down what you changed and what it bought.** The tuning log in
> [templates/latency-budget.md](../../templates/latency-budget.md) is three columns and takes thirty
> seconds per row. In six months it is the difference between a pipeline you understand and one you
> are afraid to touch.

## Reflect

1. Which stage is your slowest, and how does it compare with the budget for that stage?
2. Do you meet the two-second target for built-in intents? If not, which single change would you try
   first, and why that one?
3. What is the worst run in your ten, what caused it, and would your household notice?

## Sources

- [Home Assistant — setting up a fully local voice assistant](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- [Latency budget template](../../templates/latency-budget.md)
- [Measure-yours tables](../../templates/measure-yours.md)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)
- [34 · Intents first, LLM as fallback](../module-10/lesson-02.md)
- [41 · Always-on without starving the voice pipeline](../module-12/lesson-01.md)