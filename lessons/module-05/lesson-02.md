---
id: "05.2"
module: 5
minutes: 14
practice_minutes: 50
prerequisites: ["05.1"]
objectives:
  - Build an eval set of at least 20 real tasks from your own use of the stack.
  - Score several candidate models side by side on the same set, and read the result honestly.
  - Explain why a leaderboard tells you nothing about which model suits your household.
volatility: concept
sources:
  - title: "Benchmark numbers and where they come from"
    url: https://github.com/geerlingguy/ai-benchmarks
  - title: "Measure-yours tables"
    url: https://github.com/ggml-org/llama.cpp
last_verified: "2026-09-30"
---

# 05.2 · Build your own eval set

Every model has a score somewhere. Those scores are measured on somebody else's tasks, with
somebody else's definition of "good", on hardware nobody in your house has. This lesson replaces
them: twenty of your own tasks, scored side by side, which is the only comparison that means
anything for a model that will live in your kitchen.

## Why it matters

Benchmarks fail you in a specific way: they measure the average, and a home assistant is not an
average user. A model can be excellent on the benchmark and useless for the two things you actually
ask it — reading the same kind of document all the time, and turning a misheard sentence into the
right tool call. Nobody has ever published a benchmark for your household.

The alternative is cheap. Twenty tasks, written once, takes an hour. Run it against three models in
twenty minutes. And unlike a leaderboard, the result is defensible: it is your data, on your
machine, for your work.

## How it works

An eval set here is four things per task, and the fourth is what makes it work.

| Field | Why it exists |
|---|---|
| The prompt, exactly as you would type or say it | Otherwise you test a phrasing nobody uses |
| The expected answer, or a clear statement of what must be true | Otherwise you are grading on taste |
| A pass condition you can check without re-reading it | Otherwise scoring is subjective and slow |
| **A reason this task is in the set** | Otherwise you will delete the hard ones and flatter yourself |

That last field is the one everybody skips, and it is what stops the eval set from quietly becoming
twenty easy tasks that every model passes.

### Three kinds of task, three kinds of score

**Generative tasks** — "explain this to a ten-year-old", "summarise this warranty in two
sentences". Score on a checklist: did it stay on topic, did it respect the length, did it invent
anything not in the source?

**Retrieval tasks** — "when does the washing machine warranty end?". Score on whether the correct
document was retrieved, which you can check before the model is even involved. This is where
problems hide that have nothing to do with the model.

**Action tasks** — "it's cold in here". Score on what the assistant *did*: the right entity, the
right action, or a refusal. Never score these on the wording of its reply. A small model that
refuses clearly is more useful than one that acts wrongly and apologises nicely.

### The scoring rule that keeps it honest

Score **pass or fail per task, not a 1–10 scale**. A 1–10 scale invites you to average your way to
a comfortable answer, and averages hide exactly the failures you care about: a model that is fine on
eighteen tasks and dangerous on the two that involve your front door.

## Show me

A worked example — four tasks from the course's own [sample
folder](../../labs/common/), written the way your own twenty should be written:

| # | Prompt | Expected | Pass condition | Why it is here |
|---|---|---|---|---|
| 1 | "When does the washing machine warranty end?" | 2027-03-14 | The date appears and no other date is given for it | The most common question you will ever ask it |
| 2 | "What do I do if the washing machine shows E3?" | Follow section 4, the filter procedure | It mentions the filter, not the pump or the sensor | Instructions must come from the document, not from general knowledge |
| 3 | "Explain the RAM bill in two sentences." | Weights + KV cache + everything else | Exactly two sentences, and all three parts present | Length control is a common failure of small models |
| 4 | "It's cold in here." | Turns on the hall heater, or asks which room | The action is right; the wording does not matter | The most common thing the voice path will ever do |

Look at row 2. A model that answers this correctly from its own training data, in fluent prose,
without mentioning the filter, **fails**. The pass condition is about the document, not about the
fluency, and that is the whole point: the document is what makes it right.

## Try it

1. Collect twenty prompts. The fastest source is your own history: what you asked in the first week
   you had any AI tool, and what you asked Home Assistant in the first month you owned it. Write
   them down now, before you start comparing, or you will write prompts that flatter whichever model
   you end up choosing.

2. Write the pass condition for each. Be specific enough that someone else could check it:

   ```text
   Task 3: "Summarise the energy bill for March in one sentence."
     Pass: the number 402 kWh appears, or the total 86.85, and only one sentence is produced.
     Why it is here: numbers are where small models invent rather than retrieve.
   ```

3. Add the "why it is here" field. At least a third of the set should be tasks that expose a
   weakness you suspect: long context, precise numbers, negation, or an action with a consequence.

