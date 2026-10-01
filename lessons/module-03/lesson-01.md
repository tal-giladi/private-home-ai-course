---
id: "03.1"
module: 3
minutes: 12
practice_minutes: 25
prerequisites: ["02.4"]
objectives:
  - Decide whether to run the stack on the machine you already own or on a second, always-on host.
  - Compare a mini PC, an old desktop, a Raspberry Pi 5 and a laptop on the four things that matter: memory bandwidth, RAM, noise and idle power.
  - Name the cost you pay for an always-on box before buying one.
volatility: concept
sources:
  - title: "Stratosphere — LLM performance on Raspberry Pi 5"
    url: https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html
  - title: "Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard"
    url: https://github.com/geerlingguy/ai-benchmarks
last_verified: "2026-09-30"
---

# 03.1 · Choose the host

The laptop on your desk is enough to build and learn the whole stack. It is not enough to be
*always* available, and the gap between those two things is where most of the friction in a home AI
setup comes from: lid closed, machine asleep, a voice command that only works when you happen to be
sitting in front of it. This lesson is about deciding where the stack lives, and about knowing what
you give up either way.

## Why it matters

Every decision later in the course depends on this one. A Raspberry Pi 5 with 8 GB forces a 1B
model, forces Speech-to-Phrase over Whisper, and forces short context — and each of those is fine,
as long as you chose them on purpose. A 32 GB desktop with dual-channel memory gives you a 7–8B
model, but it costs 40–70 watts to sit idle, which is roughly 300–600 kWh a year and a fan you can
hear at night.

The mistake is not choosing a small machine. The mistake is discovering the constraint in Module 8,
after you have built a pipeline around a model that will not fit.

## How it works

Two properties decide almost everything, and neither is the CPU's clock speed.

**Memory bandwidth sets generation speed.** Every new token re-reads the entire model from RAM, so
speed is bounded by how fast the memory subsystem delivers bytes. Dual-channel DDR5-6000 moves about
96 GB/s in theory; a Raspberry Pi 5 moves about 17 GB/s because it is a single-channel design on
purpose. That is the whole story behind the numbers below: an 8B Q4 model is about five times
faster on a desktop than on a Pi 5, and the CPU is barely involved.

**Memory type and channel count decide the ceiling.** Two DIMMs in the right slots are roughly
double one DIMM. A laptop with soldered memory is usually dual-channel already; a desktop with one
stick in one slot is single-channel, and that is the single most common reason a home AI machine
feels broken. `homelab.py doctor` reports this as `memory channels: unknown` on macOS and Windows,
because there is no portable way to ask — on those systems you look up the machine's memory
specification instead.

### The four candidates, honestly

| Machine | Memory bandwidth, about | RAM you can get | Idle power, about | Noise | Good enough for |
|---|---|---|---|---|---|
| Raspberry Pi 5, 8 GB | ~17 GB/s | 8 GB, single channel | ~3 W | none (add a fan case and it is not) | 1–3B chat, Speech-to-Phrase, typed Assist |
| Intel N100 / N150 mini PC | ~25–30 GB/s | 16 GB, single channel | ~6–10 W | fan, often audible | 3B chat, Whisper base, most of the course |
| Old desktop, 8–12th gen, dual-channel | ~50–100 GB/s | 32–64 GB, dual channel | ~25–45 W | quiet with a decent case | 7–8B chat, Whisper small, the full stack |
| Laptop, 16 GB, dual-channel | ~40–90 GB/s | 16 GB | ~8–15 W closed-lid, but it sleeps | usually silent | the whole course, while it is awake |

