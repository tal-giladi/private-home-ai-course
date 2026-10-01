---
id: "10.4"
module: 10
minutes: 11
practice_minutes: 35
prerequisites: ["10.3", "06.3"]
objectives:
  - >-
    Answer a spoken question over your own files, and measure the time before the first word.
  - >-
    Explain why this is the most expensive thing the voice path can do, and what to shorten first.
  - Decide whether to keep the feature, having measured it.
volatility: implementation
sources:
  - title: "Home Assistant — Ollama integration"
    url: https://www.home-assistant.io/integrations/ollama/
  - title: "Open WebUI documentation"
    url: https://docs.openwebui.com
last_verified: "2026-09-30"
---

# 10.4 · Answer from your own files by voice

The capstone of the voice path, and the most expensive thing in it. Speaking is fast, transcription
is fast, and then a two-thousand-token retrieved prompt goes through a model that processes prompts
slowly on a CPU — and the whole thing has to finish before the first sound of the answer.

**This lesson needs Module 6.** If you skipped retrieval, skip this one. You lose lesson 10.4 and
one capstone criterion, and nothing else in the course depends on it.

## Why it matters

It is the feature people most want and most often turn off. "What's the warranty on the
dishwasher?" spoken in a kitchen is exactly the kind of question an assistant should answer, and it
is also the one that takes longest on a CPU.

The reason is structural rather than fixable: retrieval needs context, context needs prompt
processing, and prompt processing is the slowest thing in the pipeline on this hardware. The
lesson is not "make it fast" — that is not always possible — it is "know what it costs, shorten what
you can, and decide honestly whether to keep it".

## How it works

### Where the time goes

| Step | Typical cost on a CPU | Can you shorten it? |
|---|---|---|
| Speech-to-text | ~1 s | marginally, with a smaller model |
| Embedding the question | tens of milliseconds | no, it is already small |
| Vector search | milliseconds | no |
| **Prompt processing** | **seconds, and it scales with retrieved tokens** | **yes — this is the lever** |
| Generation | seconds, at generation speed | yes, with a smaller model |
| Text-to-speech | ~0.5 s | marginally |

Only one of those is really adjustable, and it is the one that everyone forgets is adjustable. A
retrieval system that returns ten chunks twice over will double your wait; one that returns four
relevant chunks will halve it.

### The phrase that kills it

Three words decide whether this feature feels good: **"read that back".** Spoken, you get a fast
intent-free path. Asking a model to read retrieved text aloud puts two thousand prompt tokens in
front of a three-second target, and the result is usually a wait long enough that people stop
asking.

## Show me

The shape of the timing, using your own Module 8 numbers rather than anyone else's:

| | Typed question | Spoken question over files |
|---|---|---|
| Wake word + end-of-speech | n/a | 0.3–0.5 s |
| Speech-to-text | n/a | ~1 s |
| Retrieval | ~0.1 s | ~0.1 s |
| Prompt processing | hidden in the wait | **the dominant cost** |
| Generation | seen as typing speed | slower to read aloud |
| Text-to-speech | n/a | ~0.5 s |
| **Total before the first sound** | n/a | **often several seconds** |

The lesson in that table is the asymmetry: as text, the wait is the least interesting thing about
the feature; as speech, it is the only thing about it.

## Try it

1. Wire it up. With Module 6's knowledge base connected to the chat interface, the simplest path
   for voice is to make the chat interface's model endpoint reachable from Home Assistant's
   conversation agent — which is a configuration question, not a code question. Read the current
   documentation linked below, because the exact setting names move.

2. Ask the same question three ways and time each from the end of your sentence:

   ```text
   "When does the washing machine warranty end?"   typed   →  __ s
   "When does the washing machine warranty end?"   spoken  →  __ s
   "turn on the kitchen light"                     spoken  →  __ s   (for comparison)
   ```

   The third line is the control. It is what a fast voice command costs, and the gap between it and
   the first is the price of retrieval.

3. Shorten the prompt and measure again. In order of preference:

   ```dotenv
   RAG_TOP_K=3        # fewer chunks, a shorter prompt
   ```

   ```yaml
   # and in the assistant configuration, a smaller conversation model
   ```

   One change at a time, and write down what it bought. If halving the chunks saves a second, that
   is a real number and the right trade is four chunks, not ten.

4. Try a question that needs only one document, and one that needs three. The second will be slower
   and worse, and knowing which of your real questions fall into which bucket is the useful output.

5. Decide, honestly, in one sentence:

   ```text
   Knowledge questions by voice: 4.1 s to first audio. Usable for one-off questions,
   not for conversation. Keeping it, with RAG_TOP_K at 4.
   ```

   "Not usable for conversation, keeping it for one-offs" is a perfectly good outcome and it is the
   answer most people arrive at.

## Break it

**Break it by raising `RAG_TOP_K` to twenty.** Everything works and everything takes forever. The
user has no idea why, because the only symptom is slowness.

**Break it by using an 8B model for questions.** The answer is better and the wait is worse, and in
voice the wait is what the user is judging.

**Break it by measuring with a fast command.** Comparing a knowledge question against "turn on the
light" gives a number that means nothing.

**Break it by asking it to read the whole document back.** A model asked to summarise at length
generates for a long time, and by then the user has forgotten what they asked.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Too slow to use | Too many retrieved chunks | Lower `RAG_TOP_K` to 3–4 |
| Correct but vague | Chunks truncated | Shorter documents, or a larger chunk size |
| Long wait, good answer | Model too big for a spoken answer | A smaller conversation model for the voice path |
| Answers from its own memory | Knowledge base not attached | Attach it |
| Fine for one document, bad for several | Each document needs its own chunks | Ask narrower questions, or accept it |
| Works typed, unusable spoken | Prompt processing dominates | Same fix: fewer chunks, smaller model |

## How do I know it works?

- [ ] You have three timings on your own machine: typed knowledge, spoken knowledge, spoken command.
- [ ] You know which part of the wait is prompt processing, by having halved the chunks and
      re-measured.
- [ ] Your `RAG_TOP_K` is chosen from a measurement rather than from the default.
- [ ] You have written one honest sentence about whether you keep the feature.
- [ ] You can still complete every voice lab without this feature.

## Use it when / avoid it

**Use it for one-off questions.** "When does the warranty end?" is a good fit: you ask once, you
wait once, you get a cited answer.

**Do not use it for conversation.** The latency budget from lesson 08.4 was built for commands, and
a knowledge question does not fit inside it on most CPUs.

**Shorten the prompt before you change the model.** `RAG_TOP_K` is free; a bigger model is RAM and
time.

**Keep it off the fast path.** Nothing in this lesson should be in the path of "turn on the light".

> [!NOTE]
> If you skipped Module 6, this lesson is the only thing you have missed, and skipping it is a
> legitimate choice. The capstone rubric marks this criterion as applying only if Module 6 was
> taken.

## Reflect

1. What is the gap between your spoken knowledge question and your spoken command, in seconds?
2. Which single change bought you the most time, and would you make that change permanently?
3. Would you keep this feature? What sentence would you write in the capstone write-up?

## Sources

- [Home Assistant — Ollama integration](https://www.home-assistant.io/integrations/ollama/)
- [Open WebUI documentation](https://docs.openwebui.com)
- [Latency budget template](../../templates/latency-budget.md)
- [22 · Is the answer right?](../module-06/lesson-03.md)
- [29 · Measure the voice pipeline](../module-08/lesson-04.md)