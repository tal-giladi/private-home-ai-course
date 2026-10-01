---
id: "12.1"
module: 12
minutes: 15
practice_minutes: 30
prerequisites: ["04.2", "08.4", "11.2"]
objectives:
  - >-
    Set a memory limit per service so the total leaves room for the operating system, and explain
    what a limit does to a service that exceeds it.
  - >-
    Choose a keep-alive policy per job so a voice command never pays for a model load, and know the
    RAM that policy costs.
  - Measure idle memory and idle power on your own machine, and set up restarts, health checks and
    log rotation so nothing has to be watched by hand.
volatility: implementation
sources:
  - title: "Ollama FAQ — keep-alive, context size and running multiple models"
    url: https://docs.ollama.com/faq
  - title: "Docker — resource constraints and restart policies"
    url: https://docs.docker.com/engine/containers/resource_constraints/
  - title: "Docker — logging drivers and log rotation"
    url: https://docs.docker.com/engine/logging/configure/
  - title: "Docker Compose file reference — restart, healthcheck, logging, resources"
    url: https://docs.docker.com/reference/compose-file/services/
last_verified: "2026-09-30"
---

# 12.1 · Always-on without starving the voice pipeline

An always-on stack has one job that a stack you start by hand never has: being the right shape when
nobody is looking at it. Idle memory that never comes down, logs that fill a disk at 3 a.m., a chat
generation that steals the memory bandwidth your voice pipeline needs — these are the failures that
only show up once you have stopped watching.

## Why it matters

The tension is real and it is specific. A spoken command has a latency budget — the course aims for
under 2 s for a built-in intent and under 5 s with the model fallback — and every millisecond of that
is spent waiting for CPU that somebody else is using. Meanwhile a chat generation is bandwidth-bound
by design: it re-reads the model's weights for every token, and it will happily use every thread
while it does.

So the same machine has two demands that pull in opposite directions: keep the model resident so
voice is instant, and let the machine go quiet so a machine sitting in a cupboard is not burning
power and RAM forever. Almost every setting in this lesson is a dial between those two, and the
right answer is a policy you write down rather than a default you inherit.

> [!IMPORTANT]
> The measurement spike has not run yet, so this module contains no figures we produced. Every table
> with a number in it is either a default that is already in
> [`labs/common/compose.yaml`](../../labs/common/compose.yaml), a limit you are about to choose
> yourself, or a cell waiting for your own measurement. The tables in
> [measure yours](../../templates/measure-yours.md) are blank on purpose.

## How it works

### The memory budget, added up rather than guessed

Every service in the stack has a limit, and the defaults in `.env.example` sum to more than a
16 GB machine has:

| Service | Default limit | `.env` variable |
|---|---|---|
| `ollama` | 12 GB | `OLLAMA_MEMORY_LIMIT` |
| `open-webui` | 2 GB | `WEBUI_MEMORY_LIMIT` |
| `homeassistant` | 2 GB | `HA_MEMORY_LIMIT` |
| `wyoming-whisper` | 2 GB | `WHISPER_MEMORY_LIMIT` |
| `wyoming-piper` | 1 GB | `PIPER_MEMORY_LIMIT` |
| `qdrant` (optional) | 1 GB | `QDRANT_MEMORY_LIMIT` |
| **Total** | **20 GB** | — |

On a 32 GB machine that is a budget. On a 16 GB machine it is a plan to be killed by the kernel. The
numbers `.env.example` suggests for tier A — 7, 1, 1, 1, 512m — come to about 10.5 GB, which leaves
room for the operating system, the Docker VM on Windows, and a browser.

A limit is a ceiling, not an allocation. The container may use far less; the ceiling exists so that
the failure is *this service stops* rather than *the whole machine swaps*. The cost of a ceiling being
too low is a container killed from outside, which shows up in `docker compose ps` as an exit code
and leaves almost nothing in the application's own log.

### Keep-alive, and the two jobs that want different things

`OLLAMA_KEEP_ALIVE` is how long the server holds a model in memory after the last request. It is the
single most consequential setting in the file for an always-on box, because it sets both halves of
the trade:

| Policy | Chat experience | Voice experience | RAM held when idle |
|---|---|---|---|
| `0` (unload immediately) | Every message pays a model load | Every command pays a model load | Almost nothing |
| `5m` (the course default) | Second message is instant | A command after 5 minutes idle pays a load | Nothing after 5 minutes |
| `-1` (never unload) | Always instant | Always instant | The model, forever |
| Two models resident (`OLLAMA_MAX_LOADED_MODELS=2`) | Both jobs instant | Both jobs instant | Two models, always |

