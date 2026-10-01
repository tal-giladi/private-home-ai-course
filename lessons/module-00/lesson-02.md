---
id: "00.2"
module: 0
minutes: 8
practice_minutes: 10
prerequisites: ["00.1"]
objectives:
  - Run `python homelab.py doctor` and read every line of its output without guessing.
  - Name your tier from the tool's own rules and say which number decided it.
  - Pick a first model and a first context size for your machine, and write both down.
  - Recognise the port line that means a service is reachable from your network, and the one that
    means nothing is listening.
volatility: implementation
sources:
  - title: "Ollama FAQ — context size, keep-alive, and the default bind address"
    url: https://docs.ollama.com/faq
  - title: "Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard"
    url: https://github.com/geerlingguy/ai-benchmarks
last_verified: "2026-09-30"
---

# 00.2 · Find your tier with homelab doctor

One command, about five minutes, and it ends with two sentences that decide the rest of the
course: the tier your machine falls into and the model you should pull first. What matters more
than the answer is that the tool shows its working — every number it prints comes from your
machine, and the tier is calculated by rules you can read and check yourself. No model is
downloaded, nothing is installed, and nothing on your machine is changed.

## Why it matters

The most expensive mistake in a home AI project is picking a model before knowing what the machine
can hold, and the most common version of that mistake is picking one from a benchmark somebody ran
on a desktop. This lesson removes the guesswork in one step: the tier is a function of total RAM and
core count, the recommended model follows from the tier, and the ports section tells you whether
you have already exposed something you did not mean to.

It also fixes your vocabulary. "Tier A" means a 16 GB laptop, not "a good computer", and from
Module 1 onwards the course uses that word instead of "probably fine".

## How it works

`doctor` is a read-only script in the course's shared lab folder. It uses only the Python standard
library, so there is nothing to install, and it prints five sections. This is what a real report
looks like, line by line — the values are from one test machine, the structure is what you get.

```text
==========================================================================
homelab doctor - WORKSTATION-7
==========================================================================

System
------
  ok    operating system       Windows 10 10.0.19045
  ok    architecture           AMD64
  ok    python                 3.12.7 (needs 3.10+)
  ok    cpu                    AMD Ryzen 7 5825U with Radeon Graphics
  ok    logical cores          16 logical

Memory
-------
  ok    total ram              32.0 GB
  ok    available ram          18.4 GB free right now
  WARN  memory channels        unknown
  ok    free disk (home)       212.6 GB

Tools
-----
  ok    docker + compose       server 27.3.1, compose v2.29.7
  ok    ollama cli             ollama version is 0.35.0
  --    llama-bench            not on PATH - optional, doctor still works
  ok    microphone             2 recording device(s) reported by the audio driver

Services and ports
------------------
  ok    ollama api             answering on 127.0.0.1:11434
  ok    port 11434 (Ollama)    loopback only - not reachable by other devices
  --    port 8080 (Open WebUI) not listening
  --    port 8123 (Home Assistant) not listening
  --    port 6333 (Qdrant)     not listening
  --    port 10200 (Wyoming wake word) not listening
  --    port 10300 (Wyoming speech-to-text) not listening
  --    port 10301 (Wyoming text-to-speech) not listening
  --    port 10302 (Wyoming satellite) not listening
  --    port 10303 (Wyoming speech-to-phrase) not listening

Tier and recommendation
-----------------------
  ok    tier                   B
  ok    recommended first model qwen3:4b
  ok    why                    32 GB class: you can try a 7-8B if your bandwidth
                               supports it. Start at 4B and measure before you go bigger.

  Numbers here come from this machine, not from the course. See references/benchmarks.md.
```

Nothing above is a measurement by the course: the values are a worked example so you can recognise
the shape of the report, and your own run will name your machine, your RAM and your tools.

### What each line tells you, and what to do with it

