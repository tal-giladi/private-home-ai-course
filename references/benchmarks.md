# Benchmark numbers and where they come from

**Read this page before you quote any number from this course.**

Every performance figure in the course is one of three things, and each one is labelled where it
appears:

| Label | Meaning |
|---|---|
| **Cited** | Someone else measured it, on a machine named here, and there is a link |
| **Measured by us** | The course maintainers ran it on a named test machine |
| **Measure yours** | No number is given; a command is, and you fill in your own |

> [!IMPORTANT]
> **No number on this page is a guarantee for your machine.** They are what other people got on
> their hardware. A 7B model that manages 9.6 tokens/s on a Ryzen 9 will not manage 9.6 tokens/s on
> a laptop with one RAM stick, and that is not a defect — it is what memory bandwidth means. The
> point of the course is to predict, measure and choose, not to memorise a table.

## Chat generation on CPU

| Model | Machine | Generation | RAM | Source |
|---|---|---|---|---|
| Gemma 3 1B | Raspberry Pi 5, Ollama | 11.5 tok/s | 1.4 GB | [Stratosphere Pi 5 study](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html) |
| Llama 3.2 1B | Raspberry Pi 5 | 11.2 tok/s | 2.4 GB | same |
| Qwen2.5 1.5B | Raspberry Pi 5 | 10.0 tok/s | 1.9 GB | same |
| Llama 3.2 3B | Raspberry Pi 5 | 4.6–4.9 tok/s | 4.7 GB | Stratosphere; [Geerling](https://github.com/geerlingguy/ai-benchmarks) |
| Llama 3.2 3B | Intel N150 mini PC | 9.1 tok/s | — | [Geerling](https://github.com/geerlingguy/ai-benchmarks) |
| Llama 3.2 3B | Framework mainboard (Ryzen) | 13.1 tok/s | — | same |
| Qwen2.5 3B | Raspberry Pi 5 | 5.2 tok/s | 3.0 GB | Stratosphere |
| Gemma 3 1B | Intel i5 laptop, 12 GB | ~18.6 tok/s | — | [It's FOSS CPU test](https://itsfoss.com/testing-local-llms-without-gpu) |
| Phi-4-mini 3.8B | Intel i5 laptop | ~6.9 tok/s | — | same |
| ~7B | Intel i5 laptop | ~4.2 tok/s | — | same |
| Llama 3.1 8B, Q4_K_S (4.4 GiB) | Ryzen 9 7950X, llama.cpp | 9.6 tok/s generation; 108 tok/s prompt (pp512) | ~5–6 GB | [ik_llama.cpp discussion #164](https://github.com/ikawrakow/ik_llama.cpp/discussions/164) |
| 7B Q4_0 | Ryzen AI laptop | ~10 tok/s generation; 31–36 tok/s prompt | — | [mgroeber](https://www.mgroeber.de/benchmarking-llamacpp-on-legacy-hardware-2.html) |

**What the spread tells you.** The same 3B model runs at 4.6 tok/s on a Pi 5 and 13.1 tok/s on a
Ryzen mainboard — a factor of almost three, from memory bandwidth and memory type alone. The model
is not the variable. The machine is.

### Gaps: not measured, not claimed

- Qwen3 4B and Gemma 3 4B on CPU.
- Any 7–8B model on an Intel N100/N150. Bandwidth arithmetic puts it at roughly **2–4 tok/s**, which
  is an estimate from the rule in [06 · Memory bandwidth sets your speed](../lessons/module-02/lesson-01.md),
  not a measurement.
- Embedding throughput of `nomic-embed-text` and `bge-small` on CPU.
- Everything on Apple Silicon. Unified memory is fast and the expectation is that an M-series Mac
  beats an x86 laptop of the same year, but **we have not measured it**, and the course marks macOS
  steps "not verified by us" throughout.

## Voice on CPU

| Component | Number | Source |
|---|---|---|
| faster-whisper `small`, 13 min of audio, i7-12700K, 8 threads | 2 min 37 s (fp32); whisper.cpp 2 min 05 s using 1.0 GB; `openai/whisper` 6 min 58 s using 2.3 GB | [faster-whisper README](https://github.com/SYSTRAN/faster-whisper) |
| whisper.cpp memory per model | tiny ~273 MB, base ~388 MB, small ~852 MB, medium ~2.1 GB | [whisper.cpp README](https://github.com/ggml-org/whisper.cpp) |
| whisper.cpp real-time factor, RK3588 ARM board | tiny 0.10, base 0.16, small 0.47, medium 1.51 | [Turing Pi guide](https://turingpi.com/whisper-cpp-piper-tts-arm64-turing-pi-rk3588/) |
| Whisper in Home Assistant | ~8 s per command on a Pi 4; under 1 s on an Intel NUC | [HA local voice guide](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/) |
| Speech-to-Phrase in Home Assistant | under 1 s even on a Pi 4, for a fixed command set | same |
| Piper medium voices | 1.6 s of audio generated per second on a Pi 4 | same |
| Piper real-time factor, i7-1255U | ~0.15 | [aivideosensei](https://aivideosensei.com/guides/piper-tts-offline-voice-guide) (secondary) |
| openWakeWord | 15–20 models in real time on one Pi 3 core; targets < 0.5 false accepts/hour, < 5% false rejects | [openWakeWord README](https://github.com/dscripka/openWakeWord) |
| Minimum hardware for full local Whisper | an Intel N100-class CPU is the stated bare minimum | [HA Voice PE](https://www.home-assistant.io/voice-pe/), [Voice chapter 9](https://www.home-assistant.io/blog/2025/02/13/voice-chapter-9-speech-to-phrase/) |

A real-time factor below 1.0 means the stage is faster than live. `base` at 0.16 on a slow ARM
board means one second of audio takes 160 ms; the same model on your laptop will be far better.

## The latency budget

Course goals for the whole spoken round trip, from the end of your sentence to the first sound of
the reply:

| Stage | Budget |
|---|---|
| End-of-speech detection | 0.3–0.5 s |
| Speech-to-text (a 3 s command, Whisper base/small) | ≤ 1 s |
| Built-in intent match | ≤ 0.1 s |
| LLM with tools (1–3B) | ≤ 3 s |
| Text-to-speech to first audio (Piper) | ≤ 0.5 s |
| **Total, built-in intents** | **≤ 2 s** |
| **Total, LLM fallback** | **≤ 5 s** |

These are **targets, not measured results**. [29 · Measure the voice pipeline](../lessons/module-08/lesson-04.md)
is where you fill this table in on your own machine, and the honest answer on some machines is "the
intents target is met, the LLM target is not" — which is itself a useful result and is why the
default pipeline is intents first.

## Why long prompts hurt

Prompt processing runs at a fraction of generation speed on most machines, and a retrieval-augmented
answer can carry 2 000 prompt tokens. At 30–100 prompt tok/s that is **20–60 seconds before the
first word appears**. Generation speed does not save you here. This is the single most common cause
of "my local AI feels broken" in a home setup, and Modules 2 and 6 both attack it directly.

## Where these numbers come from and how to get your own

```bash
# the course's own measurement, on your machine, in about a minute
python homelab.py bench

# just the models, no voice services
python homelab.py bench --models-only

# the same thing with the reference tool, if you want to compare
llama-bench -m qwen3-4b-instruct-q4_K_M.gguf -p 512 -n 64
```

Then write the numbers in [Measure-yours tables](../templates/measure-yours.md) with the machine
name. That table, not this page, is the one you will still care about in a year.
