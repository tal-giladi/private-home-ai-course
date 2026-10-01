---
id: "06.3"
module: 6
minutes: 12
practice_minutes: 40
prerequisites: ["06.2"]
objectives:
  - Score a retrieval system against labelled questions using evidence coverage, not style.
  - >-
    Separate the two failure modes — wrong chunk retrieved, right chunk wrongly summarised — by
    reading the sources.
  - Write a next step that names which of the two failed.
volatility: concept
sources:
  - title: "Qdrant documentation"
    url: https://qdrant.tech/documentation/
last_verified: "2026-09-30"
---

# 06.3 · Is the answer right?

Ten questions, a pass mark for each one, and a number at the end. This is the same discipline as
[18 · Build your own eval set](../module-05/lesson-02.md), applied to a different link in the chain,
and it exists because "it looked right" is not a measurement.

## Why it matters

A retrieval-augmented system can be wrong in two completely different ways, and the fixes are
unrelated:

- **The right answer was never retrieved.** The knowledge base does not contain it, the folder does
  not have it, or the embedding placed the relevant chunk far away. No amount of model improvement
  helps, and the sources panel will show you a passage that is clearly not the answer.
- **The right chunk was retrieved and used badly.** The sources panel shows the correct passage, and
  the answer ignores it, contradicts it, or adds something that is not in it. Now it is a prompt,
  a chunk size or a model problem.

Confusing the two is the single most common way people spend a week improving things that were
never broken. Reading the sources takes fifteen seconds and tells you which one you have.

## How it works

### Evidence coverage, in its simplest form

For each labelled question, mark two things:

| | Yes | No |
|---|---|---|
| **Evidence**: does a cited source contain the information needed to answer? | 1 | 0 |
| **Grounded**: does the answer say only what that source supports? | 1 | 0 |

Evidence coverage is the first column, and it is the one that matters most, because it is the one
you can check without judging the writing. A system with perfect evidence coverage and poor
groundedness is a prompt problem. A system with poor evidence coverage is a retrieval problem, and
no prompt will save it.

The ten labelled questions are in
[the sample folder](../../labs/common/), deliberately including the two credential questions that a
correctly scoped index must refuse.

### The scoring sheet

| # | Question | Evidence retrieved? | Answer grounded? | What failed |
|---|---|---|---|---|
| 1 | Washing machine warranty end date | | | |
| 2 | Router admin password | | | |
| … | | | | |

Two columns and one comment per row is enough. The comment is the valuable part: "retrieved the
energy bill instead of the warranty table" is a diagnosis, "wrong answer" is not.

## Show me

What the numbers mean, using an illustrative run rather than measured results — this course has not
run the evaluation on anyone's machine:

| Score | Reading | Next step |
|---|---|---|
| Evidence 10/10, grounded 9/10 | Retrieval is fine, the model is adding things | Tighten the instruction, lower the temperature |
| Evidence 7/10, grounded 7/10 | Retrieval is missing things | Wider chunks, better embedding model, or a different folder |
| Evidence 4/10, grounded 9/10 | The model is honest about a bad index | Fix retrieval first; nothing else is worth doing |
| Evidence 9/10, grounded 5/10 | The model contradicts sources it was given | The model is too small for the job, or the chunks are too long |

The bottom-right cell is the one that looks like a model problem and is usually a chunk-size
problem: a long chunk gives a small model enough context to be confidently wrong.

## Try it

1. Run all ten labelled questions from the sample folder. One row each. Do it in one sitting, at
   temperature 0, against the same index.

2. For every answer, **open the sources** and mark evidence before you mark grounded. Reading them
   in order matters: marking grounded first and then checking is how a retrieval failure gets
   recorded as a generation failure.

3. Fill in the "what failed" column in words. Sort the rows by that column afterwards. Two or three
   recurring diagnoses in ten rows is a much better use of your time than a single accuracy number.

