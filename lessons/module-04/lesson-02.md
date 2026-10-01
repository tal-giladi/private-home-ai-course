---
id: "04.2"
module: 4
minutes: 12
practice_minutes: 35
prerequisites: ["04.1"]
objectives:
  - Explain what happens on one box when chat and voice both want the model server at the same moment.
  - Control memory with `keep-alive`, `max_loaded_models` and container limits, and measure the result.
  - Design a policy for which model stays loaded and which is unloaded quickly.
volatility: implementation
sources:
  - title: "Ollama FAQ — keep-alive, context size and parallel requests"
    url: https://docs.ollama.com/faq
  - title: "Docker Compose services — resource limits"
    url: https://docs.docker.com/reference/compose-file/services/#resources
last_verified: "2026-09-30"
---

# 04.2 · Two models, one box

The moment this course has been building towards: chat and voice on the same machine, both needing
the same single pool of memory bandwidth. This lesson is about what happens when they collide, and
about the three settings that decide whether the collision is invisible or the reason your voice
assistant stops working.

## Why it matters

A home stack has at least two callers with opposite needs.

**Chat** is patient. A person asks a question, watches words appear, and does not mind a few
seconds. Between questions, the model could be unloaded entirely and reloaded with no one noticing.

**Voice** is not patient. A spoken command has a budget of about two seconds from the end of your
sentence to the first sound of the reply, and if the model is on disk instead of in RAM, that
budget is gone before it starts. A voice assistant that has to load a model on every command is
worse than one that simply does not use a model.

Those two wants conflict, and the conflict shows up exactly once: at the moment somebody says a
command while a long chat answer is still generating.

## How it works

### Three settings, three different jobs

| Setting | What it controls | Wrong value costs you |
|---|---|---|
| `OLLAMA_MAX_LOADED_MODELS` | How many models stay in RAM at once | More than one on a 16 GB box: nothing fits |
| `OLLAMA_KEEP_ALIVE` | How long an idle model stays loaded | `-1`: RAM is never given back |
| `OLLAMA_NUM_PARALLEL` | How many requests are served at once | More than 1: each request is slower, not faster |

The defaults in the course's stack:

```yaml
    environment:
      OLLAMA_MAX_LOADED_MODELS: "2"
      OLLAMA_KEEP_ALIVE: "5m"
      OLLAMA_NUM_PARALLEL: "1"
```

**`NUM_PARALLEL: 1` is the one people argue about and it has a clear answer on a CPU.** Two
requests running at once share the same memory bandwidth, so each one is roughly twice as slow. It
is not free parallelism; it is the same bytes split in half. Queueing is better: the second request
waits a moment and then runs at full speed, and the user is waiting either way.

**`MAX_LOADED_MODELS: 2`** exists because a home stack genuinely uses two: a chat model and a
smaller tool-calling model. Two loaded models on a 32 GB machine is fine. On a 16 GB machine with a
browser open it is the whole budget, and `1` is the honest setting.

**`KEEP_ALIVE` is a policy, not a preference.** Five minutes is a good default for chat. For the
voice pipeline it is usually too short, because a model that unloads between commands will need to
be reloaded on the next one. Modules 9 and 10 come back to this.

### What actually happens on a collision

Say you are mid-answer in the chat interface, generating at 6 tokens/s, and a voice command arrives.

1. The second request **queues** (with `NUM_PARALLEL: 1`). It waits for the first to finish.
2. If it needs a *different* model and `MAX_LOADED_MODELS` is 1, the first model is **unloaded** to
   make room. That is a multi-second operation.
3. If it needs the *same* model, nothing is loaded or unloaded; it simply waits.

The failure people actually hit is case 2, and it looks like "my voice assistant is slow only when
I am chatting". It is not randomness and it is not a slow model. It is a model swap, caused by
asking for two things at once, on a machine sized for one.

### The three-part fix

1. **One model for both, if the machine allows it.** A 4B model that is acceptable for chat is
   acceptable for voice tool calls, and then there is never a swap. This is the course's default and
   the reason `CHAT_MODEL` and `TOOL_MODEL` are usually the same value.
2. **If you need two models, give the box room.** Two models on a 16 GB machine means one of them
   is small, and you have to lower the other services' limits to pay for it. Do the arithmetic in
   the [RAM bill](../../templates/measure-yours.md) before you do it.
3. **Cap the model server in the container.** `deploy.resources.limits.memory` makes the model
   server fail loudly at a limit you chose rather than squeezing Home Assistant and the voice
   pipeline until something dies without explanation.

## Show me

The measured shape of the problem, on any machine. These are not the course's measurements — they
are the pattern to go and confirm on yours with the commands in **Try it**:

| Situation | What you see |
|---|---|
| One chat request | Full speed; first token after the model loads |
| Two chat requests at once, `NUM_PARALLEL: 1` | Second waits, then runs at full speed |
| Two chat requests at once, `NUM_PARALLEL: 2` | Both run at about half speed |
| Chat on model A, voice on model B, `MAX_LOADED_MODELS: 1` | A swap, and a multi-second stall |
| Chat on model A, voice on model A | No swap; the voice request waits for the chat one to finish |

The last row is the target. It is boring, and boring is the right answer for a box in a house.

## Try it

1. Watch the model server hold and release memory. With the stack running, in a second terminal:

   ```bash
   # Windows PowerShell
   docker compose logs -f ollama | Select-String -Pattern "load|offload|inference"

   # macOS / Linux
   docker compose logs -f ollama | grep -E "load|offload|inference"
   ```

   Send one message, then stop watching for six minutes. The line where it unloads is the
   `keep-alive` you configured, made visible.

