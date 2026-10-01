---
id: "01.3"
module: 1
minutes: 12
practice_minutes: 20
prerequisites: ["01.2"]
objectives:
  - Change temperature, context size, `num_predict`, keep-alive and thread count, and say what each
    one costs and buys.
  - Explain why a context window that is too large slows every single token as well as eating RAM.
  - Read the defaults a model is actually running with, instead of assuming them.
  - Decide the context size and keep-alive value your machine should use, and write them down.
volatility: implementation
sources:
  - title: "Ollama FAQ — context size, keep-alive, parallel requests and KV cache type"
    url: https://docs.ollama.com/faq
  - title: "Ollama — context length defaults, which are 4k without a GPU"
    url: https://docs.ollama.com/context-length
  - title: "llama.cpp llama-server — the equivalent flags and their defaults"
    url: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
last_verified: "2026-09-30"
---

# 01.3 · Settings that change the answer

Ask the same question of the same model twice, with one setting changed, and you can get a
different answer, a different speed, or a machine that stops responding. That is not the model
being temperamental — it is five settings that most people never look at, each with a default that
was chosen to be safe rather than to be right for you. This lesson is about opening that panel.

## Why it matters

Three of the five settings here change how much memory the model needs, and one of them changes
the answer. The one that changes the answer is the one everybody notices, usually by accident:
a context window of 512 tokens on a model that expects a conversation makes the model forget what
was said two exchanges ago, and people conclude the model is bad at multi-turn chat.

The other two are the ones that hurt. A context window set to 128 000 on a machine with 16 GB
allocates a KV cache far larger than the memory available, and a model left loaded forever means
the browser, the voice services and everything else are competing with it permanently. Both
failures are silent, both are extremely common, and both are one line of configuration.

## How it works

There are five settings, and it helps to sort them by what they actually cost.

| Setting | Default | Buys you | Costs you |
|---|---|---|---|
| `num_ctx` | 4096 on a machine without a GPU | A longer conversation, longer documents, retrieval chunks | RAM for the KV cache, and bandwidth on **every** token |
| `temperature` | 0.8 | Variety and creativity above 0; repeatability at 0 | Nonsense above about 1.2 |
| `num_predict` | unlimited, until the model stops | A cap on runaway answers | Nothing, if you leave it alone |
| keep-alive | 5 minutes | No reload on the next request | The RAM stays claimed between requests |
| `num_thread` | decided by the runtime | Faster prompt processing on a many-core machine | Nothing for generation, which is bandwidth-bound |

### `num_ctx`: the setting that costs twice

Context size is the number of tokens the model can hold at once: the system prompt, the whole
conversation so far, and the reply it is writing. Ollama picks 4096 on a machine with no GPU
above 24 GB of VRAM to spend, which is every machine in this course, and the FAQ tells you the
same default in one line. That default is a reasonable floor and a bad ceiling: for home chat,
4096 is usually enough; for a question over a retrieved document you will want 8192.

Setting it larger costs RAM, which is obvious, and it also costs **speed on every token**, which is
not. Here is why. When the model generates, it has to look at everything it has read so far — that
is what attention does — so the key and value cache, the KV cache, is read for each new token.
Double the context and you have roughly doubled the bytes read per token, on a machine that was
already bandwidth-limited. [06 · Memory bandwidth sets your speed](../module-02/lesson-01.md) has
the arithmetic, and [07 · The RAM bill](../module-02/lesson-02.md) has the sizes.

Set it three ways, depending on where you are:

```bash
# 1. in the chat, for this session only
ollama run qwen3:4b
>>> /set parameter num_ctx 8192

# 2. for the server, for every model it serves
OLLAMA_CONTEXT_LENGTH=8192 ollama serve
```

```powershell
# Windows PowerShell, for this session
$env:OLLAMA_CONTEXT_LENGTH = "8192"
ollama serve
```

```bash
# 3. per request, from the API - this is what the course's own bench script does
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:4b",
  "messages": [{"role": "user", "content": "hi"}],
  "options": {"num_ctx": 8192}
}'
```

And read back what is actually in force, rather than trusting your memory of what you set:

```bash
ollama ps          # the CONTEXT column shows the size the model is running with
```