4. Change one thing and re-run. The candidates, in the order worth trying:

   | Change | Usually fixes |
   |---|---|
   | Chunk size 300 → 500 with overlap | Evidence misses caused by a chunk boundary |
   | Chunk size 500 → 200 | Long chunks burying the answer |
   | `RAG_TOP_K` 4 → 8 | Evidence misses on questions needing two documents |
   | `RAG_TOP_K` 8 → 3 | Hallucinated detail from irrelevant chunks |
   | `bge-m3` instead of `nomic-embed-text` | Mixed-language folders |

   One change at a time. Changing three at once and improving tells you nothing about which one
   helped.

5. Write down the result as two numbers in your [measure-yours table](../../templates/measure-yours.md):
   evidence coverage out of ten, and grounded rate over the questions that had evidence. Both, not
   one. A single blended accuracy number hides which half is broken.

6. Ask the two credential questions one last time. They belong in the table, and "refused" is the
   correct result for a correctly scoped index.

## Break it

**Break it by marking grounded without looking.** Read ten answers and score them on how they read.
Fluency and correctness in a household document look almost identical, because the wrong answers
here are plausible-looking rather than obviously wrong.

**Break it by averaging.** One number over ten questions. A system that retrieves correctly for nine
and is missing the one that matters — the warranty date, the error code — scores 9/10 and tells you
nothing about which one failed.

**Break it by changing four settings and re-running once.** Everything improved. You now have no
idea which change did it, and next month the problem returns with no idea what to try.

**Break it with a stale index.** Delete a document, skip the re-ingest, and the evaluation now
credits the system for something it could not possibly know. This is the failure that makes a whole
retrieval setup look better than it is.

## Fix it

| Symptom | Diagnosis | Fix |
|---|---|---|
| Sources shown do not contain the answer | Retrieval failure | Chunk size, embedding model, or a wider folder |
| Sources contain the answer and the reply does not use it | Generation failure | Smaller chunks, a clearer instruction, a bigger model |
| Sources contain it and the reply adds detail not in them | Hallucination | Lower the temperature, fewer chunks, a bigger model |
| Two questions need one document and only one is retrieved | `RAG_TOP_K` too low | Raise it to 8, and accept the prompt cost |
| Answers correct, sources empty | Generation from memory, not from the index | Attach the knowledge base to the chat |
| Evaluation improved on every run | Something is leaking between runs | Re-index and re-run from a clean state |

The rule underneath: **every row gets a diagnosis, and the diagnosis decides the next change.** A
percentage does not.

## How do I know it works?

- [ ] You have run all ten labelled questions and recorded two columns for each.
- [ ] Every row has a written diagnosis, and the diagnoses cluster into one or two kinds.
- [ ] You changed one setting, re-ran, and can say whether it helped.
- [ ] You have two numbers written down: evidence coverage and grounded rate.
- [ ] The credential questions are recorded as refused.

## Use it when / avoid it

**Do this before you index anything private.** Ten questions take half an hour and they tell you
whether the system can do the job at all. After you index a folder of documents, you need to know.

**Re-run it when the model changes.** A new small model every month is a reason to re-measure, not
a reason to assume.

**Do not treat grounded rate as quality.** A system that refuses everything has a grounded rate of
100% and is useless. The two numbers only mean something together.

**Skip this module if you skipped Module 6.** That is a valid choice; nothing downstream depends on
it.

> [!NOTE]
> Evidence coverage is the idea this shares with `rag-course`, in its simplest possible form. That
> course does it properly — with multiple retrieval strategies, reranking, abstention and a
> statistical evaluation — and it is the right next step if a household retrieval system becomes a
> project rather than a feature.

## Reflect

1. Which of your ten questions had no evidence retrieved, and what did the sources panel show
   instead?
2. If your evidence coverage is high and your grounded rate is low, which single change would you
   make first, and why that one?
3. Which question in your own set would you care about most getting wrong, and how would you build
   a system that is safe even when it gets it wrong?

## Sources

- [Sample labelled questions](../../labs/common/)
- [Measure-yours tables](../../templates/measure-yours.md)
- [18 · Build your own eval set](../module-05/lesson-02.md)
- [06.1 · Wire a local RAG service into the stack](lesson-01.md)
- [06.2 · Which folders to index](lesson-02.md)
- [Capstone rubric](../../assessments/capstone-rubric.md)