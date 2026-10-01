# Pinned versions

Every image in the course's Compose file is pinned to an exact tag. `latest` is banned: it turns a
working home lab into a broken one on a random Tuesday, and it is how you end up running a version
with a known CVE without ever choosing to.

Tags below were read from the registries on **2026-09-30**. The lab's real source of truth is
`labs/common/compose.yaml`; this page exists so you can see what you are running without opening the
file, and so a bump is a visible act rather than a silent one.

> [!IMPORTANT]
> The phase-1 spike has not run yet, so **the `rhasspy/wyoming-*` tags are the ones to verify first**.
> Everything else was read from a registry. Check a tag before you trust it:
>
> ```bash
> # what does this tag actually resolve to?
> docker manifest inspect ollama/ollama:0.35.0 | head -5
>
> # what is the newest published tag?
> curl -s "https://hub.docker.com/v2/repositories/rhasspy/wyoming-whisper/tags?page_size=5&ordering=last_updated"
> ```
>
> Bump a tag only from the [update routine](../templates/update-routine.md), never in the middle of a
> module.

## Core stack

| Service | Image | Pinned tag | Verified |
|---|---|---|---|
| Model runtime | `ollama/ollama` | `0.35.0` | 2026-09-30 |
| Chat UI | `ghcr.io/open-webui/open-webui` | `v0.11.4` | 2026-09-30 |
| Home Assistant | `ghcr.io/home-assistant/home-assistant` | `2026.9.4` | 2026-09-30 |
| Vector store (optional, Module 6) | `qdrant/qdrant` | `v1.19.1` | 2026-09-30 |

`ghcr.io` images are the publishers' own registries. `docker login ghcr.io` is only needed for
private images; these four are public.

## Voice stack (Modules 8–9)

| Service | Image | Pinned tag | Verified |
|---|---|---|---|
| Speech-to-text | `rhasspy/wyoming-whisper` | `1.4.0` | **check during the spike** |
| Speech-to-phrase (alternative STT) | `rhasspy/wyoming-speech-to-phrase` | `1.3.0` | **check during the spike** |
| Text-to-speech | `rhasspy/wyoming-piper` | `1.3.0` | **check during the spike** |
| Wake word | `rhasspy/wyoming-openwakeword` | `1.1.0` | **check during the spike** |
| Satellite (laptop mic) | `rhasspy/wyoming-satellite` | `1.1.0` | **check during the spike** |

All five speak the [Wyoming protocol](https://github.com/rhasspy/wyoming) and are discovered by
Home Assistant's `wyoming` integration over the internal Docker network. They are not published to
any host port at all.

## Models

Models are not pinned in `compose.yaml` — they are pulled by Ollama from its own registry, and the
tag *is* the pin (`qwen3:4b` is immutable, unlike `latest`). The default names live in
`labs/common/.env`:

```dotenv
CHAT_MODEL=qwen3:4b
TOOL_MODEL=qwen3:4b
EMBED_MODEL=nomic-embed-text
STT_MODEL=base
TTS_VOICE=en_US-lessac-medium
```

Sizes, licences and where each file comes from: [Pinned models and licences](models.md).

## Host software

Not containers, so not pinned by Compose, but worth writing down on your machine:

| Tool | Why | How to record yours |
|---|---|---|
| Ollama (native) | Modules 1–2 only, before the Compose stack exists | `ollama --version` |
| llama.cpp / `llama-bench` | Measuring, Module 2 | `llama-bench --version` |
| Docker Engine + Compose | Everything from Module 3 | `docker version` and `docker compose version` |
| Python 3.10+ | `homelab.py doctor` and `homelab.py bench` | `python3 --version` |
| Tailscale or WireGuard | Module 11 remote access | `tailscale version` |

`homelab.py doctor` prints all of these, so you never have to remember.

## What to do when a version is released

1. Read the release notes. For a model server, a *minor* bump can change default flags.
2. Check whether the advisory list for that project mentions anything in your threat model —
   unauthenticated endpoints, path traversal, model-file parsers.
3. Bump **one** tag, not five.
4. `docker compose up -d`, then the smoke test: one chat message, one typed Assist command, one
   spoken command.
5. Re-run `python homelab.py bench --quick`. Software updates routinely move speeds by 10–20%, and
   that is worth a line in your table.
6. If anything breaks, `git checkout compose.yaml` and go back. A known-good stack beats a new one.

See [40 · Updates, CVEs and model supply chain](../lessons/module-11/lesson-04.md) for the reasoning
and [Update routine](../templates/update-routine.md) for the checklist.
