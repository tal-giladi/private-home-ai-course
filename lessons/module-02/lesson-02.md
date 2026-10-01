---
id: "02.2"
module: 2
minutes: 12
practice_minutes: 20
prerequisites: ["02.1"]
objectives:
  - >-
    Write the RAM bill for one model on your machine: weights, KV cache, runtime overhead, and
    everything else the box is already running.
  - >-
    Compute a KV cache size for a given model and context length from the model's own
    configuration.
  - >-
    Decide whether a 16 GB machine can hold the whole stack, and what to drop first if not.
  - >-
    Tell the difference between "it ran out of memory" and "it started swapping", and why only
    one of them is survivable.
volatility: concept
sources:
  - title: "Stratosphere — model sizes and measured RAM use on a Raspberry Pi 5"
    url: https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html
  - title: "Ollama FAQ — parallel requests, and quantising the K/V cache"
    url: https://docs.ollama.com/faq
  - title: "whisper.cpp README — resident memory per speech-to-text model"
    url: https://github.com/ggml-org/whisper.cpp
last_verified: "2026-09-30"
---

# 02.2 · The RAM bill

"It fits" is not a memory plan. A 2.5 GB model on a 16 GB laptop is a sentence about a model, not
about a machine, and the machine is already running an operating system, a browser, and
eventually a chat interface, a vector store, Home Assistant and two voice services. This lesson is
the invoice: four items, each with a number you can get, added against a total you already know.

## Why it matters

Out of memory on a home AI machine is almost never a clean failure. The model memory-maps its
weights from disk, so it *appears* to load even when the memory is not there, and then every single
token costs a page fault. The symptom is not an error — it is a machine that is technically
functional and unusable, sometimes intermittently, usually worse when you open one more tab.

The second reason to do this arithmetic now is that the *items* on the bill are design decisions.
Context length, quantisation, model size, how many models are resident, whether the voice pipeline
shares a box with chat — every one of them is a line you can move, and you cannot move any of them
well until you have seen the whole bill. [09 · Pick the largest model that meets your
target](../module-02/lesson-04.md) is where you spend the result.

## How it works

The bill has four items, and they are not equally important.

### 1. Weights — the file, and it is exactly what you downloaded

| Model | Q4_K_M file, about |
|---|---|
| `gemma3:1b` | 0.8 GB |
| `qwen2.5:1.5b` | 1.0 GB |
| `llama3.2:3b` | 2.0 GB |
| `qwen3:4b` | 2.5 GB |
| `qwen2.5:7b` | 4.7 GB |
| `llama3.1:8b` | 4.9 GB |

Figures from the course's [pinned model list](../../references/models.md); check yours with
`ollama list`, which reports the file on your disk rather than a table.

### 2. The KV cache — the part that grows, and the part people forget

To generate a token the model attends over everything it has read, so it keeps a key and a value
vector for every token in the context. That cache is proportional to context length, and it is
the reason a 4 096-token conversation and a 32 768-token one are not the same size of thing:

$$\text{KV bytes} = 2 \times L \times H_{kv} \times D \times b \times C$$

where $L$ is the layer count, $H_{kv}$ the number of key/value heads (small on models that use
grouped-query attention, which is most of them), $D$ the head dimension, $b$ the bytes per
element — 2, because the cache is f16 by default — and $C$ the context length. Every one of those
is in the model's own configuration, and you can read them yourself:

```bash
ollama show llama3.2:3b
# Parameters        3.2 B
# Context Length    131072
# Block Count       28
# Attention Head Count    32
# Attention Head Count K/V 8
# Embedding Length  3072
```

Block count is the layer count, head count K/V is $H_{kv}$, and the head dimension is the
embedding length divided by the attention head count. Worked out for three models you will meet
in this course, at f16:

| Model | Cache per token | At 4 096 | At 8 192 | At 32 768 |
|---|---|---|---|---|
| Llama 3.2 1B (16 layers, 8 KV heads, dim 64) | 32 KiB | 128 MiB | 256 MiB | 1.0 GiB |
| Llama 3.2 3B (28 layers, 8 KV heads, dim 128) | 112 KiB | 448 MiB | 896 MiB | 3.5 GiB |
| Llama 3.1 8B (32 layers, 8 KV heads, dim 128) | 128 KiB | 512 MiB | 1.0 GiB | 4.0 GiB |