| Line | Read it as | Action if it is wrong |
|---|---|---|
| `operating system`, `architecture`, `python` | Which platform the labs will run on | The report prints `needs 3.10+`; install a newer Python if it complains |
| `cpu` | The actual processor string, not a guess | If it says `could not read the CPU model`, read it from the OS yourself |
| `logical cores` | Hyperthreaded count, which is **not** the number of physical cores | Count physical cores: Linux `lscpu`, Windows `Get-CimInstance Win32_Processor` |
| `total ram` | The single number the tier is calculated from | — |
| `available ram` | What is free *right now*; it does not affect the tier | Close things before you trust any memory reading |
| `memory channels` | `unknown` on Windows and macOS **by design** — there is no portable way to ask | Look up your model's memory specification; this is the biggest speed lever in the course |
| `free disk (home)` | Where model files will land, in gigabytes | Below about 10 GB is a `WARN`; a 2.5 GB model plus a spare copy is the minimum |
| `docker + compose` | Whether Modules 3+ are possible at all | Start Docker Desktop; `daemon is not answering` means the CLI is installed and stopped |
| `ollama cli` | Installed and on `PATH` | [03 · Install Ollama](../module-01/lesson-01.md) |
| `llama-bench` | Optional; used in Module 2 to cross-check `bench` | Install later, or skip it — `bench` is enough |
| `microphone` | Whether Module 7+ can capture audio | Headset or built-in mic both count; a `WARN` on Linux usually means no PipeWire or PulseAudio |
| `ollama api` | Whether a model server is answering locally | `not running (fine before Module 1)` is the expected line today |
| the nine port lines | Which stack services exist, and whether they are reachable from other devices | See the next paragraph — this is the security-relevant part |
| `tier`, `recommended first model`, `why` | The output you came for | Read `why` before you disagree with it |

### The port lines, which are the ones that matter

For every port the course uses, `doctor` asks two questions: is anything listening on
`127.0.0.1`, and can a connection to this machine's LAN address reach the same port? The answers
print as one of three lines.

| Line | Meaning | Worry? |
|---|---|---|
| `loopback only - not reachable by other devices` | The service is bound to `127.0.0.1` | No. This is the correct state |
| `reachable from your router; this is the one to fix` | Bound to every interface, which is what `0.0.0.0` means | Yes — every device on your Wi-Fi can reach it |
| `not listening` | The service is not running | No, not yet |

> [!IMPORTANT]
> `0.0.0.0` is not a special address that the service connects *to*. It is the bind address that
> means "listen on every interface this machine has", including the one your router can reach. A
> service bound to `0.0.0.0` is a service on your network, not a service on your computer. The
> model server's API has no authentication at all, so this is the first line of `doctor` worth
> reading twice.

### The tier rules, spelled out

The tier is calculated from **total** RAM and **physical** core count, and nothing else — not your
storage, not your processor's clock, and not how much RAM happens to be free at the moment.

| Condition | Tier | First model | What it means |
|---|---|---|---|
| ≥ 24 GB and ≥ 8 cores | B | `qwen3:4b` | You can try 7–8B if your bandwidth supports it; measure first |
| ≥ 12 GB | A | `qwen3:4b` | 3–4B chat plus the voice services, with headroom; an 8B runs and is slow |
| ≥ 6 GB | C | `llama3.2:1b` | Stay small; use Speech-to-Phrase or Whisper tiny, and run one thing at a time |
| below 6 GB | C- | `gemma3:1b` | The course still works, with a 1B model and nothing else loaded at once |

## Show me

The three commands, from the course's lab folder. Run them from inside `labs/common`, because
`bench` later on looks for `.env` in the working directory.

```bash
# Windows PowerShell, macOS and Linux all read the same
cd labs/common
python homelab.py doctor
```

```bash
# the same report plus every value it collected, as JSON
python homelab.py doctor --verbose
```

If `python` is not found, use `python3` on Linux and macOS, or `py -3` on Windows.

The report ends with a footer that is the honest contract of the whole course: *numbers here come
from this machine, not from the course*. Every other number you will meet in
[the benchmark reference](../../references/benchmarks.md) is somebody else's machine, labelled with
its name.

## Try it

Run `doctor` and fill this in. It takes five minutes and it is the input to Module 2.

```text
Tier reported:                      __
Total RAM:                          __
Physical cores:                     __
Memory module speed (from the spec): __
Number of memory modules:           __
Free disk in your home folder:      __
Recommended first model:            __
My context size for this course:    __
```

Then do the one cross-check that is worth doing today, because it is the check people skip and it is
the difference between "local" and "a belief": confirm the model server is bound to loopback by
hand.

```bash
# Windows PowerShell: which address is port 11434 listening on?
Get-NetTCPConnection -LocalPort 11434 -State Listen | Select-Object LocalAddress, LocalPort

# Linux / macOS
ss -ltnp | grep 11434        # or: netstat -an | grep 11434
```

`127.0.0.1:11434` and nothing else is what you want to see. Record the result in
[your measure-yours table](../../templates/measure-yours.md) next to the tier.

## Break it

**Break the tier rule with a loaded machine.** Load a model, open twenty browser tabs, start Home
Assistant, and run `doctor` again. `available ram` will drop and `total ram` will not, so the tier
is unchanged. That is deliberate and it is also the trap: a machine that reports tier A while
running out of memory is a machine where a 7B model "fits" and the system starts paging instead.
The tier is about what the hardware has, not what is free. The RAM bill in
[07 · The RAM bill](../module-02/lesson-02.md) is where the two numbers meet.