2. Measure the cost of a swap. Time a request to a model that is already loaded, then to one that
   is not:

   ```bash
   # time the first request to a model you have not used recently
   docker compose exec ollama sh -c 'time ollama run qwen3:4b "say hi"'
   # and again immediately - the second one has the model loaded
   docker compose exec ollama sh -c 'time ollama run qwen3:4b "say hi"'
   ```

   The difference is the load time, and it is the number Module 8's latency budget has to absorb.

3. Test the collision. In one terminal, start a long generation:

   ```bash
   docker compose exec ollama ollama run qwen3:4b "write a 600 word essay about tides"
   ```

   While it is running, send a second short request from another terminal. Note how long the second
   one takes to produce its first word. Now change `OLLAMA_NUM_PARALLEL` to `2` in `.env`, restart
   with `docker compose up -d`, and repeat. Write both numbers in your
   [measure-yours table](../../templates/measure-yours.md).

4. Test the swap. With `MAX_LOADED_MODELS=1`, alternate requests between two models and time each:

   ```bash
   docker compose exec ollama ollama run qwen3:4b "hi"
   docker compose exec ollama ollama run llama3.2:1b "hi"
   docker compose exec ollama ollama run qwen3:4b "hi"
   ```

   The third one pays the load again. This is why the course defaults to a single model for both
   chat and tool calling.

5. Set a container limit that reflects your RAM bill rather than the default:

   ```dotenv
   OLLAMA_MEMORY_LIMIT=7g
   ```

   ```bash
   docker compose up -d
   docker stats --no-stream
   ```

6. Write your policy down, in one line, in the `Reflect` section's answer: which model stays loaded,
   for how long, and what is unloaded when you are not talking.

## Break it

**Break it with a swap and a long context.** Set `MAX_LOADED_MODELS: 1`, `KEEP_ALIVE: 24h`, use
a 4B model, then ask for a 16 000-token context. The KV cache plus the weights exceed the limit,
the container is killed by the out-of-memory mechanism, and the log shows nothing useful. The
process is killed from outside, so it never gets to explain itself — check `docker inspect` for exit
code 137.

**Break it with `NUM_PARALLEL: 4`.** The first token of every reply gets slower, not faster, and
with four in flight it gets much slower. Nothing errors.

**Break it by loading two big models and then opening a browser.** On a 16 GB machine the failure
is the machine becoming slow rather than anything stopping. `docker stats` shows the model server
holding most of the memory and the browser being squeezed.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Voice is slow only while chatting | A different model is being swapped in | Use one model for both, or raise `MAX_LOADED_MODELS` and make room |
| Every request is slower than your benchmark | `NUM_PARALLEL` above 1, or a swap each time | Set `NUM_PARALLEL: 1` |
| RAM is never released | `KEEP_ALIVE: -1`, or a very long value | A few minutes for chat; longer for voice, deliberately |
| Model server killed during a big context | The container limit is below weights plus KV cache | Raise the limit or lower the context; check exit code 137 |
| One model is loaded that you never use | `keep-alive` long enough to outlive your session | Shorten it, or remove the model |

The principle underneath all of these: **on a CPU, memory is the scarce resource and bandwidth is
the throughput.** Every setting in this lesson is really a statement about how to divide one of
them.

## How do I know it works?

- [ ] You can state, in one sentence, your policy for which model stays loaded and for how long.
- [ ] `docker stats` while idle shows the model server holding only a model you are about to use.
- [ ] You have measured the load time of a model, and written it in the measure-yours table.
- [ ] Two simultaneous requests behave as you expect with `NUM_PARALLEL: 1` — queued, not halved.
- [ ] Your container memory limit is lower than your total RAM, and higher than the largest thing
      you expect to load.

## Use it when / avoid it

**Use `NUM_PARALLEL: 1`** unless you have measured otherwise on your own machine. On a CPU it is
almost always right, and it makes latency predictable, which is what a voice pipeline needs.

**Use two models** when the jobs genuinely differ and you have measured the RAM cost. A small
1–2B model for Home Assistant tool calls and a 4B for chat is a defensible design on 32 GB, and a
poor one on 16 GB. The decision procedure is in [17 · One model per job](../module-05/lesson-01.md).

**Do not set `KEEP_ALIVE: -1`** on a laptop. It is defensible on a dedicated always-on box where the
model genuinely needs to be there for a voice command, and it is the reason Module 12 measures idle
power as well as idle RAM.

**Avoid raising container limits to "whatever is left".** A limit is a decision about what this
service may take from the others. Picking it from a measurement is fine; picking it from a guess
just moves the failure to a service that cannot defend itself.

> [!TIP]
> **If you have a GPU.** With a GPU, parallel requests stop being purely bandwidth-bound because
> compute moves off the CPU, and `NUM_PARALLEL` above 1 can genuinely help. The numbers in this
> lesson are specifically about a CPU-only box, and a GPU result is not comparable to them.

## Reflect

1. Write your policy in one sentence: which model stays loaded, for how long, and what happens when
   the other kind of request arrives.
2. You measured a model load costing N seconds. In Module 8's latency budget, where does that
   number go, and how could you make sure it is never paid during a spoken command?
3. Which service in your stack would break first if the model server were allowed to use all
   available memory, and how would you notice it was that service rather than the model?

## Sources

- [Ollama FAQ — keep-alive, context size and parallel requests](https://docs.ollama.com/faq)
- [Docker Compose services — resource limits](https://docs.docker.com/reference/compose-file/services/#resources)
- [Measure-yours tables](../../templates/measure-yours.md)
- [Troubleshooting — Home Assistant cannot reach Ollama](../../references/troubleshooting.md)
- [Home Assistant's Ollama integration — concurrency notes](https://www.home-assistant.io/integrations/ollama/)