### `temperature`: the only setting that changes the answer

Temperature scales how far the model is allowed to wander when it picks the next token. At 0 it
always takes the most likely token, so the same prompt gives the same answer — which is what you
want when you are comparing two models. Around 0.7–0.8 is normal chat. Above 1 it starts
producing confident nonsense, and a 4B model gets there sooner than you would like.

```bash
# deterministic, for measurements and for model comparisons
ollama run qwen3:4b
>>> /set parameter temperature 0.0
>>> Explain what a bloom filter is, in three sentences.
```

`homelab.py bench` sets temperature 0 for exactly this reason: a measurement should not change
because the sampler had a different mood.

### `num_predict`: a cap, not a setting you must touch

`num_predict` is the maximum number of tokens the model may generate. Left alone, generation
continues until the model emits an end token. It is worth knowing about for one reason: a model
that has lost the thread of the conversation can generate for a very long time, and on a slow
machine that is minutes of CPU. The bench script uses 64 for this reason.

### keep-alive: RAM you have chosen to give away

After a request, Ollama keeps the model in memory for five minutes by default, so the next
question does not pay the load time again. On a 16 GB machine that is a real decision: 2.5 GB of
weights and a KV cache held for five minutes after you stopped asking anything.

```bash
# what is loaded, and how long it stays
ollama ps                     # the UNTIL column is the keep-alive in plain English

# give the memory back now
ollama stop qwen3:4b

# keep it loaded for an hour (useful for a demo, wasteful for a laptop)
OLLAMA_KEEP_ALIVE=1h ollama serve
```

```powershell
# Windows PowerShell: unload five minutes after the last request
$env:OLLAMA_KEEP_ALIVE = "5m"
ollama serve
```

Module 4 uses this deliberately when a second model has to be resident at the same time.

### threads: the setting that only helps one of the two speeds

`num_thread` sets how many CPU threads the runtime uses. It has almost no effect on generation,
which is bounded by memory bandwidth, and a large effect on prompt processing, which is
arithmetic and scales with cores. So the correct value is the number of physical cores, and the
reason it is "and not more" is [08 · Measure prompt speed and generation
speed](../module-02/lesson-03.md). Set it once, then forget it:

```bash
# inside the chat, for this session
>>> /set parameter num_thread 8
```

## Show me

The whole panel, with the command that changes it. This table is the one to come back to.

| I want to | Do this | Check it with |
|---|---|---|
| A longer conversation | `/set parameter num_ctx 8192` | `ollama ps` → CONTEXT |
| Repeatable answers | `/set parameter temperature 0.0` | Ask the same question twice |
| A shorter answer | `/set parameter num_predict 200` | The reply stops sooner |
| Free the memory now | `ollama stop qwen3:4b` | `ollama ps` is empty |
| Load once for a demo | `OLLAMA_KEEP_ALIVE=1h ollama serve` | `ollama ps` → UNTIL |
| Faster long prompts | `/set parameter num_thread 8` | `bench` prompt tok/s |
| See every current value | `/show parameters`, then `/show info` | — |
| Change the server default | `OLLAMA_CONTEXT_LENGTH=… ollama serve` | `ollama ps` → CONTEXT |

Inside the chat, `/help` lists the rest: `/set system` for a persona, `/show`, `/load`, `/save`,
`/bye`. The two you will use in this course are `/set parameter` and `/show parameters`, because
they are the difference between "the model is bad" and "the model was configured this way".

> [!NOTE]
> macOS: the settings, the slash commands and the defaults are the same; only the way you set a
> server-wide environment variable differs, because the app is launched by the desktop rather than
> by your shell. **These steps are not verified by us** — the course has one Windows test machine
> — so if a default looks different on your Mac, believe your Mac and write the number you see.

## Try it

Make the context cost visible with two runs of the same question, and write down what it costs.
This is the experiment that makes the setting stick, and it takes four minutes.

```bash
# run 1: the default context
ollama run qwen3:4b --verbose "Summarise the water cycle in about 150 words."
```

