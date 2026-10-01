---
id: "09.2"
module: 9
minutes: 12
practice_minutes: 40
prerequisites: ["09.1", "08.1"]
objectives:
  - >-
    Run a Wyoming satellite natively on the host, connect it to Home Assistant over the internal
    network, and speak a command end to end.
  - Explain why the satellite is the only component that runs outside Docker.
  - >-
    Complete a spoken command without any microphone, using WAV files, so the pipeline is testable
    at every stage.
volatility: implementation
sources:
  - title: "Wyoming satellite (rhasspy)"
    url: https://github.com/rhasspy/wyoming-satellite
  - title: "Home Assistant — Wyoming integration"
    url: https://www.home-assistant.io/integrations/wyoming
  - title: "Wyoming protocol"
    url: https://github.com/rhasspy/wyoming
last_verified: "2026-09-30"
---

# 09.2 · Your laptop as a voice satellite

The last missing piece is the part that listens. The satellite runs on your host — it is the one
component that needs a microphone — and this lesson gets a spoken command from your mouth to a
changed light without buying anything.

## Why it matters

Everything so far has been typed or file-driven, deliberately, so that a failure could be localised.
This lesson removes the last abstraction. It is also the first moment the whole stack is a single
thing a person in your house can use, and the first moment you find out whether your latency
budget survives contact with a real microphone.

The satellite is a small program with one job: listen for the wake word, and when it fires, stream
the audio that followed it to Home Assistant over the Wyoming protocol. It also detects the end of
speech, which is the stage whose cost everybody forgets.

## How it works

### What the satellite does

```text
microphone → wake word detector → (fires) → ring buffer of the last ~2 seconds
                                                        ↓
                                            stream audio + timestamps to Home Assistant
                                                        ↓
                              Home Assistant: speech-to-text → intent → text-to-speech
```

Three things happen there and nowhere else:

1. **Wake word detection**, in the satellite, on the host.
2. **End-of-speech detection**, also in the satellite. This is where the "it cut me off" and "it
   waited forever" bugs live.
3. **Audio streaming**, with the pre-roll buffer that lesson 09.1 referred to.

Everything after the stream — transcription, intents, speech — is already running in containers
that you never have to look at again.

### Why it runs on the host

Recap from lesson 08.1, because it is the design decision that matters here: audio can be passed
*into* a container, but a container cannot simply open a laptop's microphone. Doing it needs a
virtual audio device and, on Windows, a permission dance. The microphone belongs to the operating
system; the services that never touch hardware belong in Compose.

### Reaching Home Assistant from the host

The satellite is on the host; Home Assistant is in a container that publishes no port. Three
options, and only the first is the one to use:

| Option | How | Verdict |
|---|---|---|
| **Docker bridge gateway** | Point the satellite at the container's IP or `host.docker.internal` | Works, but the IP can change |
| **Publish Home Assistant's port** | `"127.0.0.1:8123:8123"` | Works, and it is the thing Module 11 is about |
| **`network_mode: host` on a satellite container** | Satellite in Docker, sharing the host network | Works on Linux; awkward on Docker Desktop |

Use the bound port you already added in lesson 07.1 — on loopback — and point the satellite at
`127.0.0.1:8123`. That is the whole reason the course asked you to publish it *deliberately*: it is
needed here, on loopback only, and Module 11 explains what happens if you widen it.

### The text-only route, again

If you cannot use a microphone — or you do not want to, today — the pipeline is already testable
from files. Every measurement in Module 8 was made that way, and a spoken-command lab that cannot
be done by typing is a lab with a microphone problem in it.

## Show me

The configuration and the command:

```bash
# Windows PowerShell — from the host, not from inside a container
wyoming-satellite --mic-pulseaudio --audio-device default \
  --wake-word hey_jason --uri tcp://0.0.0.0:10300

# macOS
wyoming-satellite --mic-alsa --audio-device default \
  --wake-word hey_jason --uri tcp://0.0.0.0:10300
```

Note `--uri tcp://0.0.0.0:10300`. That is **not** Home Assistant — it is the wake word service on the
voice network, and the satellite finds it by discovery. The satellite publishes *itself* on
`10300` so Home Assistant can send audio back out to your speakers; that is the only port this
lesson adds, and it is why one is acceptable.

## Try it

1. Confirm the four containers are up and Home Assistant has discovered them:

   ```bash
   docker compose --profile voice ps
   ```

   Whisper, Piper and the wake word service should be there, and Home Assistant should have added
   two Wyoming integrations.

2. Install the satellite on the host. It is a single Python package:

   ```bash
   py -3 -m pip install wyoming-satellite      # Windows
   python3 -m pip install wyoming-satellite    # macOS / Linux
   ```

3. Point Home Assistant at it. In your voice assistant's configuration, the **Wake word** stage
   should show the openWakeWord service once it has been discovered. Run the pipeline from
   **Developer Tools → Assist** with "test sentence" input if you want to verify the other stages
   without speaking.

