# Capstone write-up

One page. It is not a report of what you did; it is a defence of every choice you made, using your
own numbers. A reviewer should be able to disagree with a decision only if you can show the
measurement that drove it.

**Name:** ____________________
**Machine:** ____________________ (CPU, RAM total, RAM speed, number of sticks, storage)
**Tier:** ____
**Date:** ____________________

## 1. What you built

Three or four sentences: which services run, on what hardware, and what a person in your house can
actually do with it.

______________________________________________________________________

## 2. Sizing: prediction versus measurement

| Model | Size (GB) | Predicted gen tok/s | Measured gen tok/s | Gap | Explanation of the gap |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

Total RAM with the full stack loaded: ______ GB on a machine with ______ GB.

**What you would change if you had to cut memory in half:** ____________________

## 3. Model choices

| Job | Model | Why | Measured speed | Eval score |
|---|---|---|---|---|
| Chat | | | | |
| Tool calling | | | | |
| Embeddings | | | | |

**The eval set you built:** how many tasks, how you scored them, and the single question on it that
your first choice failed and your final choice passed.

______________________________________________________________________

## 4. Voice

| Stage | Measured (s) | Budget (s) |
|---|---|---|
| End of speech → speech-to-text | | |
| Intent match or LLM | | |
| Text-to-speech to first audio | | |
| **Total, built-in intents** | | **≤ 2.0** |
| **Total, LLM fallback** | | **≤ 5.0** |

Entities controlled: ______ (list them). Misfire rate on your 30-command set: ______ %.

**Did you use the microphone, the typed route, or both, and why:** ____________________

## 5. Guardrails

- Entities deliberately **not** exposed: ____________________
- Actions that require confirmation, and how you built that in: ____________________
- One tool call you read in the logs that you would rather it had not made: ____________________

## 6. Security

- Remote access method: ____________________
- How you verified nothing is reachable from the internet: ____________________
- Last successful restore drill: ____________________
- Update routine, and the date it is next due: ____________________

**One risk you accepted, and why:** ____________________

## 7. No cloud

How you blocked outbound traffic, and what broke (if anything): ____________________

## 8. Reproducing it

The exact steps someone else needs, starting from a clean machine, to get your stack running:

1. ____________________
2. ____________________
3. ____________________

**Anything that is not in git, and why:** ____________________