**Break the port check by publishing something.** Start a container with a published port, or set
`OLLAMA_HOST=0.0.0.0` and restart the runtime, and the `ollama api` line changes from
`loopback only` to `reachable from your router; this is the one to fix`. Nothing else in the
report changes, nothing crashes, and the only symptom is that line. This is exactly why the line
exists.

> [!CAUTION]
> If `doctor` reports a routable port, treat it as an exposure until you have looked at it. On your
> own network today it means every phone, laptop and television can reach that service; if anything
> ever forwards that port, it is on the internet. The [troubleshooting
> page](../../references/troubleshooting.md) lists the symptoms, and Module 11 is the lesson that
> designs this properly.

**Break the microphone line without a microphone.** Unplug your headset, or run `doctor` on a
machine with no audio input device at all. The line goes to `WARN` and tells you which tool it
tried (`pactl`, `wpctl`, or the Windows audio driver). It is a `WARN` and not a `FAIL` because
every voice lab in this course also works from a WAV file, so a missing microphone costs you
convenience and not the path.

## Fix it

1. **Tier too low for what you want?** Do not buy anything yet. Confirm the number is the machine's
   *total* RAM and that you read the spec sheet for the right machine. Then read the tier C notes
   in each lesson — the course is written so a tier C machine finishes it, with smaller models.
2. **`memory channels: unknown`?** This is expected on Windows and macOS, not a failure. Look up
   the memory specification for your exact model, count the modules, and record both. One module
   in one slot means one memory channel, and that roughly halves generation speed — see
   [06 · Memory bandwidth sets your speed](../module-02/lesson-01.md).
3. **Free disk below about 10 GB?** Model files are large and they are not optional. Free space
   before the first `ollama pull`, not after it fails.
4. **A port is reachable from your network?** Find the bind address and put it back to loopback:

   ```bash
   # macOS / Linux
   unset OLLAMA_HOST && ollama serve
   ```

   ```powershell
   # Windows PowerShell — for this session only
   $env:OLLAMA_HOST = "127.0.0.1:11434"
   ```

   Then re-run `python homelab.py doctor` and confirm the line says `loopback only`. If the port
   belongs to a container, the fix is in the compose file, not on the host, and Module 3 is where
   that file is built — with no published port on the model server at all.
5. **`docker + compose` failing?** Nothing in Modules 0–2 needs Docker. Note it and install Docker
   Desktop when Module 3 asks for it.

## How do I know it works?

- [ ] `python homelab.py doctor` runs to the end and you have read every line, not just the tier.
- [ ] You can say which two numbers produced your tier, and what the next tier up would need.
- [ ] Your memory module speed and module count are in
      [the measure-yours table](../../templates/measure-yours.md), from the spec sheet and not from
      memory.
- [ ] You know whether port 11434 is on loopback, and how you checked.
- [ ] You have written down your first model, and you know which file size that means on disk.

## Use it when / avoid it

**Use `doctor` on day one, and again whenever something changes** — after you install a second
memory module, after you install Ollama, after Docker starts misbehaving, and before any
"it is slow" conversation. It takes seconds, it changes nothing, and it ends with a line that
names the most likely cause.

**Read the tier as a budget, not a verdict.** Tier A does not mean "a 4B will feel fast"; it means
"a 4B fits with room for the rest of the stack". The speed is a separate measurement, and
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md) is where you predict it and
Module 2 is where you find out.

**Ignore the parts that do not apply yet.** `llama-bench: not on PATH` and
`ollama api: not running` are both normal before Module 1, and `port 8123: not listening` is normal
until Module 7. The script marks missing things as informational rather than failing, and you
should do the same with them.

**Avoid treating "tier A" as a reason to skip the measurement.** The tier comes from RAM and cores;
speed comes from memory bandwidth, which `doctor` cannot see on your operating system. That gap is
the subject of [Module 2](../module-02/lesson-01.md), and it is where the useful surprise lives.

## Reflect

1. Which two numbers decided your tier, and how much RAM would you need to move up one tier?
2. If your machine has one memory module in one slot, what would you expect to change the day you
   add a second one, and what would not?
3. Which line in the report did you skim, and what would you have missed by skimming it?

## Sources

- [Shared lab code — the `doctor` and `bench` commands](../../labs/common/README.md)
- [Ollama FAQ — context size, keep-alive, and the default bind address](https://docs.ollama.com/faq)
- [Troubleshooting by symptom](../../references/troubleshooting.md)
- [Pinned models and licences](../../references/models.md) and [the model tag explained](../module-01/lesson-02.md)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)
