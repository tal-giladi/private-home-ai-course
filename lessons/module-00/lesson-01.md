---
id: "00.1"
module: 0
minutes: 10
practice_minutes: 15
prerequisites: []
objectives:
  - Name the three jobs a private home AI stack does, and the one hardware budget they share.
  - Say which hardware tier your machine is in and which of the three things you can drop first.
  - Choose a path through the course (core, voice, safe and always-on) with a time estimate.
  - Explain why "nothing leaves the house" is a claim you test rather than a claim you make.
volatility: concept
sources:
  - title: "Home Assistant — local voice control and pipeline overview"
    url: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
  - title: "Ollama FAQ — does Ollama send my prompts and answers back to ollama.com?"
    url: https://docs.ollama.com/faq
  - title: "Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard"
    url: https://github.com/geerlingguy/ai-benchmarks
last_verified: "2026-09-30"
---

# 00.1 · What a private home AI stack is

A private home AI stack is not a product you buy and it is not a single program. It is three
capabilities sharing one machine, one power supply and one pool of RAM: a chat assistant that runs
on your own processor, question answering over files you own, and a voice assistant that answers in
the room with the router unplugged. Getting all three to feel ordinary is the whole project, and
the hard part is not the model — it is that they compete for the same gigabytes.

## Why it matters

Most people arrive at "I want AI at home" with one use case in mind and discover three constraints
they did not know they had. The first is memory. A model is a few gigabytes of weights that must
sit in RAM to answer, plus a cache that grows with every token of context, plus the chat
interface, plus Home Assistant, plus your browser. On a 16 GB laptop that budget is real and it is
the subject of [07 · The RAM bill](../module-02/lesson-02.md).

The second is that "private" is a claim about bytes, not about intentions. A chat window that
looks local can be one misconfigured environment variable away from sending your conversations to
a hosted API. The vendor of the runtime has to be asked, and their answer has to be checked by you.

The third is that a CPU is enough, but only for particular sizes of model. Nobody is going to run a
70B model at talking speed on a machine with no graphics card. What a CPU *can* do comfortably is
the middle of the range, and knowing where that boundary sits on your own hardware is what this
course teaches you to calculate rather than guess.

## How it works

![The private home AI stack: one box, a model server, a chat interface, a vector store, and a voice pipeline that only reach each other inside it](../../assets/stack-map.svg)

### The three jobs

| Job | What the user does | What has to be true | Which module |
|---|---|---|---|
| Local chat | Types questions, gets streamed answers | A model fits in RAM and answers at a readable rate | Modules 1–4 |
| Answers over your own files | Asks about a manual, a recipe, a warranty | The files are chunked, embedded and searched locally, and the answer cites them | Module 6 (optional) |
| Voice assistant | Speaks in the kitchen, a light turns on | Speech-to-text, an intent or a model, and speech out, all inside the house | Modules 7–10 |

One box, one RAM budget. That single sentence is the design constraint the whole course respects.
Every extra service you start is a claim on the memory that the model wanted.

### The three hardware tiers

| Tier | Example machine | RAM | Realistic chat model | Voice |
|---|---|---|---|---|
| A | Any 2019+ x86 or Apple Silicon laptop | 16 GB | 3–4B, quantised | Whisper base/small + Piper |
| B | Desktop or mini PC, dual-channel | 32 GB | 7–8B, quantised | Whisper small + Piper |
| C | Raspberry Pi 5 8 GB, Intel N100 mini PC | 8–16 GB | 1–3B | Speech-to-Phrase, or Whisper tiny/base |

`python homelab.py doctor` decides which of these you are in, and
[02 · Find your tier with homelab doctor](../module-00/lesson-02.md) is five minutes long. A GPU is
optional everywhere in this course: no lab needs one and no success criterion assumes one.

### What a CPU can and cannot do

