---
id: "08.2"
module: 8
minutes: 14
practice_minutes: 40
prerequisites: ["08.1"]
objectives:
  - >-
    Choose a speech-to-text engine and size for your machine using cited figures and your own
    measurements.
  - Measure transcription time on your own hardware, from a WAV file, without a microphone.
  - Explain the trade between Whisper and Speech-to-Phrase, and when each is the right answer.
volatility: implementation
sources:
  - title: "whisper.cpp — model memory requirements"
    url: https://github.com/ggml-org/whisper.cpp
  - title: "Speech-to-Phrase"
    url: https://github.com/OHF-voice/speech-to-phrase
  - title: "Home Assistant — setting up a fully local voice assistant"
    url: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
  - title: "faster-whisper"
    url: https://github.com/SYSTRAN/faster-whisper
last_verified: "2026-09-30"
---

# 08.2 · Speech-to-text on your CPU

Two engines, two different ideas about what speech recognition is for. Whisper will try to
transcribe anything; Speech-to-Phrase only recognises sentences you gave it, and is fast enough to
stay under a second on a Raspberry Pi. Picking the wrong one is either a slow assistant or a
useless one.

## Why it matters

Whisper's large sizes are the accuracy ceiling and also the reason people give up on local voice.
A `medium` model can take eight seconds per command on a Pi 4, and a household does not wait eight
seconds. The fix is not to give up on speech — it is to use the smallest model that recognises your
actual commands, and to measure it rather than assume.

The other half of the lesson is that you can do all of this from recorded files. Every lab here
starts from a WAV on disk, not from a microphone, and that is a deliberate choice: it removes the
audio layer from the problem so you can tell a transcription fault from a microphone fault.

## How it works

### Whisper: open-ended

| Model | File | RAM, cited | Character |
|---|---|---|---|
| `tiny` | ~75 MB | ~273 MB | Rough. Digits and short keywords |
| `base` | ~142 MB | ~388 MB | The default for a 16 GB machine |
| `small` | ~466 MB | ~852 MB | A real accuracy jump; the sweet spot on 32 GB |
| `medium` | ~1.5 GB | ~2.1 GB | Too slow for voice on most CPUs |

