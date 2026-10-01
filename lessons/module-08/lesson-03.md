---
id: "08.3"
module: 8
minutes: 11
practice_minutes: 30
prerequisites: ["08.2"]
objectives:
  - Choose a Piper voice on quality, size and licence, and explain why the voice is a separate choice.
  - >-
    Stream a reply so the first audio arrives before the sentence is finished, and measure the
    time to first sound.
volatility: implementation
sources:
  - title: "Piper voices repository"
    url: https://github.com/rhasspy/piper-voices
  - title: "Piper — current release (GPL)"
    url: https://github.com/OHF-Voice/piper1-gpl
  - title: "Home Assistant — using Piper in automations"
    url: https://www.home-assistant.io/voice_control/using_tts_in_automation/
last_verified: "2026-09-30"
---

# 08.3 · Text-to-speech with Piper

The stage nobody thinks about until it is wrong. Piper is fast enough that it is not usually the
bottleneck, and the interesting decisions are about voice choice, about licensing, and about
whether the reply starts arriving before the sentence has finished.

## Why it matters

Two reasons, and the second is the one people get wrong.

The first is that it is a quarter of the latency budget. Home Assistant's own figure is that medium
quality Piper voices generate about 1.6 seconds of audio per second on a Raspberry Pi — fast enough
that it is not your bottleneck on decent hardware, slow enough to matter on a weak one.

The second is licensing. A voice is not a sample; it is a recorded work licensed separately from the
engine that speaks it. The course's model list is careful about this and this lesson explains why
it has to be.

## How it works

### Voices are the product

The engine is the same for every voice. What you actually hear — accent, warmth, clarity, the
presence or absence of any particular affect — is a set of weights downloaded separately. Piper's
repository has hundreds of them, contributed by people, under different licences.

| Voice | Character | Size |
|---|---|---|
| `en_US-lessac-medium` | The default: clear, neutral, pleasant | ~60 MB |
| `en_US-amy-medium` | Clearer, slightly slower | ~60 MB |
| `en_GB-alba-medium` | Scottish English | ~60 MB |
| `en_US-hfc_female-medium` | Natural cadence, less synthetic | ~60 MB |