This is arithmetic on published model configurations, not a measurement — and it is the kind of
arithmetic you can check in a minute with the command above, which is why it is worth doing rather
than guessing. The grouped-query detail is the one that catches people: a model with 32 attention
heads may have only 8 key/value heads, and that factor of four is why an 8B model does not need
32 GB to chat.

### 3. Runtime overhead — not zero, and not small

The weights are not the only thing in the process. There are the compute buffers, the scratch
space the kernels need, the tokeniser, and the KV cache from item 2. The benchmark reference
gives a way to see the size of this without instrumenting anything: take the measured total RAM
and subtract the file size, and what is left is everything that is not weights.

| Model on a Raspberry Pi 5 | File, about | Measured RAM, cited | The difference |
|---|---|---|---|
| Gemma 3 1B | 0.8 GB | 1.4 GB | 0.6 GB |
| Qwen2.5 1.5B | 1.0 GB | 1.9 GB | 0.9 GB |
| Llama 3.2 1B | 0.8 GB | 2.4 GB | 1.6 GB |
| Qwen2.5 3B | 2.0 GB | 3.0 GB | 1.0 GB |
| Llama 3.2 3B | 2.0 GB | 4.7 GB | 2.7 GB |

All from the [Stratosphere Pi 5 study](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html),
by subtraction. Read the spread, 0.6 GB to 2.7 GB, and note that it is not a constant you can
add once: it depends on the context the study used, on how the memory was measured, and on the
model. Budget something in that range and then replace it with your own number, which is what the
measure-yours table is for.

One real lever here, from the Ollama FAQ: `OLLAMA_KV_CACHE_TYPE` quantises the cache itself —
`q8_0` uses about half the memory of the f16 default, `q4_0` about a quarter, at a small cost in
precision. It needs Flash Attention and it is a global setting, which is why it belongs to
[05 · Settings that change the answer](../module-01/lesson-03.md) as an optimisation rather than
as a starting move.

### 4. Everything else on the box

This is the item nobody budgets for, because it is not part of the model. The course's sizing
calculator uses these planning allowances, and they are deliberately generous so that a plan built
on them survives contact with a real machine:

| Item | Allowance | Note |
|---|---|---|
| Chat interface | 1.2 GB | grows with history and with a long document open |
| Home Assistant | 1.0 GB | more with add-ons; the Container build is lighter than HA OS |
| Voice services | 1.6 GB | Whisper `base` is about 388 MB resident, plus Piper and the protocol layer |
| Vector store and embedder | 1.2 GB | the embedder is small; the index is what grows |
| Browser, ten tabs | 1.5 GB | the most optimistic number on this list |
| Operating system | 2.5 GB | the most machine-specific number on this list |

[Simulation: Sizing a home AI stack](../../simulations/sizing/index.html?preset=tier-a)

[Simulation: Sizing a home AI stack with the voice services](../../simulations/sizing/index.html?preset=voice)

The two numbers to distrust most are the last two, because they are the ones that differ most
between machines. Measure them on yours; the commands are in the next section.

### The bill for a 16 GB laptop

This is the number most people in this course will care about, so here it is in full. Two
configurations, same machine, `qwen3:4b` in both, differing in what else is running:

| Item | Chat only | Full stack |
|---|---|---|
| Weights (`qwen3:4b`, Q4_K_M) | 2.5 GB | 2.5 GB |
| KV cache at 4 096 | 0.6 GB | 0.6 GB |
| Runtime overhead and buffers | 1.0 GB | 1.0 GB |
| Chat interface | 1.2 GB | 1.2 GB |
| Home Assistant | — | 1.0 GB |
| Voice services | — | 1.6 GB |
| Vector store and embedder | — | 1.2 GB |
| Browser | 1.5 GB | 1.5 GB |
| Operating system | 2.5 GB | 2.5 GB |
| **Total** | **9.3 GB** | **13.1 GB** |
| **Left on a 16 GB machine** | **6.7 GB** | **2.9 GB** |

