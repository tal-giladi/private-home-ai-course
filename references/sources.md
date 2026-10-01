# Source list

Everything the course leans on, in one place, so a claim in a lesson can be traced without hunting
through the text. Each lesson's own `## Sources` section lists the ones it actually used.

## Runtimes and tools

| What | Link | Used in |
|---|---|---|
| Ollama | <https://docs.ollama.com> | 1, 2, 4, 5, 10 |
| Ollama FAQ — bind address, context size, keep-alive | <https://docs.ollama.com/faq> | 1, 4, 11 |
| Ollama security advisories | <https://github.com/ollama/ollama/security/advisories> | 11 |
| llama.cpp and `llama-bench` / `llama-server` | <https://github.com/ggml-org/llama.cpp> | 1, 2, 4 |
| llama.cpp issue #1437 — memory bandwidth and generation | <https://github.com/ggml-org/llama.cpp/issues/1437> | 2 |
| Docker Compose file reference | <https://docs.docker.com/reference/compose-file/> | 3, 4, 11, 12 |
| Docker Compose profiles | <https://docs.docker.com/compose/how-tos/profiles/> | 3 |
| Docker resource limits | <https://docs.docker.com/reference/compose-file/services/#resources> | 12 |
| Docker networking | <https://docs.docker.com/engine/network/> | 3, 11 |
| Docker Desktop WSL2 backend | <https://docs.docker.com/desktop/features/wsl/> | 3 |
| Qdrant | <https://qdrant.tech/documentation/> | 6 |
| faster-whisper | <https://github.com/SYSTRAN/faster-whisper> | 8 |
| whisper.cpp | <https://github.com/ggml-org/whisper.cpp> | 8 |
| OpenAI Whisper | <https://github.com/openai/whisper> | 8 |

## Home Assistant and voice

| What | Link | Used in |
|---|---|---|
| Set up a fully local voice assistant | <https://www.home-assistant.io/voice_control/voice_remote_local_assistant/> | 7, 8, 10 |
| Home Assistant Container installation | <https://www.home-assistant.io/installation/linux#docker-compose> | 7 |
| Assist pipelines | <https://www.home-assistant.io/voice_control/pipelines/> | 7, 8, 10 |
| Exposing entities to Assist | <https://www.home-assistant.io/voice_control/voice_remote_expose_devices/> | 7, 10 |
| Custom sentences | <https://www.home-assistant.io/voice_control/custom_sentences/> | 7 |
| Built-in sentences | <https://www.home-assistant.io/voice_control/builtin_sentences/> | 7 |
| Best practices for Assist | <https://www.home-assistant.io/voice_control/best_practices/> | 7, 10 |
| Ollama integration | <https://www.home-assistant.io/integrations/ollama/> | 10 |
| LLM API developer docs (intents become tools) | <https://developers.home-assistant.io/docs/core/llm/> | 10 |
| Exposing scripts to LLMs | <https://www.home-assistant.io/voice_control/exposing_scripts_to_llms/> | 10 |
| Wyoming protocol | <https://github.com/rhasspy/wyoming> | 8, 9 |
| Wyoming integration | <https://www.home-assistant.io/integrations/wyoming> | 8, 9 |
| Speech-to-Phrase | <https://github.com/OHF-voice/speech-to-phrase> | 8 |
| Voice Chapter 9 — Speech-to-Phrase | <https://www.home-assistant.io/blog/2025/02/13/voice-chapter-9-speech-to-phrase/> | 8 |
| Piper (now `piper1-gpl`, OHF-Voice) | <https://github.com/OHF-Voice/piper1-gpl> | 8, 19 |
| Piper voices | <https://github.com/rhasspy/piper-voices> | 8, 19 |
| openWakeWord | <https://github.com/dscripka/openWakeWord> | 9 |
| Home Assistant's approach to wake words | <https://www.home-assistant.io/voice_control/about_wake_word/> | 9 |
| Voice Preview Edition | <https://www.home-assistant.io/voice-pe/> | 9, 10 |
| Remote access (and why a port is not it) | <https://www.home-assistant.io/docs/configuration/remote/> | 11 |

## Security