The default `5m` is a compromise chosen for a laptop: long enough that a conversation has no pauses,
short enough that the machine returns to idle between uses.

The better answer for a box that is genuinely always-on, and the one the course's own defaults
already encode, is this line in `.env`:

```dotenv
CHAT_MODEL=qwen3:4b
TOOL_MODEL=qwen3:4b
```

**The chat model and the tool model are the same model.** There is no swap to pay for, so the voice
pipeline can never be starved by an eviction, whatever the keep-alive is. If you decide you need a
different model for tool calling, then you have created a second resident model, and from that moment
`OLLAMA_MAX_LOADED_MODELS` and the keep-alive become a real design decision rather than a default.

The last dial is the one people forget: **stop the CPU work that nobody asked for.** A long
generation, a document re-index and a voice command all compete for the same cores. One request at a
time — `OLLAMA_NUM_PARALLEL: "1"` in the Compose file — is what stops a queue of chats from turning
into a voice command that arrives two seconds late.

### Health checks, and what they do not do

The Compose file gives the model server and the chat interface health checks, and the chat interface
waits for the model server to be healthy before it starts:

```yaml
  ollama:
    healthcheck:
      test: ["CMD-SHELL", "ollama list >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

`start_period` is the part that matters on a cold machine: a model server that has just started is
not answering yet, and without it the first three checks would fail and the container would be
declared unhealthy before it was ever ready.

The subtlety worth internalising: **a failing health check marks the container unhealthy, and nothing
else.** It does not restart it. Only a container *exiting* triggers the restart policy. A service
that is alive, hung, and answering nothing is `unhealthy` and stays up until it dies — which is why
the health check is a signal for Compose and for you, not a self-healing mechanism.

### Logs, disks and restarts

Every service in the file carries the same logging block, and it is not decoration:

```yaml
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Without those options, Docker's default `json-file` driver has no size limit at all: a chatty
service writes until the disk is full, and the first symptom is the whole machine behaving strangely,
which is the least useful error message in the stack. Three files of 10 MB per service is a ceiling
you can defend.

Restart policies, and what each one is for:

| Policy | Restarts after a crash | Restarts after a deliberate `stop` | Use when |
|---|---|---|---|
| `no` | No | No | One-shot jobs, and the exposure lab |
| `on-failure` | Yes, with a retry limit you set | No | A service that should retry once or twice, then stay down for you to look at |
| `unless-stopped` | Yes | **No** | The default here: always-on, but you stay in control |
| `always` | Yes | Yes | Machines you never log into — and be careful, a crash-looping container will loop forever |

`unless-stopped` is the right default for a home stack because it means "keep it running unless I
said stop". It also means a service that crashes on startup stays down after you stop it, which is
the behaviour you want at 2 a.m. and also the one that saves you at 9 a.m.

## Show me

What "idle" should look like, as targets rather than measurements. Fill the right-hand column on
your machine, then leave it alone for a week and check whether it is still true.

| What to record | How | Yours |
|---|---|---|
| Total RAM on the host | `python homelab.py doctor` | ______ |
| Sum of your configured limits | Add up the six `*_MEMORY_LIMIT` values in `.env` | ______ |
| Idle RAM after 10 minutes with nothing loaded | `docker stats --no-stream` | ______ |
| Peak RAM during a chat answer | `docker stats --no-stream` while replying | ______ |
| Idle RAM with the model held (`keep_alive` long) | `docker stats --no-stream` right after a reply | ______ |
| Log directory size | `docker system df` | ______ |
| Idle watts, machine on, stack idle | A plug meter, or a smart plug | ______ |
| Watts during one long generation | The same meter | ______ |

Two honest notes about that table. The power readings come from a meter, not from software, because
a laptop's own battery reporting is a different quantity and quoting it as a wall figure is how
course numbers become wrong. And the spike that would have produced our own figures has not run, so
we are not going to print numbers in a column we cannot fill honestly — you fill it.

## Try it