The KV row is computed for a 4B model of Qwen3's shape — 36 blocks, 8 key/value heads, head
dimension 128, so 144 KiB per token — and you should recompute it for your own model with the
command in item 2. The overhead row uses the middle of the range derived above rather than its
optimistic end.

The honest conclusion: **16 GB is enough for the whole stack with a 3–4B model, and it is not
generous.** 2.9 GB of headroom is enough to run, not enough to be careless — one video call, one
spreadsheet, one extra container and the machine is paging. If you are on 16 GB, the first thing
to give up is the vector store, because it is the one service that can be started when you need it
instead of always, and it is the optional module. If you are on 32 GB, the same bill has 18.9 GB
spare, which is what makes a 7–8B model possible at all.

> [!TIP]
> The order to cut in, if the total is over your headroom: context length first (it is free to
> reduce and nobody notices at 4 096), then the quantisation (Q4_K_M before Q8_0), then a smaller
> model, then a service that is always-on but rarely needed. Never cut the operating system or the
> browser's real usage — those are the numbers that will surprise you.

## Show me

The whole bill in one formula, which is the thing to remember:

$$\text{headroom} = \text{total RAM} - \text{file size} - \text{KV cache} - \text{runtime overhead} - \text{everything else}$$

and the two things to measure, in order of how much they surprise people:

1. **What the box is using before you start anything.** This is `everything else`, and it is
   usually bigger than you think.
2. **What the model process uses when it is loaded.** The difference between the two is your
   runtime overhead, and it is a number about *your* machine rather than a range from a paper.

The [measure-yours table](../../templates/measure-yours.md) has a RAM bill section with exactly
these rows, and filling it in is this lesson's deliverable. The [troubleshooting
page](../../references/troubleshooting.md) covers the case where the answer turns out to be "the
Docker VM has its own memory limit", which on Windows is a real and commonly missed cause.

## Try it

Measure the two numbers that only your machine can tell you. Before you load anything:

```bash
# Linux
free -h
# macOS — not verified by us; the course has one Windows test machine
vm_stat | head -5
```

```powershell
# Windows PowerShell: total, available, and the largest processes
Get-CimInstance Win32_OperatingSystem |
  Select-Object @{n='TotalGB';e={[math]::Round($_.TotalVisibleMemorySize/1MB,1)}},
                @{n='FreeGB';e={[math]::Round($_.FreePhysicalMemory/1MB,1)}}
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 8 Name,
  @{n='MB';e={[math]::Round($_.WorkingSet64/1MB)}}
```

Now start the model, ask it one long question so the KV cache fills, and measure again with the
model resident:

```bash
# Linux and macOS: resident size of the model process
ps -o rss= -C ollama | awk '{printf "ollama: %.2f GB\n", $1/1048576}'
```

```powershell
# Windows PowerShell
Get-Process ollama | Select-Object Name, @{n='RAM_GB';e={[math]::Round($_.WorkingSet64/1GB,2)}}
```

Then fill this in — the [RAM bill table](../../templates/measure-yours.md) in the template is the
right place for it:

```text
File size on disk:                 __ GB
KV cache at my context length:     __ GB   (from the formula, with my model's config)
Runtime overhead:                  __ GB   (loaded minus the two rows above)
Everything else, before I started:  __ GB
Total RAM:                         __ GB
Headroom left:                     __ GB
Headroom at 8 GB or more?          yes / no
What I would drop first:           ______________________
```

The "8 GB or more" threshold comes from the template, and it is a sensible one: below that, a
machine that also runs a browser is always one update away from paging.

## Break it

**Break it with a context that is too large.** Set a 32 768 context on that 16 GB laptop, with
the full stack running. From the table in item 2, the KV cache for a 3B model at 32 768 is
3.5 GB instead of 448 MiB — about 3 GB that the bill never planned for. The total goes over, and
the failure mode is the ugly one: not an allocation error, but a machine that pages, because the
runtime memory-maps the weights and believes the load succeeded.

**Break it with two models loaded.** Ollama's default allows several models to be resident at
once, and the FAQ is explicit that the required RAM scales with parallel requests times context
length. A 4B chat model plus a 3B embedding-adjacent model plus a voice model is three bills in
one 16 GB budget, and `ollama ps` is where you will see all three listed with their `UNTIL` times.