```bash
# run 2: a small context, so the difference is unmistakable
ollama run qwen3:4b
>>> /set parameter num_ctx 512
>>> /set parameter temperature 0.0
>>> Summarise the water cycle in about 150 words.
>>> /show parameters
>>> /show info
```

Then, in a second terminal, watch the memory while the model is loaded:

```powershell
# Windows PowerShell
Get-Process ollama -ErrorAction SilentlyContinue | Select-Object Name, @{n='RAM_GB';e={[math]::Round($_.WorkingSet64/1GB,2)}}
```

```bash
# Linux / macOS
ps -o rss= -C ollama | awk '{printf "%.2f GB\n", $1/1048576}'
```

Record four numbers in [the measure-yours table](../../templates/measure-yours.md):

```text
Context 512  — generation rate __ tok/s, process RAM __ GB
Context 4096 — generation rate __ tok/s, process RAM __ GB
Difference in RAM:            __ GB
Ratio of generation rates:    __
```

The RAM difference is the KV cache, and it is the number that will size your context in
[07 · The RAM bill](../module-02/lesson-02.md). If the generation rate barely moved, your machine
has bandwidth to spare and a longer context is affordable — and if it moved a lot, you now know
exactly what a 32 000-token context would cost you.

## Break it

**Break it the way it actually happens: a context far larger than the job needs.** Ask for a
128 000-token context on a 16 GB machine with a 4B model:

```bash
# Windows PowerShell
$env:OLLAMA_CONTEXT_LENGTH = "131072"
ollama serve
```

```bash
# macOS / Linux
OLLAMA_CONTEXT_LENGTH=131072 ollama serve
```

What you get is a KV cache sized for 128 000 tokens whether or not one token is ever used. Do the
arithmetic once: a 3B model with grouped-query attention needs roughly 112 KiB of KV cache per
token, so 128 000 tokens is about **14 GB** of allocation on top of the weights —
[07 · The RAM bill](../module-02/lesson-02.md) works the numbers. The model may therefore fail to
load, or load and push the machine into paging, or — worst — load and run, slightly slower on
every single token, with no error anywhere. Then ask it a two-sentence question and wonder why it
feels sluggish.

**Break it with parallelism, which multiplies the context.** Ollama's FAQ states it plainly:
required RAM scales by `OLLAMA_NUM_PARALLEL` times `OLLAMA_CONTEXT_LENGTH`. Set four parallel
requests and a 8192 context, and the allocation is sized as though you had four conversations
open at once, whether or not you ever make four.

```bash
OLLAMA_NUM_PARALLEL=4 OLLAMA_CONTEXT_LENGTH=8192 ollama serve
```

**Break it with keep-alive.** Set `OLLAMA_KEEP_ALIVE=-1` to keep a model resident forever, start
Home Assistant and the voice services, and the machine has no memory left for any of them. The
model is not slow; the box is full, and the failure will look like three unrelated services being
broken.

**Break it with temperature.** Set it to 1.5 and ask the same factual question five times. A 4B
model at high temperature produces a different wrong answer every time, which is the fastest way
to convince a sceptic that "local models are unreliable" is a setting, not a verdict.

## Fix it

1. **Set the context from the job, not from the model's maximum.** Home chat: 4096. A question
   over a retrieved document: 8192. Anything above that needs an argument, and the argument is
   measured memory. `ollama ps` shows what is actually running.
2. **Set temperature to 0 when you are measuring or comparing.** Non-zero is for writing, not for
   benchmarking, and it costs you the ability to reproduce anything.
3. **Set `num_predict` when a runaway answer is worse than a truncated one** — a voice assistant
   with a 3-second budget is the case that matters, and Module 10 is where you will need it.
4. **Set keep-alive to the shortest value your usage allows.** Five minutes is a sensible default
   on a 16 GB machine; `0` when you want the RAM back immediately; a long duration only for a
   machine that does nothing else. `ollama stop` is always available as a manual release.
5. **Leave `num_thread` at a physical core count.** Beyond that, generation stops improving and
   prompt processing keeps going; [08 · Measure prompt speed and generation
   speed](../module-02/lesson-03.md) is the lesson that shows you which of your two numbers is
   which.
