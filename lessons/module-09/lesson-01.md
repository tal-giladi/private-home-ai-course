---
id: "09.1"
module: 9
minutes: 12
practice_minutes: 35
prerequisites: ["08.1"]
objectives:
  - Explain what a wake word does and why it is the step most likely to make people give up.
  - >-
    Compare false accepts and false rejects, and measure both on your own voice in a real room.
  - Choose between openWakeWord and a micro model on the evidence rather than on a leaderboard.
volatility: implementation
sources:
  - title: "openWakeWord README"
    url: https://github.com/dscripka/openWakeWord
  - title: "Home Assistant — the approach to wake words"
    url: https://www.home-assistant.io/voice_control/about_wake_word/
last_verified: "2026-09-30"
---

# 09.1 · Wake words that do not lie to you

A wake word is a small model that listens continuously and decides whether one particular phrase was
just said. It is the least impressive component in the pipeline and the one most likely to end your
project, because it is the only stage that runs when nobody is talking and therefore the only stage
whose failures you cannot ignore.

## Why it matters

There are exactly two ways a wake word can be wrong, and they are opposites:

| | Meaning | What it feels like |
|---|---|---|
| **False accept** | It fired when nobody said it | The assistant is talking to itself at 2 a.m. |
| **False reject** | It did not fire when you said it | You say the phrase again, louder, annoyed, twice |

Both destroy a household's willingness to use the thing, and they are measured on completely
different distributions. The numbers people quote — openWakeWord's README targets fewer than 0.5
false accepts per hour and fewer than 5% false rejects — are for a trained model in a quiet room.
Your kitchen is not a quiet room.

The useful thing to understand is that you can trade one for the other. Raising sensitivity fixes
false rejects and makes false accepts worse; lowering it does the reverse. That is the knob, and
this lesson is about turning it against your own measurements.

## How it works

### How it listens all day without noticing

Running a language model on every audio frame would be absurd. Wake word detection uses a much
cheaper method: a small neural network on short windows of audio, run at a modest sample rate,
looking for a fixed spectral signature rather than for words. openWakeWord's README reports that
one Raspberry Pi 3 core runs fifteen to twenty of its models in real time, which is the number that
makes an always-on listener possible at all.

Because it runs continuously, it is also the only component that consumes CPU with nobody talking —
which is a Module 12 power question and a "turn it off when you leave" question.

### Two families of model

| | openWakeWord | microWakeWord |
|---|---|---|
| What | A bundle of ~20 prebuilt models, plus custom ones you can train | One much smaller model, per keyword |
| Training | Few hours of your own audio produces a "verified" model | Faster and simpler |
| Targets | < 0.5 false accepts/hour, < 5% false rejects, for a verified model | Varies; generally fewer accepts, more misses |
| CPU cost | One core can run ~20 models | Cheaper per model |

Prebuilt models are trained on public audio and will mostly work; a custom model trained on your own
voice is the one that recognises you at a whisper and does not fire on the television.

> [!NOTE]
> Prebuilt openWakeWord models are **not** fully verified. The project's own README is explicit that
> the public prebuilt models are known to produce more false accepts than the stated targets, and
> that training your own is the way to get the numbers the README advertises. Take that seriously:
> it is the difference between an assistant people keep and one they turn off.

### Wake word versus hot word versus press-to-talk

Worth deciding early, because all three are legitimate and they have very different failure modes:

- **Wake word**: hands-free, needs a false-accept rate low enough to sleep next to.
- **Hot word**: a harder phrase, said deliberately, trained specifically. Fewer false accepts,
  more false rejects.
- **Press-to-talk or a button on a dashboard**: no wake word at all. Zero false accepts, and it
  works perfectly on a machine too small to run one.

Press-to-talk is the right answer for a lot of people, and it is the one nobody tries first.

## Show me

The configuration, again one line in `.env`:

```dotenv
# labs/common/.env
WAKE_MODEL=hey_jason      # or whatever you chose
```

```yaml
  wyoming-openwakeword:
    image: rhasspy/wyoming-openwakeword:1.1.0
    command: ["--preload-model", "${WAKE_MODEL:-hey_jason}"]
    networks: [voice]
    deploy:
      resources:
        limits:
          memory: 256m
```

Note the tight memory limit and the absence of any volume: wake word models are small and can be
re-downloaded, unlike the speech models. This is the cheapest component in the stack and the one
with the most ways to be wrong.

## Try it

1. Measure the false-accept rate before you measure anything else, because it is the number that
   decides whether the feature survives. Leave the wake word service running for an hour in a
   normal room with the television on and people talking, and count how many times it fires without
   being spoken to:

   ```text
   Test 1: sitting room, TV on, 60 minutes            → __ false accepts
   Test 2: kitchen, extractor fan on, 60 minutes      → __ false accepts
   Test 3: same room, nothing else on, 60 minutes     → __ false accepts
   ```

   Three numbers, written down, against the target of fewer than 0.5 per hour. If Test 3 fails,
   the problem is your room; if Test 3 passes and Test 2 fails, it is your kitchen.

