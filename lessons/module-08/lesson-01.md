---
id: "08.1"
module: 8
minutes: 12
practice_minutes: 35
prerequisites: ["07.2"]
objectives:
  - >-
    Describe the Assist pipeline stage by stage, name what runs on which machine, and explain what
    the Wyoming protocol is for.
  - Bring the voice services up on an internal network and see Home Assistant discover them.
  - Explain why a satellite runs on the host rather than in a container.
volatility: concept
sources:
  - title: "Wyoming protocol specification"
    url: https://github.com/rhasspy/wyoming
  - title: "Home Assistant — Wyoming integration"
    url: https://www.home-assistant.io/integrations/wyoming
  - title: "Home Assistant — setting up a fully local voice assistant"
    url: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
last_verified: "2026-09-30"
---

# 08.1 · The Wyoming protocol

A voice assistant is four or five programs that have to agree on a format for audio going in and
audio coming out. Wyoming is that agreement. It is a small, boring, extremely useful piece of
infrastructure, and understanding it is what turns "my voice assistant sometimes works" into
"stage three is slow on my machine".

## Why it matters

Without a shared protocol, every pairing of speech-to-text with text-to-speech needs its own glue.
With one, the services are interchangeable: swap Whisper for another speech engine, or Piper for
another voice engine, and nothing else changes. That is why Home Assistant, the satellite, the
wake word and the speech services all speak Wyoming rather than anything proprietary.

It also gives the pipeline a shape. Once the shape is explicit, latency has a place to live, and
latency is the product requirement that makes voice different from chat.

## How it works

### The stages

![The Assist pipeline: a satellite listening for a wake word and detecting the end of speech, then speech-to-text, then either a built-in intent match or a local LLM with tools calling Home Assistant, then text-to-speech back out to a speaker, with the budget for each stage underneath](../../assets/assist-pipeline.svg)

Read that diagram as five boxes with four arrows. Each box is a separate process:

| Stage | What it is | Runs on |
|---|---|---|
| **Satellite** | Listens for a wake word, streams audio, detects the end of speech | Your host, with the microphone |
| **Speech-to-text** | Audio → text | A container on the `voice` network |
| **Intent** | Text → an intent and slots | Inside Home Assistant |
| **Conversation agent** (optional) | Text → a choice of tool | The model server, via Home Assistant |
| **Text-to-speech** | Text → audio | A container on the `voice` network |

The **voice activity detection** — deciding the user has finished speaking — lives inside the
satellite, not in the speech service. It is worth knowing which box it lives in, because "it cuts me
off after three words" and "it waits two seconds after I stop" are different bugs in different
processes.

### What Wyoming actually does

It is a simple line-based protocol over a socket, carrying chunks of audio or text plus timestamps.
The important properties for this course:

- **It is a socket, not an HTTP request.** A service runs as a server on a port; clients connect.
- **It streams.** Audio goes up in chunks and text comes back in chunks, which is why the first
  word of a reply can arrive before the reply is finished.
- **It is discovered, not configured.** Home Assistant's `wyoming` integration finds services on the
  network automatically. You add the service once and pick it in the pipeline editor.

### The two networks

```yaml
    networks:
      - ai        # to the model server
      - voice     # to Whisper, Piper and the wake word
```

Both are `internal: true`, so the voice services publish nothing to your machine at all. The
satellite is the only piece that needs to reach your host's network, and it runs there — which is
why the next section matters.

### Why the satellite is on the host

A container can have audio passed to it. It cannot, without significant plumbing, reach a laptop's
microphone, and on Windows the plumbing involves a virtual audio device and a permission dance that
is not worth any learner's time. So the satellite runs natively on the host, and everything else runs
in containers where it belongs.

This is a deliberate design decision, not a limitation being worked around. The microphone belongs
to the operating system; the speech engines do not.

## Show me

The services in `labs/common/compose.yaml`, all on the voice network with no published ports:

```yaml
  wyoming-whisper:
    image: rhasspy/wyoming-whisper:1.4.0
    command: ["--model", "${STT_MODEL:-base}", "--language", "${LANG_TAG:-en}", "--download-dir", "/data"]
    volumes: [whisper-models:/data]
    networks: [voice]

  wyoming-piper:
    image: rhasspy/wyoming-piper:1.3.0
    command: ["--voice", "${TTS_VOICE:-en_US-lessac-medium}", "--download-dir", "/data"]
    volumes: [piper-voices:/data]
    networks: [voice]
```

