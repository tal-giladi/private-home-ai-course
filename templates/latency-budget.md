# Latency budget

A voice assistant is judged on one number: how long between you finishing your sentence and hearing
a reply. This is the sheet for breaking that number into stages and deciding which stage to attack.

**Machine:** ____________________________________
**Date:** ____________________________________

## The budget

| Stage | Budget | Typical source of overrun |
|---|---|---|
| End-of-speech detection | 0.3–0.5 s | Silence threshold too high; VAD waiting for a full frame |
| Speech-to-text | ≤ 1.0 s | Model too large (`small` instead of `base`); long audio buffer |
| Built-in intent match | ≤ 0.1 s | Rarely the problem; a large model used here instead |
| LLM with tools | ≤ 3.0 s | Model too big; long system prompt; too many exposed entities |
| Text-to-speech to first audio | ≤ 0.5 s | Synthesising the whole sentence before starting to play |

**Targets:** ≤ 2 s from the end of speech to the first sound for a built-in intent; ≤ 5 s when the
LLM has to answer. These are course goals, not guarantees — measure and write what you actually get.

## Measured

| Run | Mode (intents / LLM / hybrid) | STT | Intent or LLM | TTS | End of speech → first audio | Within target? |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

**Median across the five runs:** ______ s
**Worst run:** ______ s
**What the distribution looks like:** consistent / one clear slow path / noisy

## The 95th-percentile question

Voice feels bad when it is *sometimes* slow, not when it is uniformly slow. Run the same command ten
times and note how many exceed the budget.

| Command | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Over budget |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |
| | | | | | | | | | | | |

**How many runs exceeded the budget:** ______ / 10

## Tuning log

Change one thing at a time and re-measure. Write down what changed and what it bought you.

| Change | Before | After | Kept it? |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

**Rules that worked for this machine:**

1. ____________________
2. ____________________
3. ____________________

**Rules that did not work here (and why):** ____________________