1. Sum your limits before you change anything:

   ```bash
   # Linux / macOS — adds up every *_MEMORY_LIMIT, g and m suffixes alike
   grep -E '^[A-Z_]*MEMORY_LIMIT=' .env | cut -d= -f2 | awk '
     { v = $1; u = 1024; if (v ~ /m$/) u = 1; gsub(/[gm]/, "", v); s += v * u }
     END { printf "%.1f GB total across all limits\n", s / 1024 }'
   ```

   ```powershell
   # Windows PowerShell
   $mb = 0
   Get-Content .env | ForEach-Object {
     if ($_ -match '^[A-Z_]*MEMORY_LIMIT=(\d+)([gm])$') {
       $v = [double]$Matches[1]
       if ($Matches[2] -eq 'g') { $v = $v * 1024 }
       $mb += $v
     }
   }
   "{0:N1} GB total across all limits" -f ($mb / 1024)
   ```

   If the answer is more than about 70% of your RAM, you are on the tier A path from
   `.env.example` — lower `OLLAMA_MEMORY_LIMIT` first, because it is the one that actually moves.

2. Apply the tier A numbers if you need them, then bring the stack up and confirm the limits took:

   ```bash
   docker compose up -d
   docker inspect --format '{{.Name}} {{.HostConfig.Memory}}' $(docker compose ps -q)
   ```

   ```powershell
   # Windows PowerShell
   docker compose up -d
   docker compose ps -q | ForEach-Object { docker inspect --format '{{.Name}} {{.HostConfig.Memory}}' $_ }
   ```

3. Watch what memory the stack is actually using, twice — once idle, once mid-answer:

   ```bash
   docker stats --no-stream
   docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"
   ```

   Ask the chat interface something long enough to take ten seconds, and run the second command in
   the middle of it.

4. Test the keep-alive policy directly. Send one message, then immediately check whether the model
   is still resident:

   ```bash
   docker compose exec ollama ollama ps
   ```

   Leave it five minutes and run it again. If `CHAT_MODEL` and `TOOL_MODEL` are the same model, the
   row is still there and nothing has been swapped.

5. Confirm the logging ceiling, and see the file you are actually writing to:

   ```bash
   docker inspect --format '{{json .HostConfig.LogConfig}}' homelab-open-webui
   docker system df
   ```

   `max-size` and `max-file` should both be present. This is the check that stops a disk-full
   incident from looking like a mysterious slowdown weeks later.

6. Check the health of the two services that have checks, and learn the difference between *running*
   and *healthy*:

   ```bash
   docker compose ps
   docker inspect --format '{{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' homelab-ollama
   ```

7. If your machine is Windows, check the Docker Desktop side of the budget as well. The WSL2 virtual
   machine has its own memory setting, and it is a second, separate ceiling that ignores every limit
   in `.env`. Raise it or lower it to match what the container limits assume.

8. Decide what runs overnight, and write it down. On most boxes the answer is "everything, with
   nothing scheduled" — no pull, no re-index, no rebuild. If you want the voice services off at
   night because nobody is going to ask the house anything:

   ```bash
   docker compose --profile voice stop wyoming-whisper wyoming-piper wyoming-openwakeword
   ```

   and start them again in the morning with `docker compose --profile voice up -d`. Schedule that
   however your operating system does it, and remember the satellite will fail its connection until
   the services are back.

## Break it

**Break it by setting `OLLAMA_KEEP_ALIVE=-1` and calling it a fix.** Voice is instant. The machine
now holds a model in RAM forever, on a 16 GB box with five other services, and the thing that breaks
is not voice — it is everything else, quietly, on a Tuesday.

**Break it by giving the tool model a different name from the chat model.** Now every command that
arrives while a chat is generating can trigger an eviction and a load. You have built the exact
starvation this lesson exists to prevent, and you did it in `.env`.

**Break it by lowering a limit until the model is evicted.** A limit below the weight size plus a KV
cache turns every request into a crash, and the application's own log stays quiet because the kill
came from outside the process. Watch for exit code 137 in `docker compose ps`.

**Break it by removing the logging options.** It feels like cleanup. It is a disk that fills at the
speed of your chattiest service, and the failure mode is the whole stack getting slow rather than
anything logging.

