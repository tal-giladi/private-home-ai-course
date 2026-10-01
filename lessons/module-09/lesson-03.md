---
id: "09.3"
module: 9
minutes: 9
practice_minutes: 20
prerequisites: ["09.2"]
objectives:
  - >-
    Describe what dedicated voice hardware changes about a home setup, and what it does not change.
  - Decide honestly whether buying a voice satellite is worth anything at this point.
  - Run a complete voice command on hardware you already own, without buying anything.
volatility: concept
sources:
  - title: "Home Assistant Voice Preview Edition"
    url: https://www.home-assistant.io/voice-pe/
  - title: "Home Assistant — ESP32-S3-BOX voice assistant tutorial"
    url: https://www.home-assistant.io/voice_control/s3_box_voice_assistant/
  - title: "Voice Chapter 9 — Speech-to-Phrase"
    url: https://www.home-assistant.io/blog/2025/02/13/voice-chapter-9-speech-to-phrase/
last_verified: "2026-09-30"
---

# 09.3 · Optional: Voice Preview Edition and ESP32 satellites

Two kinds of dedicated hardware: a finished product that runs Home Assistant's own voice software
and a microcontroller you flash yourself. Neither is needed for anything in this course, and this
lesson is short on purpose — its job is to tell you what they change, so you can decide with your
eyes open rather than feeling obliged.

## Why it matters

A satellite on your laptop works until the laptop lid closes. A dedicated satellite works always, in
every room, and costs a fixed amount of money once. That is a real trade, and it is worth naming
even though the course's answer is "not yet".

The reason to read this lesson before buying is that hardware does not fix the two problems most
people actually have. A $69 satellite does not improve your false-accept rate — it changes where the
microphone is. And it does not make a small model smarter, so the model work in Module 10 still has
to happen.

## How it works

### Voice Preview Edition

A finished device: a small box with a microphone, a speaker and an on-device wake word detector,
designed to be a satellite for your own Home Assistant instance. Roughly $69 at time of writing.

What it changes:

- **Always available**, and physically in a room rather than on a desk.
- **Its own microphone and speaker**, so your laptop can be closed.
- **Runs the wake word on the device**, which is the point — the audio only leaves when the wake
  word fires.

What it does not change:

- Your transcription accuracy, which is the speech model on your box.
- Your model's misfire rate.
- Anything about your network exposure.

### ESP32 satellites

An ESP32-S3 board with a microphone and amplifier, flashed with firmware that does the same job:
wake word on the chip, audio streamed to your instance over Wi-Fi. Home Assistant publishes a
tutorial for the ESP32-S3-BOX.

What it changes: the same as above, except you assemble it yourself and you can put it anywhere.
What it adds: the cost is your time and a soldering iron, and the firmware is community-maintained.

> [!IMPORTANT]
> Neither device is a requirement of this course, and neither unlocks a capstone criterion. Every
> lab in Modules 7 to 10 is completed with a laptop microphone or with typed input, and the
> capstone rubric accepts a typed-command pipeline plus a text-to-speech output check. If you are
> reading this to decide whether to buy something before starting: start with nothing.

## Show me

The comparison, at the point where you would decide:

| | Laptop satellite | Voice PE | ESP32 satellite |
|---|---|---|---|
| Cost | none | ~$69 | ~$20–40 plus parts |
| Always on | no, unless you configure power | yes | yes |
| Wake word in hardware | no | **yes** | **yes** |
| Audio leaves the device when idle | n/a (it is the server) | no | no |
| Setup time | minutes | minutes | an afternoon |
| Fits in every room | no | yes, cheaply | yes, cheaply |
| Needs this course | yes | no | no |

The row that matters is "wake word in hardware". A dedicated device is not buying better speech; it
is buying a wake word detector that runs on a chip, which means it can be in three rooms and cost
almost nothing in power.

## Try it

1. Do not buy anything yet. Finish Module 10 and measure your misfire rate on your own hardware.
   That number is what tells you whether the problem you have is the model or the microphone.