**Licences differ per voice.** Some are MIT, some are CC-BY, and community-donated voices carry
whatever their donor chose. The [piper-voices repository](https://github.com/rhasspy/piper-voices)
carries a model card per voice; read that one, not the engine's licence. Also worth knowing: Piper's
active release moved to a GPL-licensed project separate from the original MIT code — irrelevant for
running at home, relevant if you ever redistribute a binary.

### Quality levels

Piper ships voices in several quality tiers. `low` is fast and noticeably robotic; `medium` is the
sensible default; `high` is slower than you want in a pipeline and not obviously better for short
replies. For a voice assistant saying "the kitchen light is on", medium is enough, and the size
difference matters on an 8 GB machine.

### Time to first audio

The number that matters is not total synthesis time. It is how long until the first sound comes
out. Piper streams: it can begin playing audio while it is still synthesising the rest of the
sentence. That is why a reply feels like it starts immediately even when the whole sentence takes
half a second to synthesise.

If your interface waits for the whole sentence before playing anything, that is a client
behaviour, not Piper, and it is worth half a second of your users' attention.

## Show me

The configuration, again one line in `.env`:

```dotenv
TTS_VOICE=en_US-lessac-medium
```

```yaml
  wyoming-piper:
    image: rhasspy/wyoming-piper:1.3.0
    command: ["--voice", "${TTS_VOICE:-en_US-lessac-medium}", "--download-dir", "/data"]
    volumes: [piper-voices:/data]
    networks: [voice]
```

And the check, which is the only way to know a voice is right for your household:

```text
Turn the kitchen light on.
It is 18 degrees in the hallway.
I could not find that in your files.
Sorry, I did not understand that.
```

The fourth sentence is the one to listen to carefully. It is what a refusal sounds like, and a
household can tell within a day whether it sounds like a person declining or like a machine failing.

## Try it

1. Start Piper and let it download the voice:

   ```bash
   docker compose --profile voice up -d wyoming-piper
   docker compose --profile voice logs wyoming-piper
   ```

   The first start fetches roughly 60 MB. It is stored in a volume, so this is once.

2. Listen to the default before you change it. In **Developer Tools → Assist**, type a sentence
   and play the reply. Judge it on the four sentences above, not on a greeting.

3. Try two alternatives and compare honestly:

   ```dotenv
   TTS_VOICE=en_US-amy-medium
   ```

   ```bash
   docker compose --profile voice up -d wyoming-piper
   ```

   Repeat for `hfc_female-medium`. Three voices and ten minutes, and you will have an opinion you
   can defend — which is the only way this decision should be made.

4. Measure time to first audio, which is the number in the latency budget:

   ```bash
   # Windows PowerShell
   Measure-Command { docker compose --profile voice logs --tail=1 wyoming-piper }

   # macOS / Linux
   time docker compose --profile voice logs --tail=1 wyoming-piper
   ```

   For a more meaningful number, synthesise a long sentence rather than a one-word reply — a short
   reply is too fast to measure on its own. Write the figure in your
   [latency budget](../../templates/latency-budget.md).

5. Check the licence before you settle:

   ```bash
   # Look at the model card for the exact voice you chose, not the engine's README.
   ```

   Record it in your notes. This is thirty seconds now and it is the thing you would otherwise
   forget to do before showing the setup to somebody.

6. Compare quality tiers once, if your machine has RAM to spare. `medium` against `high` for the
   same four sentences. If you cannot hear the difference in a voice assistant saying short status
   replies, stay on `medium` and keep the memory.

## Break it

**Break it with a voice nobody in the house recognises.** Pick a voice because it is technically
good. An assistant that sounds wrong is an assistant the household stops speaking to, and that
failure is not measurable in a benchmark.

**Break it with `high` quality on an 8 GB machine.** It works, and it takes memory and time that
Whisper needed. "The machine is slow" is the symptom; voice quality is the cause.

**Break it by buffering.** Configure a client to wait for the whole sentence before playing. The
reply now takes noticeably longer for no reason, and the cause is not Piper.

**Break it by redistributing without reading the licence.** A community voice with a CC-BY
requirement is fine to use at home and not fine to ship. This is the failure from lesson 05.3
appearing in a place nobody expected.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| No sound | The voice did not download, or the volume is zero | `docker compose --profile voice logs wyoming-piper` |
| Reply starts late | The client buffers the whole sentence | Enable streaming in the client |
| TTS is the slowest stage | Quality tier too high for the machine | Use `medium` |
| Voice sounds wrong for the household | Wrong voice choice | Try three, listen to a refusal, pick with everyone in the room |
| Reply is chopped off | A sentence that is too long for the stream | Shorten the response text |
| The voice is unavailable after a rebuild | The voice lives in a volume, not in the image | It should persist; check the volume is mounted |

## How do I know it works?

- [ ] A spoken reply comes out of the pipeline and starts promptly.
- [ ] You have listened to a refusal, not just a success.
- [ ] You have a time-to-first-audio figure in your [latency budget](../../templates/latency-budget.md).
- [ ] You have recorded the licence of the voice you chose.
- [ ] Someone else in the household has heard it and not complained.

## Use it when / avoid it

**Use `medium` quality and a voice the household recognises.** Both defaults are defensible and both
are cheap.

**Use streaming.** Time to first audio is the metric, not total synthesis time.

**Read each voice's licence.** It is thirty seconds, and it is the difference between using a voice
and being able to say you may.

**Do not spend memory on quality tier you cannot hear.** A `high` voice saying "the light is on" is
indistinguishable from a `medium` one and costs more.

> [!NOTE]
> Hebrew voices for Piper are scarce and mostly community-contributed, with licences that vary. The
> course's English samples are labelled by language in `labs/common/samples/en/` precisely so a
> later `he/` folder can be added with the same file names and no code changes.

## Reflect

1. Which voice did you pick, what convinced you, and had anyone else heard it?
2. What is your time to first audio, and would a different quality tier change it enough to matter?
3. If you wanted to give this voice assistant to a friend, what would you have to check that you did
   not have to check for yourself?

## Sources

- [Piper voices repository — per-voice licences](https://github.com/rhasspy/piper-voices)
- [Piper — current release (GPL)](https://github.com/OHF-Voice/piper1-gpl)
- [Home Assistant — using Piper in automations](https://www.home-assistant.io/voice_control/using_tts_in_automation/)
- [Latency budget template](../../templates/latency-budget.md)
- [05.3 · Licences and trusted sources](../module-05/lesson-03.md)
- [29 · Measure the voice pipeline](lesson-04.md)