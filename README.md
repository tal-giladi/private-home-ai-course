# Private Home AI: A CPU-only Home Lab

Turn an ordinary 16–32 GB computer into a private home AI stack: a local chat assistant, search and question answering over your own files, and an offline voice assistant that controls Home Assistant — with no cloud account, no subscription and no GPU. Every module ends with something you can see or hear working on your own machine within minutes, and every performance number is measured or cited, never promised.

## What this course is

You will build one stack on one box and grow it module by module: a model server, a chat UI, a
vector store over your own files, a Home Assistant instance with demo entities, and a fully local
voice pipeline over the Wyoming protocol. The same RAM budget has to cover all of it, so the course
spends as much time on *sizing* as on building.

The course is honest about what CPUs can and cannot do. You will learn to predict generation speed
from memory bandwidth, measure it on your own machine, pick the largest model that still meets your
speed target, keep voice latency inside a budget, and run the whole thing safely on a home network
where one careless port forward exposes an unauthenticated model server to the internet.

## Who it is for

A developer, IT person, maker or Home Assistant hobbyist who is comfortable in a terminal and wants
AI at home without sending their data, voice or files to a cloud service.

**You are assumed to know:** `cd`, editing a file, running a command, installing software, and what
a router and an IP address are.

**You are not assumed to know:** machine learning, Docker (there is an on-ramp in
[Module 3](lessons/module-03/lesson-02.md)), Home Assistant, or anything about smart-home hardware —
the voice path runs on demo entities and your laptop microphone, and every voice lab has a
text-only route.

## What you need

| | |
|---|---|
| Computer | Any 2019+ x86 or Apple Silicon laptop, or a desktop or mini PC with 16–32 GB RAM |
| GPU | Not required, not used by any lab. Each module has an "If you have a GPU" note. |
| Disk | 25 GB free is comfortable; models are 1–5 GB each and there is more than one. |
| Network | Needed to download software and models once. After that the whole stack runs offline. |
| Purchases | None. An always-on mini PC and a Voice Preview Edition are mentioned as optional upgrades; no lab or capstone criterion needs either. |

Tier A (16 GB) runs 1–4B chat models comfortably. Tier B (32 GB) runs 7–8B. A Raspberry Pi 5 or an
Intel N100 mini PC works on the reduced path. [Lesson 02](lessons/module-00/lesson-02.md) prints
which tier you are on and which model to start with.

## The three paths

| Path | Modules | Needs | Time |
|---|---|---|---|
| Core: private assistant | 0–6 | A tier A or B machine | ~10–12 h |
| Voice and Home Assistant | 7–10 | The same machine and any microphone (a laptop's is fine) | +8–10 h |
| Safe and always-on | 11–12 + capstone | The same machine; optionally a second always-on host | +6–8 h |

Module 6 (your own files) is optional: skipping it removes one lesson in Module 10 and one capstone
criterion, and nothing else.

## What the course will not promise

It will not promise that a 7B model feels fast on a laptop with one RAM stick, that a small model
handles tool calls without misfires, or that opening a port is safe. Where a number is a goal rather
than a fact, the lesson says so and gives you the command to measure it yourself.

## How the course is laid out

- [Glossary](glossary.md) — every term, linked to the lesson that introduces it.
- [Pinned models and licences](references/models.md) — the default model list with sizes, licences
  and where each file comes from.
- [Pinned versions](references/versions.md) — the exact image tags the labs use.
- [Benchmark numbers and where they come from](references/benchmarks.md) — every cited CPU number
  with the machine it was measured on.
- [Troubleshooting](references/troubleshooting.md) — Windows, macOS and Linux fixes, and the common
  "it is slow" / "it cannot connect" cases.
- [Source list](references/sources.md) — every document the course leans on.
- Templates — the fill-in tables the labs ask you to complete.

## Labs

Each module has its own folder under `labs/module-NN/`, offered as that module's download, and
`labs/common/` is added to every one. The stack is a single Docker Compose file that grows through
the course with profiles (`core`, `rag`, `voice`, `secure`), so you never rebuild from scratch.

Two commands drive most of the course:

```bash
python homelab.py doctor     # what machine is this, which tier, which model to start with
python homelab.py bench      # prompt and generation speed, peak RAM, voice timings
```

## Accessibility

Every voice lab works from typed commands or from recorded WAV files, so the whole course is
completable without speaking or using a microphone. The capstone rubric accepts a typed-command
pipeline plus a text-to-speech output check. Diagrams have alt text, transcripts ship with the sample
audio, and the sizing simulation is keyboard-operable and readable at 360 px.

## Honest measurement

Performance figures in this course come in one of three forms, always labelled: a **cited** number
with a link and the machine it was measured on, a number **we measured** on a named test machine, or
a number **you measure** with a command in the lesson. The course never presents a speed it has not
measured or cited, and never promises a target it has not verified.

---

The course plan this was built from, with the research, hardware reality checks, risk analysis and
build phases, is in `plan.md`.