6. **If you must have a large context cheaply,** Ollama can quantise the KV cache itself with
   `OLLAMA_KV_CACHE_TYPE` — `q8_0` uses about half the memory of the `f16` default and `q4_0`
   about a quarter, at some cost in precision that is usually invisible. It is a global setting and
   it needs Flash Attention, so treat it as a Module 4 optimisation rather than a first move.

> [!TIP]
> **Do it yourself with llama.cpp.** Every setting above has a direct equivalent on the command
> line, which is the fastest way to see what a value actually does:
>
> ```bash
> llama-server -m models/qwen3-4b-instruct-q4_K_M.gguf --host 127.0.0.1 --port 8080 -c 8192 -t 8 --temp 0.0 -ngl 0
> ```
>
> The parameters worth playing with: `-c` (context, the same `num_ctx`), `--temp` (the server's
> default is 0.8), and `-t` (threads). `llama-server` also exposes `-ctk` and `-ctv` to change the
> KV cache type per run rather than globally, and `-n` to cap generated tokens the way
> `num_predict` does. Start the server, hit it with `curl http://127.0.0.1:8080/v1/chat/completions`,
> and the response includes a `timings` object with `prompt_per_second` and `predicted_per_second`
> — the two numbers this module keeps talking about, for the run you just did.

> [!NOTE]
> **If you have a GPU.** A GPU changes the arithmetic underneath all five settings, and it is worth
> knowing how even though nothing here requires it. A discrete card's memory bandwidth is much
> higher than dual-channel DDR5, so generation speeds up — but its memory is also much smaller, so
> `num_ctx` becomes the binding constraint much sooner, and an oversized context fails on VRAM
> rather than on system RAM. `ollama ps` shows the `PROCESSOR` column as `100% GPU`, `100% CPU` or
> a split. For a split, the honest answer is to measure: `llama-bench -m <file> -ngl 0` against
> `-ngl 99`, on the same machine, at the same `-c`. Partial offload moves the KV cache across the
> PCIe link, and on consumer cards that often costs more than it saves. Keep-alive matters more
> too: on a GPU the model is also a chunk of VRAM that other software wants.

## How do I know it works?

- [ ] `/show parameters` prints values you recognise, and you have written down the ones you will
      keep.
- [ ] You have run the same question at two context sizes and can quote both generation rates and
      both memory readings.
- [ ] `ollama ps` shows a CONTEXT value you chose, not a default you inherited.
- [ ] After a break, `ollama stop <model>` demonstrably gives the memory back.
- [ ] You can explain, in one sentence, why a bigger context is slower per token and not just
      bigger.

## Use it when / avoid it

**Change settings one at a time and write down what changed.** Two changes at once produce a result
you cannot attribute, and "it feels better" is not a finding. The measure-yours table has a place
for exactly this.

**Keep the context modest and the temperature at zero for anything you intend to compare** — two
models, three settings, one question. Once you are past measuring, raise the temperature for
writing and leave it alone.

**Raise keep-alive only where a reload is actually expensive to the user.** In a voice pipeline
where every command has a latency budget, reloading a 2.5 GB model on the first question of the
morning is a real cost, and keeping it loaded is worth the RAM. In a chat session, it is not.

**Avoid tuning a machine that is thermally throttling or short of memory.** A CPU that drops
clocks after ten minutes and a machine that is paging will both look like "settings are wrong",
and neither is fixed by a setting. [07 · The RAM bill](../module-02/lesson-02.md) and
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md) are the two lessons that tell
those two causes apart.

## Reflect

1. By how much did your context size change the process memory, and what does that imply for a
      32 000-token context on the same machine?
2. Did the generation rate change with the context size? If it did not, what does that say about
      whether your machine is bandwidth-bound?
3. Which of the five settings would you change on an always-on machine, which on a laptop, and
      which not at all in either?

## Sources

- [Ollama FAQ — context size, keep-alive, parallel requests, KV cache type and the default bind address](https://docs.ollama.com/faq)
- [Ollama — context length, and why 4k is the default without a GPU](https://docs.ollama.com/context-length)
- [llama.cpp `llama-server` — the same settings as flags, with their defaults](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)
- [Pinned versions](../../references/versions.md) — which settings belong to the stack and which to your machine
