---
id: "03.4"
module: 3
minutes: 10
practice_minutes: 30
prerequisites: ["03.3"]
objectives:
  - Find out what is using disk space in the stack and remove what you are not using.
  - Use `keep-alive` and memory limits so an idle stack gives RAM and power back.
  - Read container logs and set a size limit so they do not fill the disk over a year.
volatility: implementation
sources:
  - title: "Ollama FAQ — keep-alive and context size"
    url: https://docs.ollama.com/faq
  - title: "Docker Compose services — resource limits and logging"
    url: https://docs.docker.com/reference/compose-file/services/
last_verified: "2026-09-30"
---

# 03.4 · Keeping the box tidy

A home stack is not a laptop you reimage every year. It is a machine that will still be running in
eighteen months, with a model you no longer use, logs that grew without a bound, and a service that
has quietly held 11 GB of RAM since April. This lesson is the twenty minutes that keeps it a
machine rather than a problem.

## Why it matters

Three separate things accumulate, and they have different fixes:

1. **Disk.** Downloaded models are the largest thing you own, and you will download more of them
   than you use. Containers, images and logs add up underneath that.
2. **RAM while running.** A model server that never unloads a model holds it forever. Two models
   loaded "just in case" on a 16 GB machine is the difference between a fast box and a thrashing one.
3. **Power while idle.** An always-on host that keeps a 4B model resident draws tens of watts for
   nothing. Module 12 measures this; this lesson is the control that fixes it.

## How it works

### Where the disk goes

| What | Where it lives | How big | Safe to delete? |
|---|---|---|---|
| Model weights | `homelab-ollama-models` volume | 1–5 GB each | Yes, but you re-download it |
| Old images | Docker's image store | 100 MB–4 GB each | Yes, after an upgrade |
| Stopped containers | Docker's container store | Small, but logs grow | `docker container prune` |
| Container logs | `/var/lib/docker/containers` | Unbounded by default | Rotate, do not just delete |
| Chat history | `homelab-open-webui-db` | Grows forever | Only if you want it gone |
| Home Assistant database | `homelab-ha-config` | Grows steadily | Configure the recorder, see below |

The one that surprises people is logs. A chatty service in a container with no rotation setting can
write a single multi-gigabyte file, and `docker logs` will show you the last ten lines with no
indication that the file is enormous. The course's compose file caps every service at 10 MB × 3
files:

```yaml
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Why models stay in RAM

Loading a 2.5 GB model from disk takes a few seconds. Doing that on every request would be
unpleasant, so the model server keeps it resident after use. The relevant setting is `keep-alive`,
and the default behaviour of most runtimes is to keep a model loaded for several minutes and then
unload it. Two settings control it in the stack:

```yaml
    environment:
      OLLAMA_KEEP_ALIVE: "5m"          # unload five minutes after the last request
      OLLAMA_MAX_LOADED_MODELS: "2"    # never hold more than two models at once