4. Start the satellite, with a microphone argument that matches your platform:

   ```bash
   # Windows PowerShell
   wyoming-satellite --mic-pulseaudio --audio-device default `
     --wake-word hey_jason --uri tcp://0.0.0.0:10300

   # macOS
   wyoming-satellite --mic-alsa --audio-device default `
     --wake-word hey_jason --uri tcp://0.0.0.0:10300

   # Linux with PipeWire
   wyoming-satellite --mic-pulseaudio --audio-device default `
     --wake-word hey_jason --uri tcp://0.0.0.0:10300
   ```

   The first argument is the most common failure point, and each platform names its microphone
   system differently.

5. Say the wake word, then "turn on the kitchen light", and watch the dashboard. **Write down the
   gap** between finishing the sentence and the light coming on. That is your real end-to-end
   latency, including the microphone, and it is the number Module 8's table was preparing you for.

6. Do the same for a question, with the conversation agent still set to "Home Assistant" — built-in
   intents only. Then set it to a model and repeat. Now you have both paths measured through a real
   microphone, which is the comparison that matters.

7. Run the thirty-command set spoken. If a microphone is not available or not wanted, run it typed:
   the misfire measurement in Module 10 is about the assistant's decisions, and removing the speech
   stage makes that measurement cleaner.

## Break it

**Break it with the wrong microphone argument.** On Linux, `--mic-alsa` against a PulseAudio or
PipeWire system produces silence rather than an error. The satellite runs, it never hears anything,
and every failure looks like a wake word problem.

**Break it by launching it twice.** A second satellite cannot bind port 10300 and exits. The symptom
is a satellite that connects and then goes silent, which also happens when a container is already
using that port.

**Break it with a container-based microphone.** If you try to put the satellite in Docker with
`--mic-pulseaudio`, you get either silence or a device that belongs to the VM, not your laptop. This
is the lesson's actual content, and experiencing it once explains the design.

**Break it by setting a very low silence threshold.** The satellite decides you have finished after
half a syllable, and you get "turn on the kitch—" three times in a row. Raise it; the cost is
latency and nothing else.

**Break it by opening the port more widely.** Change `--uri` from `0.0.0.0` to a LAN address or add
a firewall rule "just for testing". Now anyone on your Wi-Fi can stream audio into your home
automation. Module 11 is the lesson about not doing that.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Satellite runs, hears nothing | Wrong microphone argument for the platform | Try `--mic-pulseaudio`, then `--mic-alsa` |
| Binds to 10300 and exits | Another satellite is already running | Find it, stop it, run one |
| Cuts off mid-sentence | Silence threshold too low | Raise it; expect a little more latency |
| Waits several seconds after you stop | Silence threshold too high, or noise floor set wrong | Lower it slightly; check for a fan |
| Misses the first word | Pre-roll buffer too short | Increase it |
| Nothing is heard on the speakers | The satellite cannot open the output device | Test the output device name separately |
| It works typed but not spoken | The pipeline is fine; the microphone path is not | Check the argument and the device |

The general rule: when the pipeline works from a typed sentence and fails from speech, the fault is
in the satellite or the microphone, and never in the containers.

## How do I know it works?

- [ ] A spoken wake word plus command changes a real entity in the dashboard.
- [ ] You have written down your real end-to-end latency, through a microphone.
- [ ] You have measured both the intent path and the model path the same way.
- [ ] The satellite is the only process listening on a port you added for this.
- [ ] You can run the thirty-command set without a microphone.

## Use it when / avoid it

**Use a satellite on the host** for a laptop, a desktop or a machine whose microphone you want.

**Use press-to-talk** if the microphone path is unreliable, if the machine is too small to run an
always-on listener, or if people are simply more willing to use a button.

**Keep the satellite's port on loopback or leave it unpublished.** It exists so audio can come back
to your speakers; it is not a service that needs to be reachable from the network.

**Do not put the satellite in a container to "keep it consistent".** The consistency is worth less
than the microphone working, which it will not.

> [!NOTE]
> macOS asks for microphone permission per application, so Terminal, your editor and your browser each
> need it separately — and none of those steps are verified by us, because the course has one
> Windows test machine.

## Reflect

1. What is your end-to-end latency through a microphone, and how does it compare with your typed
   measurement from Module 8?
2. Which stage grew the most between the two, and what would you change about that one?
3. If your machine could only support one of a wake word or the speech model, which would you drop
   and what would you tell people to do instead?

## Sources

- [Wyoming satellite](https://github.com/rhasspy/wyoming-satellite)
- [Wyoming protocol](https://github.com/rhasspy/wyoming)
- [Home Assistant — Wyoming integration](https://www.home-assistant.io/integrations/wyoming)
- [Latency budget template](../../templates/latency-budget.md)
- [Sample command set](../../labs/common/)
- [33 · The Ollama conversation agent](../module-10/lesson-01.md)