2. If you already have one of these devices, use it as a satellite rather than running its own
   software stack. Point it at your Home Assistant instance and leave the wake word on the device.

3. Run the full thirty-command set from [the sample folder](../../labs/common/) on hardware you own
   now. Write down, for each: did it hear you, did it understand you, did it do the right thing.
   Three separate columns, because they have three different causes.

4. If your columns are: hearing is poor, understanding is fine, doing is fine — you have a
   microphone placement problem and hardware would genuinely help.

5. If your columns are: hearing is fine, understanding is fine, doing is often wrong — hardware will
   not help at all, and Module 10 is where your time belongs.

6. Come back to this lesson after the capstone. At that point you will know what your stack cannot
   do, and you will be buying for a specific reason rather than for the idea of a voice assistant.

## Break it

**Break it by buying first.** The most common expensive mistake in a home AI project: hardware
arrives, it works, and the system is still wrong in exactly the way it was before, because the
problem was the model's decisions rather than the microphone's position.

**Break it by running a second Home Assistant on the device.** Voice PE and the ESP32 firmware both
offer a standalone mode with their own instance. Running that plus the stack you built gives you
two systems with different entity names and an afternoon of confusion.

**Break it by assuming the wake word gets better.** Hardware wake word detection is more consistent
than a laptop microphone's, and it is still the same class of false-accept problem.

## Fix it

| Symptom | What actually helps |
|---|---|
| The laptop lid closes and the assistant stops | Dedicated satellite, or power settings |
| The assistant does not hear from across the room | Microphone placement first, hardware second |
| The assistant hears but misunderstands | A bigger speech model, not a better microphone |
| The assistant hears and understands but does the wrong thing | Module 10: a different model, fewer entities, intents first |
| The assistant works but only in one room | This lesson, once you have finished Module 10 |

The last column is the useful one: every row has a cheaper fix that is not hardware, and hardware
only appears once those have been ruled out.

## How do I know it works?

- [ ] You have finished Module 10 and have a misfire rate for your own hardware.
- [ ] You can name which of hearing, understanding and doing is your weakest link.
- [ ] You have a written decision: buy hardware now, or wait, with your measurement as the reason.
- [ ] Every lab in the course has been completed without buying anything.

## Use it when / avoid it

**Buy a dedicated satellite** when your stack works and the limitation is that it only listens in
one place, or only while a laptop is open. That is a genuine, specific problem and about $69 fixes
it.

**Do not buy anything before finishing Module 10.** The measurement you would make afterwards is
the thing that tells you whether hardware helps, and it takes an hour instead of a purchase.

**Do not run a standalone instance on the device.** Point it at the stack you built.

**Remember that hardware is optional throughout.** This course, its labs and its capstone are
complete without a purchase, and the accessibility routes exist for a reason.

> [!TIP]
> Home Assistant's own minimum for full local Whisper is an Intel N100-class CPU — which is also the
> class of machine this course's tier C path targets, and costs less than a dedicated satellite. If
> your limitation is speed, that is the cheaper place to spend money.

## Reflect

1. Which of hearing, understanding and doing is weakest in your own setup right now?
2. What would dedicated hardware change, and what would it leave exactly as it is?
3. What evidence would you need before buying anything — and do you have it yet?

## Sources

- [Home Assistant Voice Preview Edition](https://www.home-assistant.io/voice-pe/)
- [Home Assistant — ESP32-S3-BOX voice assistant tutorial](https://www.home-assistant.io/voice_control/s3_box_voice_assistant/)
- [Voice Chapter 9 — Speech-to-Phrase and minimum hardware](https://www.home-assistant.io/blog/2025/02/13/voice-chapter-9-speech-to-phrase/)
- [Sample command set](../../labs/common/)
- [03.1 · Choose the host](../module-03/lesson-01.md)
- [35 · Tools and guardrails](../module-10/lesson-03.md)