# Shared lab code

This folder is added to every module's download. You do not need to run anything in it before
Module 0 — `doctor` in Module 0 is the first thing that uses it.

```
common/
  homelab.py                 the two commands the whole course runs on
  compose.yaml               the stack, one file, grown by profiles
  .env.example               copy to .env; it holds YOUR numbers, so it is gitignored
  samples/en/                fictional household documents, questions, demo entities, commands
  README.md                  this file
```

## homelab.py

Python 3.10 or newer. **Standard library only** — no `pip install`, no virtual environment, nothing
to break.

```bash
python homelab.py doctor          # what machine is this, which tier, which model to start with
python homelab.py bench           # prompt and generation speed, peak RAM, voice samples
python homelab.py bench --quick   # same, without the voice section
python homelab.py make-samples    # generate placeholder WAVs so voice labs can run
```

If `python` is not found, try `python3` (Linux, macOS) or `py -3` (Windows).

`doctor` only reads. It checks the operating system, CPU, cores, RAM, memory channels where the
platform will say, free disk, Docker and Compose, whether Ollama answers on `127.0.0.1`, whether a
microphone exists, which stack ports are listening, and — the line that matters most — whether any
of them is reachable from another device on your network. It ends with a tier and a recommended
first model.

`bench` sends two prompts to the model server you already run and prints a table you can paste into
[the measure-yours template](../../../templates/measure-yours.md). It measures prompt throughput
and generation throughput separately, because they are limited by different things and the course
treats them differently.

## compose.yaml

| Command | What starts |
|---|---|
| `docker compose up -d` | model server + chat interface (the core stack) |
| `docker compose --profile rag up -d` | + vector store, for Module 6 |
| `docker compose --profile voice up -d` | + speech-to-text, text-to-speech, wake word |
| `docker compose --profile secure up -d` | + the isolated exposure lab, Module 11 |
| `docker compose down` | stops everything, **keeps** your data |
| `docker compose down -v` | stops everything and **deletes** the volumes — read this twice |

Every image is pinned to an exact tag. The model server and Home Assistant publish no host port at
all. The only published port is the chat interface, on `127.0.0.1` by default. Module 11 explains
why, and is the one lesson that changes it.

## .env

```bash
cp .env.example .env          # Linux / macOS
Copy-Item .env.example .env   # Windows PowerShell
```

`.env` is gitignored and must stay that way. It holds your model choices and your memory limits —
numbers that are true of your machine and nobody else's. The two that matter most on a small
machine are `OLLAMA_MEMORY_LIMIT` and `WEBUI_MEMORY_LIMIT`; Module 2 works out what they should be
for you.

## samples/en

Fictional household documents, ten labelled questions, thirty voice commands for the misfire test,
demo Home Assistant entities and custom sentences. Everything invented, so it is safe to index, and
small enough to read.

`home/` in a later version of the course holds the same file names in Hebrew. Nothing in the labs
hard-codes a language: one `LANG_TAG` in `.env` picks the Whisper language, the Home Assistant
language and the sample folder.

## Problems

Start with `python homelab.py doctor` and read the whole output, not the first line. The
[troubleshooting page](../../../references/troubleshooting.md) is organised by symptom and covers
Windows, macOS and Linux.