Two defaults worth naming: `STT_MODEL=base` and `TTS_VOICE=en_US-lessac-medium`. Both are
provisional — the choice of speech model is the subject of the next two lessons — and both live in
`.env` so you can change them without editing a lesson.

## Try it

1. Start the voice services:

   ```bash
   docker compose --profile voice up -d
   docker compose --profile voice ps
   ```

   You should see Whisper, Piper and the wake word service running. Give them a minute: the first
   start downloads the model and the voice, which is a few hundred megabytes.

2. Watch them start, rather than assume:

   ```bash
   docker compose --profile voice logs -f wyoming-whisper
   ```

   You are looking for the port it is listening on, and for the model download finishing.

3. Let Home Assistant discover them. Go to **Settings → Devices & services**. Unconfigured
   integrations named `Wyoming` appear, one per service — that is discovery working, not a bug.

4. Add each one. For Whisper, set the language to match `LANG_TAG` in your `.env`; for Piper,
   pick a voice. Then check **Settings → Voice assistants**: both should now be selectable.

5. Create an assistant if you have not already, and point it at those two services:

   ```text
   Conversation agent:  Home Assistant        (Module 10 changes this)
   Speech-to-text:      Whisper
   Text-to-speech:      Piper
   ```

6. Test from the Assist developer tools page — **typed**, with no microphone and no satellite. If
   a typed sentence comes back as audio in the log, the pipeline is assembled correctly. That is the
   fastest possible check and it isolates the four services from the two things Module 9 adds.

7. Write down what each stage is, from memory, on a piece of paper. If you cannot name the five
   boxes without looking, the next three lessons will be harder than they need to be.

## Break it

**Break it with a wrong language.** Set `STT_MODEL` language to English and speak something else.
Whisper does not refuse; it returns confident nonsense, and everything downstream acts on nonsense.
This is a lesson worth experiencing once, because the failure looks like a broken model.

**Break it by starting only some services.** `docker compose up -d wyoming-whisper` without the
profile. Home Assistant discovers nothing, and the pipeline editor offers no speech engine. The
fix is the profile flag, not the configuration.

**Break it with a port collision.** Run two Wyoming services on the same port on the host — for
example if you started a satellite natively while a container one is still running. The second
fails to bind and the symptom is a satellite that connects and then goes silent.

**Break it by putting a voice service on a published port.** It works, and it has created the
situation Module 11 is about: a service on your network that will transcribe whatever is sent to
it. The compose file deliberately has no `ports:` line for any of them.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| No Wyoming integrations appear | The services are not running | `docker compose --profile voice ps` |
| They appear but the assistant offers nothing | Not added yet | Add each discovered integration |
| Transcription is wrong but confident | Wrong language | Match `LANG_TAG` on both sides |
| The pipeline editor has no speech engine | The integration was not added, or the assistant was not configured | Check both, in that order |
| A satellite connects then goes silent | Port already bound by something else | Find it with `ss -tlnp` or `Get-NetTCPConnection` |
| Nothing works after a restart | Profile not passed | `docker compose --profile voice up -d` |

## How do I know it works?

- [ ] `docker compose --profile voice ps` shows all three voice services running.
- [ ] Home Assistant has discovered and added both a speech-to-text and a text-to-speech service.
- [ ] A typed sentence produces spoken audio through the full pipeline.
- [ ] You can name the five stages and say which machine each one runs on.
- [ ] You have not published any voice service to your network.

## Use it when / avoid it

**Use the Wyoming services** because they are interchangeable, discovered rather than configured,
and they compose with Home Assistant without glue code.

**Keep them on an internal network.** They process audio of your household, and none of them needs
a port.

**Run the satellite on the host.** The microphone belongs to the operating system, and every
alternative is a worse trade at home.

**Do not treat the pipeline as one thing.** Every voice problem is a stage problem, and the stage
is where the fix is. Module 8.4 is the lesson that finds it.

> [!NOTE]
> macOS: audio permissions are granted per application, so Terminal, your editor and your browser
> each need it separately. Our macOS steps are **not verified by us** — there is one Windows test
> machine.

## Reflect

1. Name the five stages and the machine each one runs on, without looking.
2. If a command is cut off after two words, which stage is the suspect, and what would you check
   first?
3. Why is the satellite the only part that has to run on the host, and what would you have to build
   to put it in a container?

## Sources

- [Wyoming protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant — Wyoming integration](https://www.home-assistant.io/integrations/wyoming)
- [Home Assistant — setting up a fully local voice assistant](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- [27 · Speech-to-text on your CPU](lesson-02.md)
- [29 · Measure the voice pipeline](lesson-04.md)