| What | Link | Used in |
|---|---|---|
| Cisco — detecting exposed Ollama servers with Shodan | <https://blogs.cisco.com/security/detecting-exposed-llm-servers-shodan-case-study-on-ollama> | 11 |
| Twingate — Ollama server exposure counts | <https://www.twingate.com/blog/ollama-server-exposure> | 11 |
| NYU Shanghai RITS — Bleeding Llama | <https://rits.shanghai.nyu.edu/ai/bleeding-llama-critical-unauthenticated-memory-leak-hits-300000-ollama-servers/> | 11 |
| Wiz — CVE-2024-37032 "Probllama" | <https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032> | 11 |
| Cyera — CVE-2026-7482 "Bleeding Llama" | <https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform> | 11 |
| Open WebUI security advisories | <https://github.com/open-webui/open-webui/security> | 11, 12 |
| ReversingLabs — malicious models on Hugging Face | <https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face> | 11 |
| Tailscale | <https://tailscale.com/kb/> | 11 |
| WireGuard | <https://www.wireguard.com/quickstart/> | 11 |
| CISA advisories | <https://www.cisa.gov/known-exploited-vulnerabilities-catalog> | 11 |

## Benchmarks and measurement

| What | Link | Used in |
|---|---|---|
| Geerling — ai-benchmarks (Pi 5, N150, Framework) | <https://github.com/geerlingguy/ai-benchmarks> | 2 |
| Stratosphere — LLM performance on Raspberry Pi 5 | <https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html> | 2 |
| mgroeber — llama.cpp on legacy hardware | <https://www.mgroeber.de/benchmarking-llamacpp-on-legacy-hardware-2.html> | 2 |
| It's FOSS — local LLMs without a GPU | <https://itsfoss.com/testing-local-llms-without-gpu> | 2 |
| Turing Pi — Whisper + Piper on RK3588 | <https://turingpi.com/whisper-cpp-piper-tts-arm64-turing-pi-rk3588/> | 8 |
| ik_llama.cpp discussion #164 (Ryzen 9 7950X) | <https://github.com/ikawrakow/ik_llama.cpp/discussions/164> | 2 |
| localaimaster — running LLMs on CPU only (secondary) | <https://localaimaster.com/blog/run-llm-cpu-only> | 2 |

## Interfaces and web UIs

| What | Link | Used in |
|---|---|---|
| Open WebUI | <https://docs.openwebui.com> | 3, 4 |
| LM Studio | <https://lmstudio.ai> | 3 (mentioned, not used) |
| Jan | <https://jan.ai> | 3 (mentioned, not used) |
| AnythingLLM | <https://anythingllm.com> | 6 (mentioned, not used) |
| LocalAI | <https://localai.io> | 3 (mentioned, not used) |
| privateGPT | <https://github.com/zylon-ai/private-gpt> | 6 (mentioned, not used) |
| awesome-selfhosted | <https://github.com/awesome-selfhosted/awesome-selfhosted> | 3 (mentioned, not used) |

## Models

Publisher pages are the authority for size, licence and provenance:
[Gemma](https://ai.google.dev/gemma/docs) · [Llama](https://www.llama.com/llama3_2/) ·
[Qwen2.5](https://qwenlm.github.io/blog/qwen2.5/) · [Qwen3](https://qwenlm.github.io/blog/qwen3/) ·
[Phi](https://huggingface.co/microsoft) · [nomic-embed-text](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) ·
[BGE-M3](https://huggingface.co/BAAI/bge-m3) · [Snowflake Arctic Embed 2](https://huggingface.co/Snowflake/snowflake-arctic-embed2-v2.0).

The course's own table, with what each one is for, is
[Pinned models and licences](models.md).

## Courses this one links to rather than duplicates

| Course | What we take from it |
|---|---|
| `rag-course` | Depth on chunking, embeddings, hybrid search, reranking, grounding and evaluation. Module 6 gives each idea a paragraph and links here. |
| `ai-inference` | Quantization mechanics, GGUF conversion, formal benchmarking. Modules 1–2 teach only what a home user needs. |
| `ai-engineer` | Building an OpenAI-compatible gateway. Module 4 uses such an API as a user. |
| `kubernetes` | Container networking and secrets beyond one host. A home lab is Compose on one machine. |
| `ai-security-course` | Attacks on LLM services and models. Module 11 teaches home-network defence and links out for the attacks. |

## About the research itself

The course survey, the overlap check against our other courses, and the feasibility questions the
plan still has open are in `plan.md` at the repository root. Nothing in this course was verified on
macOS, and the one test machine is a Windows laptop; both limits are marked where they matter.