4. Score three models side by side, in one sitting, in the same order every time. Use
   `temperature: 0` so the only variable is the model:

   ```bash
   for m in qwen3:4b llama3.2:3b llama3.2:1b; do
     echo "=== $m ==="
     docker compose exec ollama ollama run "$m" "Summarise the energy bill for March in one sentence."
   done
   ```

   On Windows PowerShell, the same loop:

   ```powershell
   foreach ($m in @("qwen3:4b","llama3.2:3b","llama3.2:1b")) {
     Write-Output "=== $m ==="
     docker compose exec ollama ollama run $m "Summarise the energy bill for March in one sentence."
   }
   ```

   Score as you go, one row per task per model. Do not run all twenty and then score from memory;
   you will drift.

5. Add a speed column, because the winner on quality may lose on latency:

   | Task | qwen3:4b | llama3.2:3b | llama3.2:1b |
   |---|---|---|---|
   | pass / fail | | | |
   | seconds to first word | | | |

6. Write the totals in your [measure-yours table](../../templates/measure-yours.md), and record the
   one task where your first choice failed and your final choice passed. That single row is the
   most useful thing in the whole exercise, and it is what the capstone asks you to produce.

## Break it

**Break it with a benchmark instead.** Take a model that tops a public leaderboard and install it.
It will be better at being a general assistant and often worse at reading your particular
documents, because your documents are not what the benchmark was written on.

**Break it by testing prompts you invented while comparing.** Write the prompts after you have a
favourite model. They will unconsciously favour it, and you will not notice.

**Break it by scoring on vibes.** "That answer felt better" is a measurement, of you, on a good
day. Convert it to a checklist before you run the next one, or you will find yourself defending a
choice with adjectives.

**Break it by dropping the failures.** Twenty tasks with four failures is a result. Nineteen tasks
with the four failures deleted is marketing. Keep the hard ones, and write down why each one is
there — that field is what makes the set defensible later.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Every model scores 20/20 | The tasks are too easy, or the pass conditions are vague | Add tasks you expect to fail, and tighten the conditions |
| One model wins on quality and loses everywhere else | You scored quality only | Add the speed column; the trade-off is the answer |
| The scores change between runs | Temperature is not 0, or the model is nondeterministic | Set `temperature: 0` and re-run the ones that changed |
| The wrong model is chosen on the action tasks | You scored the wording of the reply | Score what was *done*, not how it was said |
| You cannot tell which failure was the model's | Retrieval and generation were scored together | Score retrieval first, before the model is involved |

The fix in the last row is the most valuable habit here: **separate what you found from what you
generated.** A correct answer from the wrong document is a retrieval problem, and no amount of
model comparison will fix it.

## How do I know it works?

- [ ] You have at least 20 tasks, each with a prompt, a pass condition and a reason.
- [ ] At least a third of them are the kind you expect a small model to fail.
- [ ] Three models have been scored on the same set in the same sitting, at `temperature: 0`.
- [ ] Your table has a speed column as well as a pass column.
- [ ] You can name one task where your first choice failed and your final choice passed.
- [ ] The chosen model is justified with a number, not an adjective.

## Use it when / avoid it

**Build the set once, re-run it when the model changes.** A new small model appears every month;
re-running twenty tasks takes ten minutes and turns "is this one better?" from a matter of taste
into a matter of record.

**Keep retrieval tasks in the set**, even though they say nothing about the model. They are how you
notice that your retrieval broke, which is a different failure with the same symptom.

**Do not grow the set past what you will maintain.** Twenty is enough to distinguish models; a
hundred is a project nobody finishes.

**Do not use it as a benchmark to publish.** This is your household's eval set, and its value comes
from being specific, not from being large.

> [!TIP]
> **If you have a GPU.** The eval set becomes even more valuable, because a GPU makes the larger
> model fast enough that the speed column stops dominating the decision. On a CPU, speed is usually
> the reason the smaller model wins; on a GPU it is often the reason the larger one wins.

## Reflect

1. Which task in your set does every model fail? That one is telling you something about your
   documents, not about the models.
2. If the fastest model passes 16 of 20 and the slowest passes 19, which do you choose for a voice
   pipeline with a three-second budget? What would change your answer?
3. What would you have to change about your documents to make a retrieval failure impossible, and
   is that a model decision or a data decision?

## Sources

- [Benchmark numbers and where they come from](../../references/benchmarks.md)
- [Sample labelled questions](../../labs/common/)
- [Measure-yours tables](../../templates/measure-yours.md)
- [22 · Is the answer right?](../module-06/lesson-03.md) — the same method applied to retrieval
- [Jeff Geerling — ai-benchmarks](https://github.com/geerlingguy/ai-benchmarks)