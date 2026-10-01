---
id: "01.1"
module: 1
minutes: 12
practice_minutes: 20
prerequisites: ["00.2"]
objectives:
  - Install Ollama on Windows, macOS or Linux and confirm the server is answering on 127.0.0.1.
  - Pull a model sized for your tier, run one question you can check, and read the timing it prints.
  - Prove the answer was produced locally, in three increasingly strong ways.
  - Say what llama.cpp is, why Ollama is the runtime in this course, and why `llama-bench` is
    the measuring instrument instead.
volatility: implementation
sources:
  - title: "Ollama — where models are stored, and how to turn the cloud features off"
    url: https://docs.ollama.com/faq
  - title: "Ollama — context length and the default of 4k on a machine without a GPU"
    url: https://docs.ollama.com/context-length
  - title: "llama.cpp releases — prebuilt binaries and source"
    url: https://github.com/ggml-org/llama.cpp/releases
last_verified: "2026-09-30"
---

# 01.1 · Install Ollama and run your first model

This is the lesson where something happens. You install one program, download a few gigabytes,
type a question, and a model on your own processor writes the answer — in under ten minutes plus
download time, with no account, no API key and no subscription. Then you do the step most courses
skip: you prove that the answer came from your machine, instead of believing it.

## Why it matters

Everything in this course runs on a local model server, and the rest of the material is only
useful if this part is solid. There is a second reason to do it early: a local model you can ask a
question of is the cheapest possible test of whether your machine is fast enough. If the first
answer takes forty seconds, every later design decision is a consequence of that fact, and you
want to know it now rather than after building a pipeline.

The third reason is the one the course is actually about. "It runs on my computer" and "nothing
leaves my house" are two different claims, and a great many home AI projects discover the
difference the day something they did not configure by hand starts making requests. This lesson
ends with a test, not a promise.

## How it works

**Ollama is two things.** A background server — the model runtime — that keeps weights in RAM and
answers requests, and a command-line client that talks to it. The server listens on port 11434 and
binds `127.0.0.1` by default, which is why nothing on your network can reach it unless you ask for
that. The client and the server are the same binary, and the server is started for you when you
install the app on Windows or macOS, or by a systemd unit on Linux.

**Three commands do the whole lesson.**

| Command | What it does |
|---|---|
| `ollama pull <tag>` | Downloads the model into the local store and verifies it |
| `ollama run <tag>` | Loads the model into RAM, opens a chat, streams the answer token by token |
| `ollama list` | Shows what is stored locally, with the size on disk |

Model files live in one directory, and it is worth knowing where: `~/.ollama/models` on macOS,
`/usr/share/ollama/.ollama/models` on Linux, and `C:\Users\<you>\.ollama\models` on Windows. The
`OLLAMA_MODELS` environment variable moves it, which is what you do when the system drive is small
and a second disk is not.

**What happens when you press enter.** If the model is not downloaded, `run` downloads it first. If
it is not in RAM, the runtime loads it — for a 4B model that is a couple of gigabytes read from
disk, and it happens once. Then every token of the answer is produced by your CPU, one at a time,
and streamed to the terminal as it is generated. That is why a good answer arrives word by word:
the model cannot write ahead of its own arithmetic.

**What llama.cpp is, and why this course mostly does not use it.** llama.cpp is the inference
library underneath: it reads GGUF weight files, runs the matrix arithmetic on a CPU, and ships two
tools this course cares about — `llama-server` (an API server, the same OpenAI-shaped interface you
would expect) and `llama-bench` (a benchmark harness that reports prompt and generation throughput
separately). Ollama gives you a friendlier way to do the same job: it picks a quantisation, keeps a
model store, handles the download, and exposes the same HTTP API. So Ollama serves, and
`llama-bench` measures. Module 2 is where the measurement matters, and [08 · Measure prompt speed
and generation speed](../module-02/lesson-03.md) is where you run it.

> [!NOTE]
> macOS: the install is a `.dmg` from the download page, and the same three commands work. Apple
> Silicon Macs are genuinely fast here because the CPU and GPU share one pool of memory, and Ollama
> uses Metal automatically. **None of that is verified by us** — this course has one Windows test
> machine — so treat the macOS steps as a model of what to expect, not a measurement.

## Show me

### Install

```powershell
# Windows: download the installer, run it, then start the app from the Start menu.
# It starts the server for you and puts an icon in the tray.
# Verify:
ollama --version
```

```bash
# macOS: download the .dmg, drag Ollama into Applications, launch it once.
# Verify (not verified by us — one Windows test machine in this course):
ollama --version
```

```bash
# Linux: the official one-line install, which sets up a systemd service
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama --no-pager
ollama --version
```