2. Measure the false-reject rate next, which is faster: say the phrase twenty times from where you
   normally stand, at normal volume, and count:

   ```text
   From where I stand while cooking:  __ / 20 recognised
   From across the room:             __ / 20 recognised
   From the sofa, TV on:             __ / 20 recognised
   ```

3. Now trade one against the other. Raise the detection threshold and re-measure both. Write all
   six numbers in a small table:

   | Threshold | False accepts/hour | False rejects |
   |---|---|---|
   | default | | |
   | raised | | |
   | lowered | | |

   The setting you want is the one where accepts are near zero and rejects are under about 5%.

4. If the numbers are not good enough, train a custom model. openWakeWord's approach is to record
   a few hours of your own voice, including the positive examples, negatives, and background noise
   at the volume you will actually use. That is a weekend, and it is the difference between "it
   mostly works" and "it works".

5. Consider hot word or press-to-talk as the honest alternative. A phrase like "computer, tidy up"
   or a dashboard button has a far lower false-accept rate than "hey jarvis", and the cost is that
   you have to say it deliberately.

6. Write down both numbers and the setting you chose. This is a capstone criterion.

## Break it

**Break it with a prebuilt model in a noisy room.** It fires at the television, or at a washing
machine spin cycle, or at the cat. Two false accepts in a night is enough for a household to
disable it, and they will not tell you why.

**Break it by making it too sensitive.** Drop the threshold until it recognises you from the
garden, and it now fires at every door closing. The fix and the disease feel similar, which is why
you measure both numbers.

**Break it by training on clean audio only.** A custom model trained on a quiet desk will miss you
in a kitchen with an extractor fan. Include the noise, or the model will learn that the noise means
"not the wake word".

**Break it by running it always.** It is cheap, it is quiet, and it is always listening. On a
laptop that is a battery cost; on a box by your bed it is a light that never goes off. Module 12
measures the idle watts.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Fires when nobody speaks | Prebuilt model, or threshold too low | Raise the threshold; train a custom model; use a hot word |
| Ignores you | Threshold too high, or a model not trained on your voice | Lower it; record and train |
| Works at the desk, not across the room | Not trained on your real distances and room noise | Train with the noise and the distances |
| Works alone, fails with the television on | No negatives in training | Record several hours including the television |
| Fine, but the laptop runs hot | It runs continuously | Accept it, or use press-to-talk |
| Words get cut off after the wake word | The satellite's audio buffer starts too late | Increase the pre-roll buffer |

The last row is worth knowing: a wake word detector has to keep a little audio *before* the
detection, or the first syllable of the command is already gone.

## How do I know it works?

- [ ] You have a false-accept count per hour for three rooms.
- [ ] You have a false-reject count out of twenty, from three positions.
- [ ] You have a threshold setting chosen from those six numbers.
- [ ] You have decided, in writing, between a wake word, a hot word and press-to-talk.
- [ ] You know what the CPU and idle power cost of an always-listening box is.

## Use it when / avoid it

**Use a wake word** when hands-free operation is the point and you have measured the false-accept
rate in your actual rooms.

**Use a hot word** when you want hands-free but would accept saying something deliberate. A longer,
harder phrase has a much lower false-accept rate and it costs you nothing but a little more
ceremony.

**Use press-to-talk when the machine is small.** A Raspberry Pi 5 with 8 GB can run an entire voice
pipeline and cannot afford an always-on wake word listener at the same time. A dashboard button
costs one RAM budget and has a zero false-accept rate.

**Do not train on clean audio.** The negatives are the training.

> [!NOTE]
> Voice PE and the ESP32 satellites in the next lesson do this listening in hardware, which changes
> the trade: they are cheap and always on, and they depend entirely on your model being right.

## Reflect

1. What is your false-accept rate in the room where you would actually put the microphone?
2. At what threshold does your false-reject rate get unacceptable, and what is your accept rate at
   that point?
3. Which of the three options — wake word, hot word, press-to-talk — would your household actually
   keep using, and what measurement decided it?

## Sources

- [openWakeWord README — targets and custom training](https://github.com/dscripka/openWakeWord)
- [Home Assistant — the approach to wake words](https://www.home-assistant.io/voice_control/about_wake_word/)
- [Home Assistant — wake words for Assist](https://www.home-assistant.io/voice_control/create_wake_word/)
- [Pinned versions](../../references/versions.md)
- [31 · Your laptop as a voice satellite](lesson-02.md)
- [41 · Always-on without starving the voice pipeline](../module-12/lesson-01.md)