**Break it by leaving the health check as the only safety net.** It reports; it does not repair. A
hung service is a service that stays up.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| A container restarts repeatedly with no log output | Hit its memory limit; exit code 137 | Raise the limit or unload models sooner, and check `docker stats` |
| Voice commands are slow right after a long chat | The tool model was evicted and has to load | Use the same model for both jobs, or allow two resident models |
| The machine never drops back to idle | `OLLAMA_KEEP_ALIVE=-1`, or a limit set far above real use | Set a finite keep-alive and re-measure idle memory |
| The disk fills over weeks | No log rotation, or models piling up | Restore the `logging` block; prune images and unused models |
| A service is up but nothing works | It is `unhealthy`, and health checks do not restart | Read the health check's last output, then restart deliberately |
| Everything restarted itself after you stopped it | `restart: always` | Use `unless-stopped`, which respects a deliberate stop |
| Voice is fine at home and broken overnight | Scheduled work competing for the CPU, or services stopped | Remove the schedule, or make it idempotent and reversible |

The general fix is the boring one: **a number per service, a ceiling on each log, a finite
keep-alive, and a policy for what runs when nobody is asking.** Write them in `.env` and in the
comments beside them, so the next person — including you in six months — knows which are choices
and which are accidents.

## How do I know it works?

- [ ] Your six memory limits sum to at most about 70% of your RAM, and the numbers are in `.env`.
- [ ] `docker stats --no-stream` shows a stack at idle that uses materially less than during a
      chat answer, and you have both numbers written down.
- [ ] `ollama ps` shows the model resident immediately after a reply, and the same model serving
      both the chat and the tool job.
- [ ] Every service has `max-size` and `max-file` in its logging block.
- [ ] `docker compose ps` shows `healthy` for the two services that have health checks, and you know
      that a failing check alone will not restart anything.
- [ ] Every long-running service uses `restart: unless-stopped`.
- [ ] Nothing is scheduled to run overnight that you have not deliberately chosen.
- [ ] `python homelab.py doctor` still prints no port warnings — an operations change is still a
      configuration change.

## Use it when / avoid it

**Use one model for both jobs until you measure a reason not to.** A single resident model is the
simplest way to guarantee that voice is never starved, and `CHAT_MODEL` equal to `TOOL_MODEL` is
already the course default. Move away from it when your own misfire measurements on the 30-command
set tell you the one model is not good enough at tool calls — not before.

**Use a finite keep-alive on a machine that is not always on, and a long one on a machine that is.**
The deciding question is not RAM in the abstract; it is whether the box is going to be asked anything
at 6 a.m.

**Avoid `always` on a machine you can still log into.** `unless-stopped` gives you the same
availability with a stop button, and the stop button is what you want at 2 a.m.

**Avoid tuning these numbers on a day you also changed something else.** One variable at a time is
boring and is the only way to attribute a 20% change to a cause.

> [!TIP]
> **If you have a GPU.** Nothing in this lesson needs one, and one changes two of these numbers.
> Model weights move off RAM, so the memory limits in `.env` stop being the binding constraint and
> the CPU-only sizing from Module 2 stops predicting your speeds. Keep the keep-alive policy, the
> log rotation and the restart policies exactly as they are — none of them change — and treat any
> speed comparison with a CPU number as a comparison between two different machines.

> [!TIP]
> **Do it yourself with llama.cpp.** If you would rather not have a second service in the loop, run
> `llama-server` directly instead of Ollama: `llama-server -m ./model.gguf --host 127.0.0.1 --port
> 8081 --ctx-size 4096 -t 6 --parallel 1`, plus a matching `--threads` value from your Module 2
> measurements. It gives you `--parallel` and `--cont-batching` as first-class knobs, no model
> swapping logic at all, and no keep-alive to reason about. What you give up is the model registry
> and `ollama pull`, so downloads and updates become your problem — and the OpenAI-shaped endpoint
> it serves is the one your chat interface can talk to with a different base URL.

## Reflect

1. Add up your limits and compare the total with your RAM. Which single limit would you lower
   first, and what would break when you did?
2. Your voice command is two seconds late exactly when a long answer is generating. Name the
   mechanism, then name the setting that would fix it without changing either model.
3. What is your stack doing at 3 a.m. right now, and how would you know?

## Sources

- [Ollama FAQ — keep-alive, context size and running more than one model](https://docs.ollama.com/faq)
- [Docker — resource constraints, including memory limits](https://docs.docker.com/engine/containers/resource_constraints/)
- [Docker — configuring log drivers, and the json-file defaults](https://docs.docker.com/engine/logging/configure/)
- [Docker Compose file reference — restart, healthcheck, logging](https://docs.docker.com/reference/compose-file/services/)
- [Pinned versions](../../references/versions.md)
- [Measure yours](../../templates/measure-yours.md)
- [Troubleshooting — "Disk is filling up"](../../references/troubleshooting.md)