> [!NOTE]
> Current Ollama builds spell the listing command `ollama ls`; older ones use `ollama list`. Both
> print the same table, so use whichever your version accepts. If `ollama` is "not recognised",
> the command works but the install directory is not on your `PATH` yet — open a new terminal.

### Pull and run, sized to your tier

```bash
# Windows PowerShell, macOS and Linux: the same commands
ollama pull qwen3:4b            # tier A and B, about 2.5 GB
ollama list

# tier C and smaller machines use this instead
ollama pull llama3.2:1b         # about 1.3 GB, the 00.2 recommendation for tier C
```

Then ask something you can check:

```bash
ollama run qwen3:4b "List the first twelve prime numbers, then explain in one sentence what a KV cache is."
```

Two things to notice in the answer: the primes are verifiable by you in ten seconds, and the
explanation is the sort of thing a 4B model is genuinely good at. Small models get easy things
wrong too — ask both `qwen3:4b` and `gemma3:1b` the same question and compare. That difference is
the whole model-selection argument in [04 · Reading a model tag](../module-01/lesson-02.md).

### Prove it is local, in three increasingly strong ways

```bash
# 1. The weights are a file on your disk. A 2.5 GB file cannot arrive per question.
ollama list

# Windows PowerShell
Get-ChildItem "$env:USERPROFILE\.ollama\models" -Recurse -File |
  Sort-Object Length -Descending | Select-Object -First 5 FullName, Length
```

```bash
# Linux / macOS
find ~/.ollama/models -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -5
```

```powershell
# 2. Turn the runtime's optional cloud features off, then restart the server.
$env:OLLAMA_NO_CLOUD = "1"
```

```bash
# macOS / Linux — put it in the environment of the service, then restart
export OLLAMA_NO_CLOUD=1
ollama serve
```

The server's log then contains `Ollama cloud disabled: true`, which is your own evidence rather
than a claim.

```bash
# 3. The test that settles it: turn the Wi-Fi off (or unplug the cable) and ask again.
ollama run qwen3:4b "In one sentence: what is a reverse proxy?"
```

It answers. That is not a proof that the program makes no other outbound connections — update
checks and downloads are different code paths — but it does prove the inference is on your machine,
which is the part people get wrong. The complete version, with the network blocked at the firewall
and every feature tested, is Module 12.

## Try it

One measurement, from your own machine, in about a minute. Ask for a long enough answer that the
timing is meaningful, and add `--verbose` so the runtime prints its own numbers:

```bash
# Windows PowerShell, macOS and Linux: identical
ollama run qwen3:4b --verbose "Explain in about 200 words how a heat pump heats a house."
```

The tail of the output contains an `eval rate` and an `eval count`, and a `total duration`. The
rate is generated tokens per second. Write the three numbers here before you go anywhere else:

```text
Model:            qwen3:4b
Prompt tokens:    __      (count, if printed)
Tokens generated: __
Generation rate:  __ tok/s
Total duration:   __ s
```

Then do the same thing on a smaller model, which is the cheapest quality-versus-speed comparison
you will ever run on your own hardware:

```bash
ollama run gemma3:1b --verbose "Explain in about 200 words how a heat pump heats a house."
```

Two rows in [your measure-yours table](../../templates/measure-yours.md), same machine, same
question, different model. If the 1B is not obviously worse at this prompt, that is a result worth
keeping: you have found a task where the small model is enough, and that is a decision you can
defend later.

## Break it

**Break it with free memory.** On a machine with 16 GB, open a browser with a hundred tabs, start
a video call, and then run a 2.5 GB model with about 1.5 GB actually free. Nothing errors. The
model loads, because the runtime maps the weights from disk, and then every single token has to
come from the page file: generation collapses to a fraction of a token per second, the machine
becomes unresponsive, and the fan runs constantly. The `ollama api` line in
`doctor` is still green the whole time. The symptom is "it works and it is unusable", and the
cause is not the model, the runtime or the network — it is the order the RAM was claimed in.

**Break it with the download.** A model pull is a multi-gigabyte download from the internet, and
it is the only part of this lesson that needs the internet. On a metered or slow connection it
stalls; behind a corporate proxy it fails outright unless `HTTPS_PROXY` is set, because Ollama
pulls over HTTPS only. The failure looks like a hang, not like an error, and the way to tell the
two apart is to check free disk first and then watch the progress output.

**Break the privacy claim by adding a convenience.** The realistic version: a chat interface
installed later, pointed at a hosted model because it was one field to change, answering questions
that came from your own files. Nothing in the interface says "this went to a server 2 000 km
away", which is exactly why the third test above is worth doing before you trust a tool with
anything that matters.