Can: a 1B model answering at double-digit tokens per second on a Pi 5 (Gemma 3 1B, 11.5 tok/s,
1.4 GB RAM, [Stratosphere's Pi 5 study](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html));
a 3B model at 13.1 tok/s on a Framework Ryzen mainboard
([Geerling's ai-benchmarks](https://github.com/geerlingguy/ai-benchmarks)); embeddings; small
speech-to-text; an always-on assistant that listens for a wake word all night.

Cannot: a 7B model on a Pi 5 at a rate you would call conversation. Llama 3.2 3B on that same Pi 5
manages 4.6–4.9 tok/s (Stratosphere, Geerling) — 4B runs, 8B does not, 70B is not a home project.
Cannot train or fine-tune anything. Cannot do 24/7 voice on 8 GB with a 7B brain.

### "No cloud" is a test, not a claim

The interesting number is not the model's quality, it is the number of packets that leave the
machine while you are not looking. Ollama's own FAQ says local prompts are not sent back to
ollama.com — that is the vendor's statement, and the right response to a vendor statement about
your data is to check it. Ollama also now ships optional cloud models, and a documented way to
switch the feature off: `OLLAMA_NO_CLOUD=1`, or `disable_ollama_cloud` in `~/.ollama/server.json`,
after which the server's own log line reads `Ollama cloud disabled: true`. The full proof —
unplug the uplink and show that every feature still works — is Module 12, and the glossary tracks
it as *Prove there is no cloud*. For now the claim is unproven, and this course treats it that
way.

## Show me

The course is 13 modules in four parts, and you do not have to finish all of it.

| Path | Modules | Needs | Time |
|---|---|---|---|
| Core — private assistant | M0–M6 | A tier A or B machine | ~10–12 h |
| Voice and Home Assistant | M7–M10 | The same machine and a microphone | +8–10 h |
| Safe and always-on | M11–M12 + capstone | Optionally a second always-on host | +6–8 h |

Part 1, the three modules you are in now, exists because everything after it assumes you can
start a model, read a model name, and say whether a 4B or an 8B fits your machine. Module 6 (your
own files, privately) is the one optional module: skipping it costs you the voice-by-voice lesson
that depends on it and one criterion in the capstone. Everything else in the course stands without
it, and Module 10's fallback design — fixed intents first, the model second — is the safer design
anyway.

If you read nothing else in this course, read this: **the model is the cheapest part to change and
the hardest part to get right.** Measure first, then choose.

## Try it

No installation needed. Write down your own answers to the three questions a stack has to answer,
and then go and read what your machine actually has.

| Question | Your answer | Where you will prove it |
|---|---|---|
| Which of the three jobs do I need first? | | Module 4, 6 or 7 |
| What is the slowest acceptable answer for it? | | [09 · Pick the largest model that meets your target](../module-02/lesson-04.md) |
| What must never leave the house? | | Module 12, *Prove there is no cloud* |

Then read your own memory, straight from the operating system, with no course tooling involved:

```powershell
# Windows PowerShell: installed RAM, and the speed of each memory module
Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed, Manufacturer
```

```bash
# Linux: total, used, available — and how many memory modules the board reports
free -h
sudo dmidecode -t memory | grep -E "Size|Speed"
```

```bash
# macOS — not verified by us; the course has one Windows test machine
system_profiler SPHardwareDataType
```

Write the two numbers — total RAM, and how many modules — into your
[measure-yours table](../../templates/measure-yours.md). The speed of the modules matters as much
as the total, and the number of modules decides whether your machine has one memory channel or two,
which is the single biggest speed lever in [06 · Memory bandwidth sets your
speed](../module-02/lesson-01.md).

## Break it

There are two ways this stack fails before you have written a line of code, and neither produces an
error message.

**The privacy claim breaks silently.** You install a chat interface, you connect it to a model
server, and it works. Three weeks later you are pasting a scanned employment contract into it. The
question "is this actually local?" has no answer in the interface itself — it is answered by the
network, and you have to go looking. A claim you did not test is not a property of your system; it
is a hope.

**The availability claim breaks at the first lid.** A laptop-based stack is excellent while you are
sitting at it and absent when it matters: the lid is closed, the machine is asleep, and the voice
assistant in the other room is a service that is not running. This is the failure that decides
whether Module 12 needs a second box.

A third break is the quiet one: starting all three jobs at once on a 16 GB machine and finding that
the model, the voice services and the browser together leave nothing. Nothing reports a failure; the
machine is simply slow, and every part of the stack looks broken for a reason that is really one
thing — [07 · The RAM bill](../module-02/lesson-02.md).

## Fix it

Turn each claim into a check you can run, and keep the checks:

1. **"The answer comes from this machine."** Find the model's file on your disk. A 2.5 GB file
   cannot be fetched per question, so its existence settles the question of where the weights come
   from. [03 · Install Ollama and run your first model](../module-01/lesson-01.md) makes you do
   this in the first ten minutes.
2. **"Nothing leaves the house."** Block outbound traffic for the runtime, then use the stack. If a
   feature stops working, you have found the feature that was never local. Module 12 does this
   properly, for every service at once.
3. **"It is there when I need it."** Decide now whether that means "when I am at the laptop" or
   "when I am not", because the second one is the whole of Module 12 and needs different hardware.

Until all three are checks rather than beliefs, treat the stack as a prototype. That is not a
failure; that is the correct amount of confidence for a system that is three services and one
power socket.

## How do I know it works?

- [ ] You can name the three jobs and which one you are building first, in one sentence each.
- [ ] You know your total RAM, your memory module speed, and how many modules you have, read from
      the operating system rather than remembered.
- [ ] You have picked a path and written down its time estimate next to your own free time.
- [ ] You can state, in one sentence, what evidence would convince you that nothing leaves the
      house — and you know that you have not collected it yet.

## Use it when / avoid it

**Build the whole thing on the machine you already own.** It is free, it is already configured, and
the measurements you take on it are the measurements that will size everything else. The one thing
it cannot do is stay awake with the lid closed.

**Reach for a second, always-on host when one of these is true**: you want the voice assistant to
answer from another room, the machine you develop on is not the machine that lives in your hallway,
or you want the stack to survive a reboot you did not plan. Decide that in Module 12 with real
numbers, not in week one with a shopping list.

**Avoid starting with retrieval.** "Ask my documents anything" is the most compelling demo and the
most demanding workload, because every question ships a few thousand tokens of prompt through a CPU
that is also the thing generating the answer.
[09 · Pick the largest model that meets your target](../module-02/lesson-04.md) is where that cost
first becomes visible. A 3–4B chat model that answers in four seconds is a better first project
than a retrieval system that takes a minute to say nothing useful.

**Avoid hardware shopping before Module 2.** The cheapest upgrade to a slow home AI machine is
almost never a faster processor; it is the second memory module.
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md) has the arithmetic.

## Reflect

1. Which of your three jobs has the tightest latency budget, and where did you get that number —
      from a product you use, or from a guess?
2. If your machine turns out to have one memory module in one slot, what changes about your plan
      for the rest of the course, and what does not?
3. Name one thing in your current setup that is already sending data off the machine. You will
      need a written answer to that question again in Module 11.

## Sources

- [Home Assistant — local voice control and pipeline overview](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- [Ollama FAQ — is your data sent back, and how do you turn the cloud features off?](https://docs.ollama.com/faq)
- [Stratosphere — LLM performance on Raspberry Pi 5](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html)
- [Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard](https://github.com/geerlingguy/ai-benchmarks)
- [Measure-yours tables](../../templates/measure-yours.md) and the [Glossary](../../glossary.md)