```

`OLLAMA_NUM_PARALLEL: "1"` is also set, and matters more than it looks: a local machine has one
memory bandwidth to share, so serving two requests at once does not double the speed, it splits it
between them and doubles the wait for each.

## Show me

What a healthy idle stack looks like, which is the state you are aiming for:

| Service | Idle RAM | Note |
|---|---|---|
| ollama | 60–120 MB | With no model loaded, this is a small process waiting |
| open-webui | 400–900 MB | The database and the web server |
| homeassistant | 600 MB–1.2 GB | Grows with the number of entities |
| wyoming-* | 200–900 MB each | Whisper loads its model on first use |

If `ollama` is holding several gigabytes while nobody is using it, `keep-alive` is too long or the
server was never told to unload. Measure your own numbers rather than adopting these.

## Try it

1. See what is actually installed, and how big each model is:

   ```bash
   # Windows PowerShell, macOS and Linux
   docker run --rm -v homelab-ollama-models:/root/.ollama ollama/ollama:0.35.0 ollama list
   ```

2. Remove a model you are not using. Pulling a 7B "to try it" and forgetting about it is the
   normal way to lose 5 GB:

   ```bash
   docker run --rm -v homelab-ollama-models:/root/.ollama ollama/ollama:0.35.0 ollama rm qwen2.5:7b
   ```

3. Find out where the disk went, before deleting anything:

   ```bash
   # Windows PowerShell
   docker system df
   docker system df -v | Select-String -Pattern "homelab"

   # macOS / Linux
   docker system df -v
   ```

   `docker system df` prints total size and reclaimable size for images, containers, local volumes
   and build cache. The reclaimable column is the answer to "can I delete this safely".

4. Reclaim space from old images after an upgrade, once the new ones are proven:

   ```bash
   # dangling (untagged) images only - safe, and the ones upgrades leave behind
   docker image prune
   ```

   Do not run `docker system prune --volumes` out of curiosity. That is `down -v` with extra steps.

5. Watch RAM while the stack is idle and then while it is answering:

   ```bash
   docker stats --no-stream
   ```

   Run it twice: once with nothing happening, once while a long answer is generating. The difference
   is the model, and it is the number to put in your RAM bill.

6. Set the limits so the mistake is not repeatable. In `.env`:

   ```dotenv
   OLLAMA_KEEP_ALIVE=5m
   ```

   and in the compose file, if it is not already there:

   ```yaml
       deploy:
         resources:
           limits:
             memory: ${OLLAMA_MEMORY_LIMIT:-12g}
   ```

   Then `docker compose up -d` to apply it.

## Break it

**Break it with `OLLAMA_KEEP_ALIVE: -1`.** That means never unload. Pull two large models, use both
once, and walk away. On a 16 GB machine, the model server is now holding roughly 7 GB of weights for
a service nobody is using, and the next thing that needs memory — a browser, a build, the voice
pipeline in Module 8 — fights for what is left. Nothing crashes. Everything is just slow, which is
the hardest kind of broken to diagnose later.

**Break it with a missing log rotation.** Remove the `logging:` block from one service, make that
service chatty, and leave it a month. Then check the size of the log file. It will be much larger
than you expect and it is a single file.

**Break it by assuming `down` frees the disk.** Run `docker compose down` and look at the free
space. Volumes survive, so models, chat history and the Home Assistant database all survive. That is
the correct behaviour and a common surprise.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Disk nearly full, no idea why | Several causes at once | `docker system df -v`, then prune images before touching volumes |
| Model server holds gigabytes while idle | `keep-alive` too long, or `-1` | Set `OLLAMA_KEEP_ALIVE=5m` and restart |
| Two slow answers at once | Parallel requests share one bandwidth | `OLLAMA_NUM_PARALLEL=1`; queue instead of splitting |
| A service killed during a big request | Its memory limit is too low | Raise the limit in `.env`, or use a smaller model |
| Home Assistant database is large | Every state change is recorded by default | Turn off unneeded recorder domains in its configuration |
| Chat history is enormous | Long conversations accumulate forever | Prune old chats in the interface, or accept the disk cost |

The habit worth forming: **run `docker system df` and `docker stats` monthly**, the same way you
would check disk space on any other machine. Neither command changes anything.

## How do I know it works?

- [ ] `docker system df` shows a reclaimable figure you could live with, and you know what it is.
- [ ] `ollama list` contains only models you actually use.
- [ ] `docker stats` while idle shows the model server at a few hundred MB, not several gigabytes.
- [ ] You can state which volume holds the thing you would be most upset to lose.
- [ ] Every service in the compose file has a `logging:` block with `max-size` set.

## Use it when / avoid it

**Do this before the capstone**, not just now. A capstone stack that runs out of disk on day three
is a stack that fails a criterion it should not have.

**Set `keep-alive` from what you measured.** If your voice pipeline needs the model loaded
immediately every time — see Module 10 — a long `keep-alive` is correct for the *tool* model and
wrong for the *chat* model. One server, two policies, is what Module 4's concurrency lesson is
about.

**Avoid deleting volumes to save space.** Rebuilding a vector index takes minutes; re-downloading a
model takes the same time and the same bandwidth. Neither is a disaster, but neither is the first
move. Look at images and logs first, because they are pure waste.

**Do not hand-manage files inside volumes.** `docker volume inspect` will show you the path on
Linux, and you can then copy things out — but editing them in place is how you end up with a state
directory that no longer matches its version.

> [!TIP]
> **Automate the boring half.** A monthly cron job running `docker image prune -f` and appending
> `docker system df` to a log is five lines, and it is the whole routine. Put the date in the
   [update routine](../../templates/update-routine.md) so it happens without you deciding to.

## Reflect

1. Which volume on your machine is largest right now, and what is the single command that would
   shrink it? Would you lose anything you care about?
2. If your model server held 7 GB of resident weights at idle, which of the five services in the
   full stack would fail first, and how would you tell the difference between "the model is too
   big" and "the model server is leaking"?
3. Which of your five services would you most want to keep running overnight, and which would you
   be happy to have stop? That is a `restart:` policy question, and it is Module 12's opening.

## Sources

- [Ollama FAQ — keep-alive, context size and environment variables](https://docs.ollama.com/faq)
- [Docker Compose services — resource limits and logging options](https://docs.docker.com/reference/compose-file/services/#resources)
- [Troubleshooting — disk filling up](../../references/troubleshooting.md)
- [Measure-yours tables — the RAM bill](../../templates/measure-yours.md)
- [Update routine](../../templates/update-routine.md)