Cited generation speeds, to give the bandwidth column some meaning (all from
[the benchmark references](../../references/benchmarks.md), and all on somebody else's hardware):

| Model | Raspberry Pi 5 | Intel N150 | Ryzen mainboard |
|---|---|---|---|
| Llama 3.2 3B | 4.6–4.9 tok/s | 9.1 tok/s | 13.1 tok/s |
| Llama 3.2 1B | 11.2 tok/s | — | — |

The same 3B model, three machines, a factor of almost three. Read that as a lesson about memory, not
about chips: when you next see a benchmark on someone else's machine, ask what their memory does
before you ask what their processor does.

## Show me

The decision this course makes for you, and why:

- **Build on the machine you already have.** Module 3 to Module 10 work entirely on a laptop. A
  second machine bought before you have built anything is a purchase made on someone else's
  benchmark.
- **Move to an always-on host in Module 12, not now**, and only after you know what you actually
  need to be always-on. For most people that is Home Assistant plus the voice pipeline, not chat.
- **If you already have a spare desktop, use it now.** The only cost is setting it up.

The one question worth answering before you buy anything: *is my current machine's memory
dual-channel, and how fast?* Find the memory specification for your exact model, and write it in
your [measure-yours table](../../templates/measure-yours.md). If it is single-channel, the cheapest
possible upgrade is a second matching DIMM, and it is worth more than any other upgrade in this
course.

## Try it

Write down your current machine and check it against the table above. Then, if you are curious what
the memory costs you, run the same model at two context lengths:

```bash
# Windows PowerShell
ollama run qwen3:4b --verbose "count from 1 to 50"

# macOS / Linux
ollama run qwen3:4b --verbose "count from 1 to 50"
```

The `--verbose` output ends with a line like `total duration: 12.4s` and an `eval rate`. Now run it
again with a long context and watch the same model get slower:

```bash
# a deliberately heavy prompt: this is what a RAG question looks like
ollama run qwen3:4b --verbose "Summarise the text in detail: <paste about 2000 words here>"
```

Record both `eval rate` numbers in the generation and prompt speed table in
[measure-yours](../../templates/measure-yours.md). The gap between the first-token time and the
per-token rate is the thing the rest of the course is about.

> [!NOTE]
> macOS: `ollama run` behaves the same, and Apple Silicon is genuinely fast because the CPU shares
> the same memory as the GPU with no copy in between. Our macOS steps are **not verified by us** —
> the course has one Windows test machine — so treat the numbers on this page as a model of what to
> expect, not as a prediction for your Mac.

## Break it

Ask for far more memory than the machine has. Give a 16 GB laptop a 32 GB context with an 8B model
loaded and a browser open:

```bash
# Windows PowerShell
ollama run qwen3:4b --verbose "count from 1 to 200" --ctx-size 131072
```

Watch what happens. The process either never starts, or it starts and the machine becomes
unresponsive as the system starts paging. On Windows the symptom is a machine that feels fine until
it is not; on Linux you can watch it happen with `free -h` in a second terminal while the request
runs.

The second way to break it is quieter and much more common: run the stack on a Pi 5 with an 8B
model, because it loads, and it works, and every answer takes fifteen seconds. Nothing errors. It is
just unusable, and there is no error message pointing at the cause.

## Fix it

Size the model to the bandwidth, and the context to the job.

1. If the model does not fit in RAM, it does not go in RAM. Use a smaller model, not a longer wait.
2. Keep the context as small as the work needs. Home chat is usually 4 096; a retrieval-augmented
   question may need 8 192; 131 072 is a research setting, not a home setting.
3. If speed is the problem and the model is already small, the problem is memory channels. That is
   hardware, and no setting fixes it.
4. On an always-on host, set `OLLAMA_KEEP_ALIVE` low so the model unloads when idle, and give the
   container a memory limit so it cannot starve Home Assistant. Module 12 does this properly.

```bash
# Windows PowerShell and macOS/Linux both read this
$env:OLLAMA_KEEP_ALIVE = "5m"
ollama serve
```

## How do I know it works?

- [ ] `python homelab.py doctor` runs and names your tier.
- [ ] You know your machine's RAM speed and whether it is dual-channel, written down, not guessed.
- [ ] You have two `eval rate` numbers in [measure-yours](../../templates/measure-yours.md) from the
      same model: one short prompt, one long prompt.
- [ ] You can say, out loud, which model this machine will run at an acceptable speed — and why.

## Use it when / avoid it

**Use a laptop** while you are learning. It is free, it is already set up, and the sleeps only
matter for the one thing you are not doing yet.

**Use a spare desktop or an N100 mini PC** when you want the stack always-on and your laptop is
already doing something else. The N100 is the sweet spot: real dual-socket-free memory at
single-channel speed, about 10 W idle, small enough to hide, and fast enough for a 3B model and
Whisper base. Home Assistant's own documentation names an Intel N100-class CPU as the bare minimum
for full local Whisper.

**Use a Raspberry Pi 5** when you want something genuinely silent and nearly free to run, and you
are content with 1–3B models. It is a good *voice* machine and a poor *chat* machine, and the
split is worth designing around: Pi for the always-on voice pipeline, a bigger box for chat.

**Avoid buying a dedicated always-on box before Module 12.** You will not yet know whether the thing
that needs to be always-on is chat, or the voice pipeline, or just Home Assistant. And if you are
running two machines, the interesting problem is the one in [44 · Your always-on home](../module-12/lesson-04.md):
how they reach each other safely.

> [!TIP]
> **If you have a GPU.** Nothing in this module requires one, and nothing in the course uses one. If
> your machine happens to have a discrete GPU, llama.cpp can offload some layers to it, which buys
> bandwidth back for the rest — but it also splits the KV cache across a PCIe link, and on most
> consumer cards that is a net loss for a home setup. Measure before you assume it is a win.

## Reflect

1. What is your machine's memory speed and channel count, and where did you find that out? If you
   could not find it, what is the cheapest way to find out for certain?
2. If you added a second matching RAM stick tomorrow, which number in your measure-yours table
   would you expect to change, and which would you expect to stay the same? Why those two?
3. When the laptop is closed and asleep, which of the five things the stack does would you still
   want? That answer is the specification for Module 12.

## Sources

- [Stratosphere — LLM performance on Raspberry Pi 5](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html)
- [Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard](https://github.com/geerlingguy/ai-benchmarks)
- [Home Assistant Voice Preview Edition — hardware requirements](https://www.home-assistant.io/voice-pe/)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)
- [llama.cpp issue #1437 — memory bandwidth and generation speed](https://github.com/ggml-org/llama.cpp/issues/1437)