**Break it with the container runtime's own limit.** On Windows, Docker Desktop has a memory limit
of its own, independent of your RAM, and WSL2 caps it again; the smaller limit wins and the
symptom is your model process being killed with no useful log line. On Linux, if the VM has no
swap and you overcommit, the out-of-memory mechanism takes the largest process — which is the
model server. Both are in [the troubleshooting page](../../references/troubleshooting.md).

**Break it by believing the free number before the load.** Available memory measured on an idle
machine is not the number that matters. The number that matters is what is left after the weights
are resident, and the only way to know it is to look while it is running.

## Fix it

1. **Budget 8 GB of headroom, not zero.** If the bill says otherwise, cut the model, the context or
   a service — not the margin.
2. **Set the context from the job.** 4 096 for chat, 8 192 for a question over a retrieved
   document. Recompute the KV row for each.
3. **Keep the quantisation at `Q4_K_M`.** It is the cheapest quality-per-megabyte point on the
   curve, and the memory saved is a full service.
4. **Give every service a memory limit in `.env`.** `OLLAMA_MEMORY_LIMIT` and
   `WEBUI_MEMORY_LIMIT` are the two that matter on a small machine, and a limit turns "the whole
   machine froze" into "one container was restarted" — a failure you can see and reason about.
5. **Do not keep models resident forever.** A short `keep_alive`, or `ollama stop` between
   activities, returns several gigabytes between experiments.
6. **Start optional services on demand.** A vector store that is only running when you are asking
   questions about your files is a service that costs nothing the rest of the time.
7. **On Windows, check the Docker memory limit before you blame the model.** It is the most common
   cause on that platform and it is in the wrong place to look.

## How do I know it works?

- [ ] The RAM bill in [the measure-yours table](../../templates/measure-yours.md) is filled in with
      your own numbers, and every row says where the number came from.
- [ ] You have computed a KV cache size for your actual model and context, from its own reported
      configuration, and the arithmetic is written out.
- [ ] You have measured the model process's resident memory while it is loaded, and the difference
      from the file size is your own overhead figure rather than a range from a paper.
- [ ] You can say what you would drop first on your machine, and why that rather than something
      else.
- [ ] You know whether the headroom is above or below 8 GB, with the load that produced that
      number.

## Use it when / avoid it

**Do this before adding a service, not after.** Every service in the stack is a line on the bill,
and the sum is what decides whether the machine is pleasant or merely functional. Adding voice to
a machine that already runs chat and retrieval is a 2.6 GB decision.

**Redo the bill whenever the model changes.** A model swap is the cheapest change to make and the
one most likely to be made without arithmetic — half the people in this course will end up with a
different model from the one on this page, and the bill is five minutes of work.

**Avoid counting only the file size.** It is the number printed in `ollama list`, it is the number
everybody uses, and on a loaded machine it understates the truth by 0.6 to 2.7 GB according to the
published Pi 5 data above.

**Avoid treating a working system as a sufficient one.** The bill is not only about whether the
model loads; it is about whether the machine is still responsive when you ask a second question
while a voice command is running. That is a concurrency question as much as a memory question, and
Module 4 is where two residents on one box is a deliberate design decision rather than an accident.

## Reflect

1. Which row of your bill was furthest from what you expected, and why do you think that is?
2. If you wanted a 7–8B model, what would have to give — and how much would be left over for a
      browser and the voice services?
3. You have 2.9 GB of headroom. Name the one change you would make first, and the measurement
      that would tell you it was the right one.

## Sources

- [Stratosphere — model sizes and measured RAM use on a Raspberry Pi 5](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html)
- [Ollama FAQ — parallel requests scaling RAM, and `OLLAMA_KV_CACHE_TYPE`](https://docs.ollama.com/faq)
- [whisper.cpp README — resident memory per speech-to-text model](https://github.com/ggml-org/whisper.cpp)
- [Measure-yours tables — the RAM bill section](../../templates/measure-yours.md)
- [Troubleshooting by symptom — including Docker's own memory limit](../../references/troubleshooting.md)
- [Pinned models and licences — the Q4_K_M file sizes, and the voice models](../../references/models.md)
