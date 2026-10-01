---
id: "05.1"
module: 5
minutes: 13
practice_minutes: 40
prerequisites: ["04.2"]
objectives:
  - Name the jobs a home stack actually has, and say which model type each one needs.
  - Choose between one large model for everything and several small models, using your RAM bill.
  - Explain why the smallest model that does the job beats the biggest one that fits.
volatility: concept
sources:
  - title: "Pinned models and licences"
    url: https://github.com/ggml-org/llama.cpp
  - title: "Home Assistant Ollama integration"
    url: https://www.home-assistant.io/integrations/ollama/
last_verified: "2026-09-30"
---

# 05.1 · One model per job

A home stack does not have one job. It has four, and they want different things: being right,
being fast, being small, and being good at following a format. This lesson is about matching a model
to each job on a fixed memory budget, instead of picking the biggest thing that fits and hoping.

## Why it matters

The instinct is to pick one good model and use it for everything, and on a 32 GB machine that is
often right. It goes wrong in two specific places:

- **Tool calling.** A model that is pleasant to chat with can be unreliable at emitting a structured
  function call with exactly the right arguments. Home Assistant will happily act on a malformed
  call. This is Module 10's subject and it is measured, not assumed.
- **Embeddings.** This is not a chat model at all. It converts text into numbers, it is never
  downloaded by the same command, and it is often the *only* model that has to be resident during
  indexing.

The other reason to care is arithmetic. If one 8B model costs 5 GB and does everything at 4
tokens/s, while a 4B for chat plus a 2B for tools costs 4 GB in total and does both jobs at 7 and
15 tokens/s, the smaller pair is better at everything except raw sophistication.

## How it works

### The four jobs

| Job | Input | Output | What matters | Typical size on a 16 GB box |
|---|---|---|---|---|
| **Chat** | A question | Prose | Coherence, instruction-following, speed | 3–4B |
| **Tool calling** | A sentence plus available functions | A structured call | Format reliability above all | 3–4B trained for it, or a small dedicated one |
| **Summarising** | A document | A shorter document | Following a length limit, not inventing | 3–4B; a small model is often fine |
| **Embeddings** | Text | 768–1024 numbers | Consistent, cheap, and nothing else | 0.3–1.2 GB, separate download |

### The decisive comparison

Work in **total resident RAM**, not in "does it fit". Here is the shape of the decision on a
16 GB laptop:

| Design | Models | RAM for weights | Chat speed | Tool-call reliability | Headroom left |
|---|---|---|---|---|---|
| One model for everything | 8B | 4.9 GB | ~3–5 tok/s | Unreliable, and slow when it does work | Almost none |
| Chat plus a small tool model | 4B + 2B | 2.5 + 1.4 GB | ~7 tok/s chat | Better, and faster to answer | Enough for the voice stack |

The second row is not obviously better on paper. It is better because the *tool* path in a voice
assistant has a three-second budget and the model answering it is a third of the size.

### Why smaller is genuinely better here

Three reasons, in order of how often they bite:

1. **Latency is per token.** Halving the model roughly halves every generation, and in a voice
   pipeline latency is the product.
2. **RAM is the budget.** Every gigabyte the chat model holds is a gigabyte Home Assistant, Whisper,
   Piper and your browser cannot have. Module 2 sized the budget; this lesson spends it.
3. **Load time is paid in a hurry.** The tool model only has to be loaded once at the start of a
   voice pipeline, not between every command — but only if it is small enough that the load is a
   fraction of a second rather than several.

> [!NOTE]
> A dedicated small model trained for home control exists — `home-llM`-style fine-tunes of small
> bases. The claims that it beats larger general models are community reports, not measured
> comparisons, and this course does not build on them. Measure your own set instead, which is the
> next lesson.

## Show me

The default configuration the course uses, and why each line is what it is:

```dotenv
# labs/common/.env
CHAT_MODEL=qwen3:4b        # general conversation: the sweet spot on 16 GB
TOOL_MODEL=qwen3:4b        # the same model - one slot, no swap. See lesson 04.2.
EMBED_MODEL=nomic-embed-text  # 274 MB, a completely different kind of model
```

`CHAT_MODEL` and `TOOL_MODEL` are the **same value on purpose**. Module 4's lesson was that two
models on one slot means a swap, and a swap costs seconds in exactly the place where seconds hurt
most. If you later measure that a dedicated tool model is worth it, and you have 32 GB, change
`TOOL_MODEL` and set `OLLAMA_MAX_LOADED_MODELS=2`. If you have 16 GB, do not: find the RAM for it
in your [measure-yours table](../../templates/measure-yours.md) first.

An embedding model is chosen completely differently, because the criteria are different:

| Model | Size | Dimensions | Best for |
|---|---|---|---|
| `nomic-embed-text` | 274 MB | 768 | English mostly, fast on a CPU |
| `snowflake-arctic-embed2` | 570 MB | 1024 | English, better quality per byte |
| `bge-m3` | 1.2 GB | 1024 | Multilingual — the safer default for a mixed folder |

Note that quality here is not "intelligence". It is whether two texts that mean the same thing end
up close together. That is a narrower question, and it has a narrower answer.

## Try it

