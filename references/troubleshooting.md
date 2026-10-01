# Troubleshooting

Symptoms first, because that is how you arrive here. Every fix links to the lesson that explains
why it works.

If your problem is not here, `python homelab.py doctor` is the first thing to run and its output
names the most likely cause.

---

## "It works, but it is very slow"

The most common complaint in a home AI setup, and usually not a bug.

- [ ] **One RAM stick, or a laptop with soldered single-channel memory.** This roughly halves
      generation speed. You cannot fix it in software; you can only choose a smaller model. Check
      what `homelab.py doctor` reports for memory channels, and confirm with a thread sweep in
      [08 · Measure prompt speed and generation speed](../lessons/module-02/lesson-03.md).
- [ ] **Swap is being used.** If the model is larger than free RAM, every token now also goes to
      disk and you are 100× slower, not 2× slower. Watch `free -h` (Linux/macOS) or the Performance
      pane (Windows) during a request.
- [ ] **Thermal throttling.** A laptop that was fast when cold and slow after ten minutes is
      throttling. Check CPU clock during a benchmark, not at idle.
- [ ] **The context is enormous.** A 32 000-token context allocates a KV cache you have to pay for
      on every token. See [05 · Settings that change the answer](../lessons/module-01/lesson-03.md).
- [ ] **A 7–8B model on a 16 GB machine.** It will run, and it will run slowly, and it will leave
      nothing for the browser. Use a 3–4B. [09 · Pick the largest model that meets your target](../lessons/module-02/lesson-04.md)
      is the lesson that tells you which one.

## "Home Assistant cannot reach Ollama"

`connection refused`, or the entity stays `unavailable`.

This is not a Home Assistant bug, it is container networking, and the cause is the same almost
every time: **Ollama on the host is bound to `127.0.0.1`, and a container cannot reach the host's
loopback address.**

- [ ] Inside a compose network, reach a host service by its service name, not `127.0.0.1`. If
      Ollama is itself a service on that network, use `http://ollama:11434`.
- [ ] If Ollama runs natively on the host, use `host.docker.internal` — and that only works if
      Ollama is listening on more than loopback. Binding it to `0.0.0.0` is the usual advice and it
      is also how people expose an unauthenticated model server to the internet.
- [ ] **The safe fix, and the one this course uses:** put Ollama in the Compose network, on an
      internal network, with no published port at all. Nothing outside the Docker network can reach
      it, and Home Assistant can. [12 · The shared stack](../lessons/module-03/lesson-03.md) builds
      it; [38 · Bind addresses and ports](../lessons/module-11/lesson-02.md) explains the reasoning.
- [ ] On Linux, a native Ollama on the host is reachable at the Docker bridge gateway
      (`172.17.0.1`) *if* it listens on `0.0.0.0` or that address. Prefer the Compose network.

## `docker compose` cannot find a file, or the network does not exist

- [ ] You copied a `compose.yaml` fragment instead of the whole file. Relative paths in Compose
      resolve against the file's own directory, not your shell's.
- [ ] You are in the wrong directory. `docker compose config` prints the fully resolved file; read
      the top of it.
- [ ] A service was started outside a profile. Profiles are opt-in: `--profile voice` and nothing
      voice-related exists. [12 · The shared stack](../lessons/module-03/lesson-03.md).
- [ ] A stale container from an earlier run is holding the port. `docker compose down` (keeps
      volumes) or `docker compose down -v` (**deletes** your data — read what you are deleting).

## Docker Desktop is slow or out of memory on Windows

- [ ] Docker Desktop has its own memory limit, independent of your RAM. Settings → Resources →
      Memory. WSL2 also caps it: `.wslconfig` in your user profile with `[wsl2] memory=16GB`. Both
      limits apply, and the smaller one wins.
- [ ] Keep model files **outside** the Docker filesystem, or on a named volume. A model living in
      the VM's virtual disk is read through a 9p mount and is dramatically slower to load.
- [ ] If the VM has no swap and you overcommit, the OOM killer takes the largest process — which
      will be your model server. Symptom: the container dies with no useful log line.

## The microphone does not work

- [ ] The browser asks for permission; a denial is sticky. Site settings → Microphone → Allow, then
      reload the page.
- [ ] On Linux, PipeWire or PulseAudio must be reachable, and your user must be in the `audio`
      group. A container cannot see your laptop's microphone without extra plumbing, which is exactly
      why this course runs the satellite **natively on the host** and not in Docker.
- [ ] macOS asks for microphone permission per application, and Terminal, your editor and the
      browser are three different applications. Grant it to all three. *(macOS steps are not
      verified by us.)*
- [ ] **The text-only route always works.** Typed Assist commands and WAV files need no microphone at
      all, and every voice lab in this course has one. Use it to isolate whether the problem is
      audio hardware or the pipeline.

## Whisper transcribes my command as nonsense

- [ ] You pulled a `.en`-only model. It is smaller and faster and it silently produces garbage on
      anything else. Use the **multilingual** models. [27 · Speech-to-text on your CPU](../lessons/module-08/lesson-02.md)
- [ ] `base` is genuinely weak on accents, background noise and unusual entity names. `small` is a
      large accuracy jump and costs about 450 MB more RAM.
- [ ] The audio device is picking up the wrong input. Check which device Home Assistant is
      actually recording from before blaming the model.

## Assist understands the words but not the meaning

- [ ] The entity is not **exposed** to Assist. Exposing is opt-in per entity, per assistant.
      [24 · Assist with typed commands](../lessons/module-07/lesson-02.md).
- [ ] The name you say does not match the name Assist knows. Add an alias.
- [ ] The area or floor is not set on the entity, so "the light" has nothing to resolve to.
- [ ] An LLM conversation agent is not configured, and the sentence is a question rather than a
      command. Built-in intents only control things; they do not answer. [34 · Intents first, LLM as fallback](../lessons/module-10/lesson-02.md)

## The LLM called the wrong tool, or called no tool

- [ ] The model is too small. This is a property of small models, not a misconfiguration.
      [35 · Tools and guardrails](../lessons/module-10/lesson-03.md) measures the rate instead of
      guessing.
- [ ] Too many entities are exposed. Every exposed entity is in the system prompt, and a small model
      drowns in the list. Expose fewer.
- [ ] Read the tool calls in the log. Open WebUI and the Home Assistant conversation log both show
      them, and the answer to "why did it do that" is almost always written there.

## Port 8080 (or 3000, or 8123) is already in use

- [ ] Something else already has it — often a previous container that did not stop.
      `docker ps -a` then `docker compose down`.
- [ ] Change the host side only: `"8081:8080"` maps host 8081 to container 8080. The left number is
      on your machine, the right one belongs to the service.

## Disk is filling up

- [ ] Models are the largest thing you own. `ollama list` shows what is downloaded;
      `ollama rm <tag>` removes one. [13 · Keeping the box tidy](../lessons/module-03/lesson-04.md).
- [ ] Old images after upgrades: `docker image prune`.
- [ ] Home Assistant's database grows with every state change; its recorder and logbook are the
      usual culprits.
- [ ] `docker system df` shows where it all went.

## `homelab.py` will not run

- [ ] Python 3.10 or newer: `python3 --version`. On Windows, `py --version`.
- [ ] Run it from the folder that holds `.env`, or point at it:
      `python homelab.py doctor --env /path/to/.env`.
- [ ] If it prints a YAML parse error, your `.env` has a value with spaces and no quotes.

---

Still stuck? Run the dry run and read the whole output rather than the first line:

```bash
docker compose --profile voice ps
docker compose --profile voice logs --tail=50 ollama
python homelab.py doctor --verbose
```