Memory figures are from the [whisper.cpp README](https://github.com/ggml-org/whisper.cpp). The speed
figures that matter are from Home Assistant's own documentation: Whisper takes **around eight
seconds per command on a Raspberry Pi 4** and **under a second on an Intel NUC**. That is a
twenty-fold difference across hardware, and it is the reason the default here is `base` and not
`medium`.

The faster-whisper README gives the same shape on a desktop: for 13 minutes of audio on an
i7-12700K with 8 threads, faster-whisper took 2 min 37 s in fp32, whisper.cpp took 2 min 05 s using
1.0 GB, and the reference `openai/whisper` implementation took 6 min 58 s using 2.3 GB. Roughly a
real-time factor of 0.26 against 0.53.

### Speech-to-Phrase: closed-ended

A different idea. Instead of transcribing speech, Speech-to-Phrase asks *which of the phrases I know
did you say?* It combines the sentence templates with the names of your exposed entities, areas and
floors, trains a small recogniser on them, and runs in **under a second even on a Pi 4** — Home
Assistant's own figure.

The cost is a fixed command set. Shopping lists, arbitrary timers and open questions do not work
out of the box, which is exactly the trade Home Assistant documents.

> [!IMPORTANT]
> Use the **multilingual** Whisper models, never the `.en` variants. The English-only models are
> smaller and marginally faster, which makes them very tempting, and they produce silent garbage
> on anything that is not English. The course is built Hebrew-ready and its lab samples are English
> only for now; an `.en` model would break that the moment anyone speaks another language.

### The comparison that actually decides it

| | Whisper `base` | Whisper `small` | Speech-to-Phrase |
|---|---|---|---|
| Needs training for your commands | no | no | yes, it learns your entity names |
| Handles an open question | yes | yes | no |
| Handles a bare entity name you invented | yes | yes | only if you added it |
| Speed on a Pi 4 | ~8 s per command | much slower | under 1 s |
| RAM | ~388 MB | ~852 MB | small |

The pattern the whole course converges on, visible already: **use the fast fixed path for the
commands, and reserve the slow general path for the questions.**

## Show me

The configuration, and where to change it:

```dotenv
# labs/common/.env
STT_MODEL=base
LANG_TAG=en
```

```bash
docker compose --profile voice up -d wyoming-whisper
docker compose --profile voice logs wyoming-whisper
```

Nothing else changes: the service, the port, the pipeline entry and Home Assistant's configuration
all stay the same whichever model you choose. That is the value of the Wyoming protocol doing its
job — a model swap is a one-word change in `.env`.

## Try it

1. Get a testable audio file without a microphone. The course can generate placeholders so every
   voice lab runs before you record anything:

   ```bash
   py -3 homelab.py make-samples      # Windows
   python3 homelab.py make-samples    # macOS / Linux
   ```

   Those are tones, not words — they prove the plumbing and nothing about accuracy. For real
   testing, record your own: any phone or voice recorder, 16 kHz mono WAV, a three-word command.
   Put it in `samples/en/commands/` next to the transcripts.

2. Measure the machine, not the impression. Time the same file at two sizes:

   ```bash
   # Windows PowerShell
   Measure-Command { docker compose --profile voice restart wyoming-whisper }

   # macOS / Linux
   time docker compose --profile voice restart wyoming-whisper
   ```

   Then change `STT_MODEL` in `.env` from `base` to `small`, restart, and repeat. Write both numbers
   in [measure-yours](../../templates/measure-yours.md).

3. Test accuracy, not just speed. Read out the same five commands three times each, at normal
   volume, from where you normally stand. Count how many Whisper got exactly right:

   ```text
   turn on the kitchen light
   what is the temperature in the bedroom
   set a timer for five minutes
   good night
   everything off
   ```

   `base` is genuinely weak on accents, background noise and unusual entity names. If it fails on
   your own voice and `small` does not, that is the answer, and it is a measurement.

4. Add Speech-to-Phrase alongside it and compare, without removing Whisper:

   ```bash
   docker run --rm --network homelab-voice rhasspy/wyoming-speech-to-phrase:1.3.0 \
     --model /data --prefix linux-x64 --download-dir /data --language en
   ```

   Discover it in Home Assistant, then create a second assistant using Speech-to-Phrase and run the
   same five commands. Time both. If Speech-to-Phrase wins on every one of them, you have found your
   default — for the fast path.

5. Measure the one number that decides the default: **the real-time factor.** Seconds of processing
   per second of audio. Under 1.0 is faster than live.

   ```bash
   # a three-second command should return in well under a second for a comfortable pipeline
   Measure-Command { docker compose --profile voice logs --tail=1 wyoming-whisper }
   ```

   On a slow ARM board, whisper.cpp real-time factors cited elsewhere in this course run 0.10 for
   `tiny`, 0.16 for `base`, 0.47 for `small` and 1.51 for `medium` — that is, `medium` is slower
   than real time, which is why it does not belong in a voice pipeline at all.

6. Write down your choice and the number behind it. That line is the capstone's voice criterion.

## Break it

**Break it with `medium`.** Set `STT_MODEL=medium` and talk. Everything still works, and everything
is slow enough that you will stop using it. There is no error, and no threshold crossed — just a
system that has become a demonstration.

**Break it with the `.en` models.** Whisper offers `base.en`, which is smaller and faster. Use it on
anything but English and it produces fluent, confident nonsense that the intent matcher then acts on.

**Break it with the wrong language setting.** Same failure, different cause: the language is set on
the service, and nothing tells you it is wrong.

**Break it by measuring with the microphone.** Record the same sentence five times with different
room noise and average them. You will conclude the model is inconsistent, when what you measured was
the room.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Transcript is wrong but confident | `.en` model, or wrong language | Use multilingual models; match `LANG_TAG` |
| Too slow for conversation | Model too large | `base` on 16 GB, `small` on 32 GB, or Speech-to-Phrase |
| Fine at the desk, poor across the room | Noise, or too small a model | Test with WAV files first; then `small` |
| Nothing is returned at all | Language download, or the container is not running | `docker compose --profile voice logs wyoming-whisper` |
| Entity names are misheard | `base` on unusual names | `small`, or add aliases and use Speech-to-Phrase |
| Fast but only works for some commands | Speech-to-Phrase's fixed set | Add custom sentences; keep Whisper for questions |

The general rule: **measure transcription from files before you blame the microphone, and size the
model from a real-time factor rather than from a memory table.**

## How do I know it works?

- [ ] You have a WAV file with a transcript beside it, and both are in `samples/en/commands/`.
- [ ] You have measured `base` and `small` on your machine and written both down.
- [ ] You have a real-time factor for your default, and it is comfortably under 1.0.
- [ ] You can name your default engine and the number that decided it.
- [ ] You are using a multilingual model and a language that matches what you speak.

## Use it when / avoid it

**Use Whisper `base` on a 16 GB machine and `small` on 32 GB.** Measure yours; those are starting
points derived from other people's hardware.

**Use Speech-to-Phrase for the fast path** if your commands are mostly control, especially on a
Raspberry Pi or an N100. It is fast enough to change the feel of the whole system.

**Keep Whisper even if Speech-to-Phrase wins.** Questions are not a fixed list, and the two paths
together are what Module 10 is built around.

**Avoid `medium` and above in a voice pipeline** on a CPU. Being slower than real time is not a
performance problem you tune; it is the wrong model for the job.

> [!TIP]
> **If you have a GPU.** This lesson changes character completely: Whisper's larger models become
> viable because the bottleneck was never the CPU. Every number here is CPU-bound, and none of them
> should be compared with a GPU result without saying so.

## Reflect

1. What real-time factor did you measure, at which model, on which machine? Would it fit a
   two-second budget?
2. Which of your five test commands did the smaller model get wrong, and would an alias or a
   custom sentence have been a cheaper fix?
3. What proportion of your household's commands are control rather than questions? That number is
   your argument for Speech-to-Phrase.

## Sources

- [whisper.cpp — model memory requirements](https://github.com/ggml-org/whisper.cpp)
- [Speech-to-Phrase](https://github.com/OHF-voice/speech-to-phrase)
- [Home Assistant — setting up a fully local voice assistant](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- [Pinned models and licences](../../references/models.md)
- [29 · Measure the voice pipeline](lesson-04.md)