1. Write down your four jobs before you pick anything, with a sentence each. "Chat: answer
   questions about my documents, fast enough to feel normal." This step takes five minutes and
   prevents the most expensive mistake in this module.

2. Look at what you have:

   ```bash
   docker run --rm -v homelab-ollama-models:/root/.ollama ollama/ollama:0.35.0 ollama list
   ```

3. Do the arithmetic for two designs and write both totals in your measure-yours table. Use your own
   RAM figure from `homelab.py doctor`, not the example numbers.

   | Design | Weights | KV at 4096 | Headroom | Chat tok/s (predict) |
   |---|---|---|---|---|
   | 4B chat only | | | | |
   | 4B chat + 1B helper | | | | |
   | 8B for everything | | | | |

4. Measure the one comparison that matters for latency: the same question against two sizes.

   ```bash
   docker compose exec ollama ollama run qwen3:4b "Explain the RAM bill in two sentences."
   docker compose exec ollama ollama run llama3.2:1b "Explain the RAM bill in two sentences."
   ```

   Time both to the first word and to the last. The 1B answer will be worse. The question is
   whether it is bad enough to matter for the *tool* path, where the answer is a structured call
   and not an explanation.

5. Make a deliberate decision and write it down in one line: which job gets which model, and what
   you would have to give up to change it. This is exactly the capstone's "model choice" criterion,
   and doing it now is how you will have something to write.

## Break it

**Break it with one 8B for everything.** On a 16 GB machine: load it, run a long document
summarisation, and then start Home Assistant and Whisper. The box has 30 MB of free RAM, and the
failure arrives as everything being slow at once rather than as one service stopping. Nothing points
at the model.

**Break it with two models and one slot.** Set `TOOL_MODEL=llama3.2:1b`, leave
`MAX_LOADED_MODELS=1`, and alternate between a chat question and a voice-like tool request. Every
alternation pays a load. This is Module 4's lesson reproducing itself in a new place.

**Break it by swapping the quantisation for the model.** Use `F16` instead of `Q4_K_M` for the same
4B model: the file doubles, RAM doubles, and you gain quality nobody will notice in a home assistant
while losing the RAM that Whisper needs.

**Break it with the wrong kind of model for the job.** Point an embedding indexer at a chat model.
It will run, it will return numbers, and retrieval quality will be poor in a way that is hard to
diagnose because nothing errors.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| One model for everything, and it is slow | No job separation | Give the tool path its own smaller model, if RAM allows |
| Home Assistant becomes slow when chatting | The chat model took the memory budget | Lower the chat model's context, or the model, or the other services' limits |
| Retrieval finds the wrong chunk | A chat model used as an embedder | Use a real embedding model |
| The tool path works but the answers are poor | One model is doing both well enough to be useful and badly enough to annoy | Separate the jobs, or accept it explicitly and write down why |
| Alternating requests are slow | Model swap, one slot | One model for both, or two slots with room to spare |

The decision procedure, in order: **list the jobs → budget the RAM → pick the smallest model per job
→ measure → write down the gap.** Skipping step one is what produces a stack with a 7B chat model
and no embedder, which cannot answer questions over your files at all.

## How do I know it works?

- [ ] You have written down four jobs and one model per job, with a reason.
- [ ] You have predicted the RAM total for at least two designs.
- [ ] You have measured two model sizes on the same prompt and written both numbers down.
- [ ] `CHAT_MODEL` and `TOOL_MODEL` match, or you have written down why they do not.
- [ ] The RAM bill in your [measure-yours table](../../templates/measure-yours.md) includes
      everything the full stack will hold at once.

## Use it when / avoid it

**Use one model for everything** when RAM is tight, when the jobs overlap, and when you have not
yet built anything. It is the simplest thing that can work, and simplicity is a legitimate
engineering choice.

**Use a separate small model for tool calling** when you have 32 GB, when you have measured that
your chat model is unreliable at tool calls, and when you can afford two model slots.

**Avoid the largest model that fits.** "Fits" is a memory constraint, not a quality one, and on a
CPU the quality gain from 8B over 4B is much smaller than the speed and RAM cost.

**Do not assume a model card's tool-calling claim transfers to your use.** Benchmarks are usually
measured with many entities and a structured prompt; Home Assistant with your twenty devices and a
voice transcription in front of it is a different task. Measure it — next lesson.

> [!TIP]
> **If you have a GPU.** The trade-off in this lesson shifts: more parameters stop being as
> expensive, so a single larger model for everything becomes more attractive and the latency
> advantage of a small tool model shrinks. None of that changes the RAM bill, which is why the
> course's conclusions still hold.

## Reflect

1. List your four jobs and the model you picked for each. Which one are you least sure about, and
   what measurement would settle it?
2. If you had to drop one of the four jobs entirely for a year, which would cost you least, and
   what RAM would that free?
3. Your measure-yours table has a RAM bill. How much of it is chat, how much is everything else,
   and which of those two numbers would you defend first if someone questioned your setup?

## Sources

- [Pinned models and licences](../../references/models.md)
- [Home Assistant Ollama integration](https://www.home-assistant.io/integrations/ollama/)
- [Home Assistant LLM API — how intents become tools](https://developers.home-assistant.io/docs/core/llm/)
- [Measure-yours tables](../../templates/measure-yours.md)
- [The RAM bill](../module-02/lesson-02.md)