## Fix it

1. **Slow because of paging:** close the memory hogs, or use a smaller model. The check is
   available memory *while the model is loaded*, not the free memory you had before you started.
   [07 · The RAM bill](../module-02/lesson-02.md) is how to budget this properly, and
   `ollama stop <model>` unloads a model and gives the memory straight back.
2. **Pull fails or hangs:** confirm free disk, confirm the connection is not metered, and if you
   are behind a proxy set `HTTPS_PROXY` rather than `HTTP_PROXY` — the latter breaks the local
   API. The [troubleshooting page](../../references/troubleshooting.md) is organised by symptom.
3. **Uncertain where your data went:** set `OLLAMA_NO_CLOUD=1`, restart, confirm
   `Ollama cloud disabled: true` in the log, and re-run the offline test. Record what you did in
   [the measure-yours table](../../templates/measure-yours.md); you will want that record in
   Module 11.
4. **Wrong answers:** before blaming the runtime, check that you are running an instruct model and
   that the context was big enough for the question. Both are the subject of
   [04 · Reading a model tag](../module-01/lesson-02.md) and
   [05 · Settings that change the answer](../module-01/lesson-03.md).

## How do I know it works?

- [ ] `ollama --version` prints a version on this machine.
- [ ] `ollama list` shows a model with a real size in gigabytes, and you can find that file on disk.
- [ ] You have asked one question you can verify the answer to, and the answer was right.
- [ ] You have run the same question with the network off and it still answered.
- [ ] You have a generation rate from `--verbose` written in
      [the measure-yours table](../../templates/measure-yours.md), with the model name and the
      machine name next to it.
- [ ] You re-ran `python homelab.py doctor` and the `ollama api` line now says it is answering.

## Use it when / avoid it

**Use Ollama for everything from here to Module 6.** It is the default runtime in this course
because it removes four chores — choosing a quantisation, finding a download, loading a file,
managing a context — that are not what these modules are about. When a lesson needs a number
rather than a conversation, it uses `llama-bench`.

**Avoid pulling several models "to have them ready".** Each one costs gigabytes on disk and,
while loaded, gigabytes of RAM. Two models loaded at once is a Module 4 topic with a real
trade-off; one model at a time is the right default for the first pass.

> [!TIP]
> **Do it yourself with llama.cpp.** Ollama will not tell you what the hardware did, because it
> makes the choices for you. `llama-server` is the same inference without the convenience layer,
> and it is one command:
>
> ```bash
> llama-server -m models/qwen3-4b-instruct-q4_K_M.gguf --host 127.0.0.1 --port 8080 -c 4096 -t 8 -ngl 0
> ```
>
> The two or three parameters worth playing with: `-c` (context size, the same `num_ctx` you will
> meet in [05 · Settings that change the answer](../module-01/lesson-03.md)), `-t` (threads, which
> is the one that matters for prompt processing), and `-ngl` (how many layers to put on a GPU —
> `0` is pure CPU). Binary releases are on the llama.cpp releases page, and
> `llama-server --help` lists everything else.

> [!NOTE]
> **If you have a GPU.** Nothing in this course needs one and nothing in it assumes one, so you
> can skip this. If your machine happens to have a discrete or integrated GPU, Ollama will use it
> automatically and `ollama ps` will show you what happened: the `PROCESSOR` column reads
> `100% GPU`, `100% CPU`, or a split like `50%/50%`. A split is the interesting case — it means
> some layers are on the card and the rest, plus part of the KV cache, are on the CPU, and the
> data crossing the PCIe link can cost more than it saves. The only honest way to know is to
> measure both: `llama-bench -m <file> -ngl 0` against `llama-bench -m <file> -ngl 99`. If they are
> within a few percent of each other, the GPU bought you nothing on this machine and you can stop
> thinking about it.

## Reflect

1. Which model did you pull, and what size was it on disk compared with the parameter count in its
      name? Where does the difference come from?
2. When you ran the question with the network off, what exactly was still running? Name the
      process, the port and the file.
3. If your machine had 1.5 GB free when you started, at which point in this lesson would you have
      known — and what would you have changed?

## Sources

- [Ollama FAQ — model storage, the default bind address, keep-alive, and disabling the cloud features](https://docs.ollama.com/faq)
- [Ollama — context length and why 4k is the default on a machine without a GPU](https://docs.ollama.com/context-length)
- [llama.cpp releases — prebuilt `llama-server` and `llama-bench`](https://github.com/ggml-org/llama.cpp/releases)
- [Pinned models and licences](../../references/models.md) and [Pinned versions](../../references/versions.md)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)
