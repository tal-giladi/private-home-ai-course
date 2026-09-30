# Private Home AI: A CPU-only Home Lab — course plan

Written 2026-09-30. First draft.

**Status**

| Item | State |
|---|---|
| Plan | Reviewed with Tal 2026-09-30; decisions recorded in §12 |
| Decisions on open questions | All 12 decided by Tal 2026-09-30, §12 |
| Spike (benchmark script + minimal stack) | Not started (planning only, per the brief) |
| Lessons, labs, simulations, quizzes | Not started |

Throughout this plan, **Cited** marks a number taken from a public source (linked in §4);
**To measure** marks something we must measure ourselves before a lesson states it. Nothing
here has been measured by us yet.

Source: TODO_FOR_TAL.md item #9 (APPROVED 2026-09-29), with Tal's constraint:

> Must be practical on CPU-only machines: target 16-32GB RAM, quantized 1-8B models
> (llama.cpp/Ollama), CPU-friendly Whisper/Piper for voice. GPU optional, never required.

---

## 1. One-paragraph pitch

A public, hands-on course that turns an ordinary computer (a 16–32 GB laptop, an old
desktop or a small mini PC) into a **private home AI stack**: a local chat assistant, search
and question answering over your own files, and an offline voice assistant that controls
Home Assistant, with no cloud account, no subscription and no GPU. Every module ends with
something the learner can see or hear working on their own machine within minutes, and
every performance claim is measured on that machine, not promised. The course is honest
about what CPUs can and cannot do: it teaches the learner to size models to their memory
bandwidth, pick the right model for each job, keep voice latency under a budget, and run
the whole stack safely on a home network where a careless port can expose it to the
internet.

---

## 2. Target learner and outcome

**Learner (public audience):** a technically curious person — a developer, IT person,
maker or Home Assistant hobbyist — who is comfortable with a terminal and wants AI at home
without sending their data, voice or files to a cloud service.

**Assumed:** terminal basics (cd, editing a file, running a command), installing software,
basic home networking words (router, IP address). **Not assumed:** ML background, Python
beyond copying a command, Docker (an on-ramp is in M3), Home Assistant experience, any
smart-home hardware (M7 uses demo entities).

**Hardware tiers (the course is written for tier A and B; tier C is supported with a
reduced path)**

| Tier | Example machine | RAM | Default models | Voice path |
|---|---|---|---|---|
| A — laptop | Any 2019+ x86 or Apple Silicon laptop | 16 GB | 1–4B Q4 (chat), small embedder | Whisper base/small + Piper |
| B — desktop / mini PC | Ryzen or Intel desktop, dual-channel DDR4/DDR5 | 32 GB | up to 7–8B Q4 | Whisper small + Piper |
| C — low-power (optional) | Raspberry Pi 5 8 GB, Intel N100/N150 mini PC | 8–16 GB | 1–3B Q4 | Speech-to-Phrase or Whisper tiny/base + Piper |

GPU: optional everywhere. Each module has a short "If you have a GPU" note; no lab needs
one and no lesson's success criterion assumes one.

**Paths**

| Path | Modules | Needs | Estimated time |
|---|---|---|---|
| Core: private assistant | M0–M6 | Tier A or B machine | ~10–12 h |
| Voice + Home Assistant | M7–M10 | Same machine, a microphone (any headset or laptop mic) | +8–10 h |
| Safe and always-on | M11–M12 + capstone | Same; optional second always-on host | +6–8 h |

**Outcome — by the end of the core path they can:**

1. Run quantized 1–8B models locally with Ollama and llama.cpp, and explain what a model
   tag (size, quantization, context) means.
2. Predict, then measure, generation speed and RAM use of a model on their own machine
   from memory bandwidth and model size, and pick the largest model that meets a speed
   target.
3. Run a persistent stack with Docker Compose: model server, chat UI, vector store, with
   models and data on volumes that survive upgrades.
4. Choose models per job (chat, tool calling, embeddings) using a small evaluation set of
   their own tasks, not leaderboards.
5. *(Optional module M6)* Ask questions over their own files locally and check whether the
   answers are grounded (M6 explains each idea briefly; rag-course teaches it in depth).

**Voice + Home Assistant path adds:**

6. Build a fully local Assist pipeline (wake word → speech-to-text → intent or LLM →
   text-to-speech) over the Wyoming protocol, and measure its end-to-end latency.
7. Let a local LLM control Home Assistant through tools, while limiting what it can touch
   and requiring confirmation for risky actions.

**Safe and always-on path adds:**

8. Threat-model the stack, keep every service off the public internet, reach it remotely
   through a VPN, and handle updates, backups and model supply chain.

---

## 3. What already exists (research)

Checked 2026-09-30. Items marked *not fetched* were confirmed to exist but their contents
were not reviewed; re-check before the build.

### Free / public courses and guides

| Resource | Format | Strength | Gap we aim at |
|---|---|---|---|
| Home Assistant — [Set up a fully local voice assistant](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/) | Official docs | The canonical Wyoming + Whisper / Speech-to-Phrase + Piper path, with honest timings | No LLM, no RAG, no sizing method, no security |
| Home Assistant — [Ollama integration](https://www.home-assistant.io/integrations/ollama/) | Official docs | Local LLM as conversation agent; tool-capable models only; advice to expose < 25 entities; warns small models make mistakes | Reference page, not a learning path; no network exposure advice |
| Home Assistant — [LLM API developer docs](https://developers.home-assistant.io/docs/core/llm/) | Developer docs | How intents become tools; MCP endpoint | Written for integration developers |
| Home Assistant — [Voice Preview Edition](https://www.home-assistant.io/voice-pe/) | Hardware + docs | Open satellite with on-device wake word | A product, not a course |
| [Wyoming protocol](https://github.com/rhasspy/wyoming) | Spec | The glue between voice services | Short spec, no tutorial (not fetched) |
| [home-llm](https://github.com/acon96/home-llm) | Project | Small models fine-tuned for HA control | A tool; claims of beating larger general models are anecdotal |
| [Ollama docs / FAQ](https://docs.ollama.com/faq) | Docs | Bind address, context size, keep-alive | Nothing on authentication or hardening |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) + `llama-bench` | Tool + docs | The standard way to measure prompt processing and generation | Terse; assumes you know what to measure |
| [Jeff Geerling — ai-benchmarks](https://github.com/geerlingguy/ai-benchmarks) | Benchmark repo | Real numbers on Pi 5, N150, Framework | Numbers, not teaching |
| GUIs: [LM Studio](https://lmstudio.ai), [Jan](https://jan.ai), [Open WebUI](https://docs.openwebui.com), [AnythingLLM](https://anythingllm.com), [LocalAI](https://localai.io), [privateGPT](https://github.com/zylon-ai/private-gpt) | Apps | Fastest first win | Teach clicking, not sizing, evaluation or security (not fetched individually) |
| [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) | List | Breadth of self-hostable services | A list (not fetched) |
| Paid: [KodeKloud — Running Local LLMs with Ollama](https://learn.kodekloud.com/courses/running-local-llms-with-ollama), [Academind — Local LLMs via Ollama & LM Studio](https://academind.com/courses/local-llms-via-ollama-lm-studio-the-practical-guide), [DataCamp — Working with Llama 3](https://www.datacamp.com/courses/working-with-llama-3) | Video courses | Ollama basics | Paid; no Home Assistant voice, no CPU sizing, no home-network security |

Not verified: a DeepLearning.AI short course dedicated to local LLMs (none found),
NetworkChuck-style YouTube guides (secondary mentions only), r/LocalLLaMA and r/selfhosted
wikis, Proxmox/TrueNAS home lab guides.

### Our own courses (overlap check)

| Course | What overlaps | How this course handles it |
|---|---|---|
| **rag-course** (plan + spike; production path M11–M14 uses Ollama + Qdrant/pgvector on CPU) | Everything about how RAG works: document preparation, chunking, embeddings, hybrid search, reranking, grounding, abstention, evaluation, permissions | **M6 stands alone but stays shallow** (§12 Q6): it wires a local RAG service into the home stack and gives each concept a short plain explanation (a paragraph, no experiments), with a "go deeper" link to rag-course. M6 does not depend on rag-course being published; links point to rag-course's plan/playground until its lessons exist, then are updated. |
| **ai-inference** M4 Quantization (GGUF, llama.cpp, `llama-quantize`, Q4_K_M vs Q8_0 lab), M5 Benchmarking on CPU (TTFT/TPOT), M6 Containerized local serving | Quantization mechanics, GGUF conversion, formal benchmarking | M1–M2 teach only what a home user needs (read a tag, pick a quant, measure your machine) and link to ai-inference M4–M6 for depth. We do not convert or quantize models ourselves. |
| **ai-engineer** M1 (OpenAI-compatible gateway with Ollama), M4–M5 (retrieval), M10 (Compose serving), M11 (security) | OpenAI-compatible API, Compose | M4 uses the API as a user; links to ai-engineer M1 for building gateways. |
| **kubernetes** M3 networking, M4 Secrets and volumes, M6 security | Container networking, secrets | No Kubernetes here: a home lab is Docker Compose on one host. One "outgrowing Compose" note links to kubernetes. |
| **ai-security-course** 00.1 threat modeling, 02.2 inference API attack surface, 13.1/22.1 weight and supply-chain security, 14.1/15.1 RAG security | Attacks on LLM services and models | M11 teaches home-network defence as a core skill (bind addresses, VPN, reverse proxy, VLAN, updates) and links to ai-security-course for attacks. |

**Not covered in any of our courses:** Whisper, Piper, Wyoming, Home Assistant, wake words,
voice latency, home network hardening. Those modules (M7–M11) are new material.

### Intended differentiator

The survey is not exhaustive. Among what we found, official docs cover each piece
separately, GUIs give a first win without understanding, and paid courses stop at "Ollama
basics". Our intended differentiator is the combination of: (a) **CPU-first sizing as a
method** — predict from memory bandwidth, then measure on your own machine; (b) **one
integrated stack** — chat, own-files RAG and offline voice for Home Assistant on the same
box, sharing one model server and one RAM budget; (c) **no smart-home hardware needed** to
learn the voice path (demo entities, laptop mic); (d) **security as a core module**, not a
footnote, because exposed local-LLM servers are a real and measured problem (§5).

---

## 4. Hardware realism

### 4.1 The rule of thumb the course teaches

- **Generation (tokens/s) is limited by memory bandwidth.** Each new token reads all the
  model's weights once, so tokens/s ≈ usable memory bandwidth ÷ model size in bytes.
  Example: dual-channel DDR5-6000 (~96 GB/s theoretical) with an 8B Q4_K_M model (~4.9 GB)
  gives a ceiling of ~20 tokens/s; real numbers land at 50–75% of that. A single RAM stick
  halves bandwidth. More than ~4–8 threads does not help generation.
  ([llama.cpp issue #1437](https://github.com/ggml-org/llama.cpp/issues/1437),
  [localaimaster CPU guide](https://localaimaster.com/blog/run-llm-cpu-only) — secondary)
- **Prompt processing is limited by compute** and does scale with cores. It decides how
  long the learner waits before the first word, which matters most for RAG (long prompts)
  and voice (short prompts, but every millisecond is felt).
  ([mgroeber llama.cpp legacy hardware benchmarks](https://www.mgroeber.de/benchmarking-llamacpp-on-legacy-hardware-2.html))
- **RAM bill** = model weights + KV cache (grows with context length) + runtime overhead +
  everything else running (Whisper, Piper, embedder, Home Assistant, the OS, the browser).

### 4.2 Cited CPU-only numbers (Q4 quantization unless stated)

| Model | Machine | Generation | RAM | Source |
|---|---|---|---|---|
| Gemma 3 1B | Raspberry Pi 5 (Ollama) | 11.5 tok/s | 1.4 GB | [Stratosphere Pi 5 study](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html) |
| Llama 3.2 1B | Raspberry Pi 5 | 11.2 tok/s | 2.4 GB | same |
| Qwen2.5 1.5B | Raspberry Pi 5 | 10.0 tok/s | 1.9 GB | same |
| Gemma 3 1B | Intel i5 laptop, 12 GB | ~18.6 tok/s | — | [It's FOSS CPU test](https://itsfoss.com/testing-local-llms-without-gpu) |
| Llama 3.2 3B | Raspberry Pi 5 | 4.6–4.9 tok/s | 4.7 GB | Stratosphere; [Geerling](https://github.com/geerlingguy/ai-benchmarks) |
| Llama 3.2 3B | Intel N150 mini PC | 9.1 tok/s | — | [Geerling](https://github.com/geerlingguy/ai-benchmarks) |
| Llama 3.2 3B | Framework (Ryzen) mainboard | 13.1 tok/s | — | same |
| Qwen2.5 3B | Raspberry Pi 5 | 5.2 tok/s | 3.0 GB | Stratosphere |
| Phi-4-mini 3.8B | Intel i5 laptop | ~6.9 tok/s | — | It's FOSS |
| Llama 3.1 8B (Q4_K_S, 4.4 GiB) | Ryzen 9 7950X, llama.cpp | 9.6 tok/s gen; 108 tok/s prompt (pp512) | ~5–6 GB | [ik_llama.cpp discussion #164](https://github.com/ikawrakow/ik_llama.cpp/discussions/164) |
| 7B Q4_0 | Ryzen AI laptop | ~10 tok/s gen; 31–36 tok/s prompt | — | mgroeber |
| ~7B | Intel i5 laptop | ~4.2 tok/s | — | It's FOSS |

**To measure (gaps in public data):** Qwen3 4B and Gemma 3 4B on CPU; any 7–8B model on an
N100/N150 (bandwidth estimate: ~2–4 tok/s); embedding throughput of nomic-embed-text and
bge-small on CPU; all numbers on Apple Silicon (fast unified memory; expected to beat x86
laptops, not measured by us).

**What this means for the course (targets, to be verified in build phase 1):**

- Tier A (16 GB): 3–4B chat at ~5–10 tok/s, plus voice services and an embedder, fits with
  headroom. 7–8B loads but is slow (~3–5 tok/s) and leaves little RAM for the rest.
- Tier B (32 GB): 7–8B chat at ~5–10 tok/s depending on bandwidth.
- Long RAG prompts cost real time: 2 000 prompt tokens at 30–100 tok/s is 20–60 s before
  the first word. M2 and M6 teach shorter contexts, prompt caching and smaller models for
  this reason.
- Voice commands need a small, fast model (1–3B) or no LLM at all (built-in intents first,
  LLM as fallback). M10 teaches that split.

### 4.3 Voice on CPU (cited)

| Component | Numbers | Source |
|---|---|---|
| faster-whisper, `small`, 13 min audio, i7-12700K 8 threads | 2 min 37 s (fp32); whisper.cpp 2 min 05 s using 1.0 GB; openai/whisper 6 min 58 s using 2.3 GB | [faster-whisper README](https://github.com/SYSTRAN/faster-whisper) |
| whisper.cpp memory | tiny ~273 MB, base ~388 MB, small ~852 MB, medium ~2.1 GB | [whisper.cpp README](https://github.com/ggml-org/whisper.cpp) |
| whisper.cpp real-time factor, RK3588 ARM board | tiny 0.10, base 0.16, small 0.47, medium 1.51 | [Turing Pi guide](https://turingpi.com/whisper-cpp-piper-tts-arm64-turing-pi-rk3588/) |
| Home Assistant's own figures | Whisper ~8 s per command on a Pi 4, under 1 s on an Intel NUC; Speech-to-Phrase under 1 s even on a Pi 4 (limited command set); Piper medium voices 1.6 s of audio per second on a Pi 4 | [HA local voice guide](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/) |
| HA minimum for full local Whisper | Intel N100 class stated as the bare minimum | [HA Voice PE page](https://www.home-assistant.io/voice-pe/), [Voice chapter 9](https://www.home-assistant.io/blog/2025/02/13/voice-chapter-9-speech-to-phrase/) |
| Piper | real-time factor ~0.15 on an i7-1255U (secondary) | [aivideosensei Piper guide](https://aivideosensei.com/guides/piper-tts-offline-voice-guide) |
| openWakeWord | one Pi 3 core runs 15–20 models in real time; targets < 0.5 false accepts/hour, < 5% false rejects | [openWakeWord README](https://github.com/dscripka/openWakeWord) |

### 4.4 Voice latency budget (target, to measure)

A spoken command should feel instant. Proposed budget on tier A, from end of speech to
start of spoken reply: **≤ 2 s for built-in intents, ≤ 5 s with the LLM fallback.**

| Stage | Budget (target) |
|---|---|
| End-of-speech detection | ~0.3–0.5 s |
| Speech-to-text (Whisper base/small, a 3 s command) | ≤ 1 s |
| Intent match (built-in) / LLM with tools (1–3B) | ≤ 0.1 s / ≤ 3 s |
| Text-to-speech first audio (Piper) | ≤ 0.5 s |

M8 and M10 make the learner measure each stage on their own machine and fill this table.

### 4.5 How we verify before promising

- Build phase 1 writes the `homelab doctor` + `homelab bench` scripts (§8.3) and runs them
  on Tal's only test machine (32 GB Core Ultra 7 laptop, §12 Q11): full runs for tier B,
  memory-capped runs to check what fits in tier A. Tier A speed and all tier C numbers stay
  cited.
- Lessons state timings as **typical ranges with the source machine named**, never as
  guarantees, and always next to "measure yours".
- No learner-submitted results are published: lessons show only our own measurements and
  cited sources (§12 Q9). Learners compare their `bench` output with those.

---

## 5. Risks and mitigations

### 5.1 Security of self-hosted services on a home network (core, taught in M11)

The evidence that this matters:

- Local model servers exposed to the internet are common. Cisco found 1 100+ exposed Ollama
  servers via Shodan ([Cisco](https://blogs.cisco.com/security/detecting-exposed-llm-servers-shodan-case-study-on-ollama));
  later 2026 counts reported ~175 000 ([Twingate](https://www.twingate.com/blog/ollama-server-exposure))
  and ~300 000 ([NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/bleeding-llama-critical-unauthenticated-memory-leak-hits-300000-ollama-servers/)).
  The Ollama API has **no authentication**: anyone who reaches it can list, pull and delete
  models and use the compute.
- Ollama binds to 127.0.0.1 by default, but many guides tell people to set
  `OLLAMA_HOST=0.0.0.0` so other devices (or Home Assistant in a container) can reach it —
  one router port-forward away from the internet ([Ollama FAQ](https://docs.ollama.com/faq)).
- Real vulnerabilities: CVE-2024-37032 "Probllama" (path traversal → remote code execution,
  worst in Docker where Ollama runs as root on 0.0.0.0; fixed in 0.1.34)
  ([Wiz](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032));
  CVE-2026-7482 "Bleeding Llama" (unauthenticated memory leak via a malformed GGUF file;
  fixed in 0.17.1) ([Cyera](https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform)
  — re-verify details at build); Open WebUI CVE-2025-64496 (account takeover → code
  execution; fixed in 0.6.35) and CVE-2025-46719 (stored XSS; fixed in 0.6.6)
  ([SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2025-64496/)).
- Home Assistant itself warns that just opening a port is not secure and recommends its
  cloud relay, a VPN or a correctly configured reverse proxy
  ([HA remote access](https://www.home-assistant.io/docs/configuration/remote/)). The course
  does not use HA Cloud (no subscriptions) and teaches the VPN route.
- Model supply chain: malicious pickle models have been found on Hugging Face
  ([ReversingLabs](https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face));
  GGUF files carry Jinja chat templates and parsers can be attacked with malformed files
  (Bleeding Llama).

What the course does about it:

- **Safe defaults from M1:** every lab keeps services on 127.0.0.1 or an internal Docker
  network. The shared Compose stack publishes no port on 0.0.0.0 except the chat UI, and
  only after M11 explains it.
- **Rules taught in M11:** never port-forward a model server or Home Assistant; remote
  access only through Tailscale or WireGuard; a reverse proxy with authentication in front
  of every web UI that is shared on the LAN; separate network (VLAN or guest network) for
  IoT devices; pinned versions and a monthly update routine with a CVE check; models only
  from named publishers, GGUF or safetensors, never pickle; secrets in `.env` files that
  are gitignored.
- **The exposure lab** runs only on an isolated Docker network on the learner's own
  machine: container A (an unauthenticated model server) and container B (an "attacker on
  the LAN") show what an open API allows, then the fix. No real scanning, no internet
  targets, no Shodan queries by learners. Opens with a `> [!CAUTION]` block.
- LLM safety inside Home Assistant (M10): expose few entities, no locks, alarms or garage
  doors to the LLM without a confirmation step, and read the tool calls in the logs.
- Attacks in depth link to ai-security-course (02.2, 13.1, 22.1).

### 5.2 Other risks

| Risk | Mitigation |
|---|---|
| Learner's machine is too weak (8 GB, old CPU) | `homelab doctor` classifies the machine into a tier on day one and recommends the tier C path or a smaller model; the course never silently assumes 32 GB |
| Tool churn (Ollama, Open WebUI, HA release monthly) | Pin every image and version in `labs/common/compose.yaml`; lessons marked `volatility: implementation` get a `last_verified` date and a quarterly re-check (§10 phase 7) |
| Model churn (new small models every month) | Lessons teach a method (sizing + own eval set), with a pinned default model list in one file; swapping the default does not rewrite lessons |
| Windows friction (Docker Desktop, WSL2, mic access inside containers) | Native Ollama on Windows for M1–M2; Docker via WSL2 from M3; voice satellite runs natively on the host, not in a container; per-OS troubleshooting pages (§8.3) |
| Microphone and audio devices differ | Every voice lab works from recorded WAV files first, microphone second |
| Small models misfire on tool calls | Taught, not hidden: M10 measures the failure rate on a fixed command set and teaches intents-first, LLM-fallback and confirmation |
| Large downloads (models 1–5 GB) | Size shown before every pull; one default model per tier; everything else optional |
| Power and noise of an always-on box | M12 measures idle watts and sets model unload (keep-alive) so RAM and power drop when idle |
| Licenses of models and voices | Default list uses permissive licenses; each model's license linked in the model list; Piper voices checked per voice |
| Privacy claims | "No cloud" is tested, not asserted: M12 lab blocks outbound traffic and shows the stack still works |

---

## 6. How labs give quick, visible results

The core design constraint: every module produces something the learner sees or hears
working within minutes, then deepens.

| Module | First visible result | Target time |
|---|---|---|
| M0 | `homelab doctor` prints the machine's tier, RAM, bandwidth estimate and a recommended model | < 5 min |
| M1 | A local model answers a question in the terminal with the network cable unplugged | < 10 min (plus download) |
| M2 | Prediction card vs measured `bench` result for 3 models on your machine | < 15 min |
| M3 | `docker compose up` brings the stack up; a chat UI in the browser talks to the local model | < 10 min |
| M6 | Ask "when does my washing machine warranty end?" over a folder of your own PDFs and get a cited answer | < 15 min |
| M7 | Type "turn on the kitchen light" into Assist and watch a demo light change | < 10 min |
| M8 | Drop a WAV file in; see the transcript and hear Piper speak the reply, with stage timings | < 10 min |
| M9 | Say the wake word into the laptop mic and hear a reply | < 15 min |
| M10 | "It's cold in here" makes the local LLM turn on a demo heater, with the tool call shown | < 15 min |
| M11 | The isolated exposure lab lists models on the "victim" container, then fails after the fix | < 15 min |

Supporting pieces:

- **One shared stack** (`labs/common/compose.yaml`) grows module by module; each module
  adds services with a profile (`--profile voice`), so learners never rebuild from scratch.
- **Sample data included:** a folder of fictional household documents (manuals, warranty
  PDFs, receipts, recipes, notes) and a set of recorded voice commands (WAV), so labs work
  before the learner uses their own files or voice.
- **Simulation: sizing calculator** (`simulations/sizing/`): choose RAM, memory type and
  channels, model size and quantization, context length and the voice services; see the
  RAM bill and predicted tokens/s. Static HTML, runs offline, labelled "estimate, measure
  yours". Used in M2 and M5.
- **Measure-yours tables:** labs end by filling a small table with the learner's own
  numbers, compared with the cited ranges in §4.

---

## 7. Course structure (5 parts, 13 modules, 44 lessons)

Every lesson follows the Academy lesson shape (§16): why it matters → how it works → show
me → try it → break it → fix it → how do I know it works → use / don't use → reflect →
sources.

### Part 1 — First light (core)

**M0. Orientation and setup check** (2 lessons)
- 00.1 What a private home AI stack is, what CPUs can and cannot do, the three tiers,
  the course map.
- 00.2 `homelab doctor`: OS, RAM, CPU, memory channels, disk space, Docker, mic; your tier
  and a recommended first model.

**M1. Your first local model** (3 lessons)
- 01.1 Ollama and llama.cpp: install, run, chat, offline test.
- 01.2 Reading a model tag: parameters, quantization (Q4_K_M, Q5, Q8 — intuition only;
  links ai-inference M4), context length, instruct vs base, where GGUF files come from.
- 01.3 Settings that change the experience: temperature, context size, keep-alive,
  threads. Break it: too-large context eats RAM.

**M2. Sizing your machine** (4 lessons)
- 02.1 Memory bandwidth and why generation speed is bandwidth ÷ model size.
- 02.2 The RAM bill: weights, KV cache, context, and everything else on the box.
  Simulation: sizing calculator.
- 02.3 Measure it: `llama-bench` / `homelab bench`, prompt processing vs generation, threads,
  one vs two RAM sticks (explained; not required to test).
- 02.4 Choose the largest model that meets your speed target; the "if you have a GPU"
  note (offloading layers).

### Part 2 — Build the stack (core)

**M3. Home lab foundations** (4 lessons)
- 03.1 Choosing the host: your laptop now, an always-on mini PC or old desktop later;
  Pi 5 and N100 honestly compared; power and noise.
- 03.2 Docker Compose on-ramp: services, volumes, networks, profiles; Windows via WSL2.
- 03.3 The shared stack: model server, chat UI (Open WebUI), where models and data live,
  version pinning.
- 03.4 Keeping it tidy: disk use of models, pruning, logs.

**M4. Serving and the OpenAI-compatible API** (3 lessons)
- 04.1 Ollama and `llama-server` APIs; the OpenAI-compatible endpoint; calling it from
  curl and a 20-line script (links ai-engineer M1 for gateways).
- 04.2 Concurrency and memory on one box: two models loaded, keep-alive, what happens
  when chat and voice ask at once.
- 04.3 Chat UI done right: Open WebUI users, local-only accounts, no telemetry settings.

**M5. Picking models for jobs** (3 lessons)
- 05.1 Jobs: chat, tool calling, summarising, embeddings; one small model per job vs one
  big model for everything, on a fixed RAM budget.
- 05.2 Your own eval set: 20 of your real tasks, scored side by side on 3 models; why
  leaderboards mislead at home.
- 05.3 Licenses and trusted sources for models.

**M6. Your own files, privately (RAG in the home stack)** (3 lessons, **optional**)
- Optional module: skipping it removes only lesson 10.4 and the capstone's "Private files"
  criterion. It stands alone (no rag-course needed); rag-course is the "go deeper" link.
- 06.1 Wire a local RAG service into the stack: an embedding model + a vector store (the
  same one rag-course's production path uses) + the chat model; ingest the sample
  household folder. Chunking, embeddings, hybrid search and grounding each get a short
  plain explanation (a paragraph each) with a link to the rag-course lesson that teaches
  it in depth.
- 06.2 Home-specific concerns: which folders to index (and which never), keeping the index
  in sync with a changing folder, deleting a file removes it from the index, prompt length
  vs CPU wait time.
- 06.3 Is it right? 10 labelled questions over the sample folder, grounded vs ungrounded
  answers, using rag-course's evidence-coverage idea in its simplest form. Next step:
  rag-course.

### Part 3 — Voice and Home Assistant

**M7. Home Assistant in a box** (3 lessons)
- 07.1 Home Assistant Container in the stack (HA OS comes in 12.4, §12 Q3); onboarding; demo and
  template entities, so no smart-home hardware is needed.
- 07.2 Assist with typed commands: intents, areas, aliases, exposed entities.
- 07.3 Custom sentences and automations triggered by voice phrases.

**M8. Speech in and out** (4 lessons)
- 08.1 The Wyoming protocol and the Assist pipeline: what runs where.
- 08.2 Speech-to-text: faster-whisper model sizes vs accuracy vs speed on your machine;
  Speech-to-Phrase as the fast, limited alternative. Lab from WAV files.
- 08.3 Text-to-speech with Piper: voices, quality levels, speed.
- 08.4 Measure the pipeline: fill the §4.4 latency table for your machine.

**M9. Wake word and satellites** (3 lessons)
- 09.1 Wake words: openWakeWord vs on-device microWakeWord; false accepts vs false
  rejects; test with the recorded set.
- 09.2 A laptop or Pi as a satellite (wyoming-satellite style) with the mic on the host.
- 09.3 Optional hardware: Home Assistant Voice Preview Edition and ESP32 satellites
  (no lab depends on it).

**M10. A local LLM as the voice assistant's brain** (4 lessons)
- 10.1 The Ollama integration: conversation agent, tool-capable models, context size.
- 10.2 Intents first, LLM as fallback: why and how, and the latency difference.
- 10.3 Tools and guardrails: exposing few entities, confirmation for risky actions, reading
  the tool calls; measuring misfires on a fixed set of 30 commands.
- 10.4 *(Optional, needs M6)* Answering from your own files by voice, with the
  prompt-length cost.

### Part 4 — Safe and always-on

**M11. Securing the home lab** (4 lessons)
- 11.1 Threat model of a home AI stack: who can reach what, what an attacker gains
  (compute, your files, your house), links ai-security-course 00.1.
- 11.2 Bind addresses and ports: 127.0.0.1 vs LAN vs internet; the isolated exposure lab;
  never port-forward.
- 11.3 Remote access the safe way: Tailscale or WireGuard; a reverse proxy with auth for
  shared UIs; separate network for IoT devices.
- 11.4 Updates, CVEs and supply chain: version pinning, a monthly update routine, checking
  advisories, model provenance (GGUF/safetensors from named publishers, never pickle).

**M12. Running it for real** (4 lessons)
- 12.1 Always-on operations: resource limits so voice never starves, keep-alive and idle
  power, health checks, logs.
- 12.2 Backups and restore drill: HA config, vector index, chat history, Compose files;
  models are re-downloadable and not backed up.
- 12.3 Prove "no cloud": block outbound traffic from the stack and show everything still
  works; find anything that phones home.
- 12.4 Your always-on home: stay on HA Container or move to HA OS on a mini PC (what
  add-ons give you, backup → restore migration, pointing HA OS at the Ollama and Wyoming
  services on the stack host). Going further: a short note on Proxmox for a dedicated
  always-on box (no lab).

### Part 5 — Capstone

The learner builds their own private home AI stack on their own hardware: chat, RAG over a
chosen folder, a voice pipeline controlling at least five (demo or real) entities, remote
access over a VPN, with measured numbers and a security checklist. Graded with §9.

**Module quizzes:** every module M0–M12 has a module quiz (8–10 scenario questions); every
lesson has a 3–5 question knowledge check (§15).

---

## 8. Public learning experience

### 8.1 Positioning

The course home page states plainly: for technically curious people with a terminal and a
16–32 GB computer; no GPU, no cloud account, no subscription, no smart-home hardware
required; three paths with time estimates (§2); what the course will not promise (fast 8B
models on a weak laptop).

### 8.2 Accessibility

- Every voice lab has a text-only route (typed Assist, WAV files instead of a mic), so
  learners who cannot speak, hear, or use a microphone can complete the course; the
  capstone rubric accepts a typed-command pipeline plus a TTS output check.
- Transcripts for every sample audio file; alt text for every diagram.
- The sizing simulation is keyboard-operable, readable at 360 px, and shows numbers as
  text, never colour alone.
- Commands are given for Windows (PowerShell), macOS and Linux where they differ.

### 8.3 Setup checks and troubleshooting

- `homelab doctor` (Python, standard library only; PowerShell fallback on Windows): OS, CPU
  model and cores, RAM total and free, memory channels where detectable, disk space,
  Docker and Compose versions, Ollama reachable on 127.0.0.1 only, microphone present,
  ports in use, **warning if any stack service listens on 0.0.0.0**. Each failure links to
  a fix page.
- `homelab bench`: runs `llama-bench` (or the Ollama API) on the tier's default models and
  prints prompt and generation tokens/s and peak RAM, plus Whisper and Piper timings on the
  sample WAVs.
- Troubleshooting pages: Windows (WSL2 memory limit, Docker Desktop resources, mic access),
  macOS (Apple Silicon images, mic permissions), Linux (Docker group, PulseAudio/PipeWire),
  "model loads but is very slow" (swap, one RAM stick, thermal throttling), "Home Assistant
  can't reach Ollama" (container networking without 0.0.0.0).

### 8.4 Hebrew-ready (Hebrew added later, §12 Q7)

Lessons are English only for now, but nothing is built in a way that makes Hebrew a
rewrite:

- **Language is a setting, not code.** `labs/common/.env.example` has one `LANG` value that
  picks the Whisper language, the Piper voice, the Home Assistant language and the sample
  data folder. No lab script hard-codes English.
- **Multilingual models by default:** Whisper multilingual models (never the `.en`-only
  variants), a chat model and an embedder that handle Hebrew reasonably (checked in the
  phase 1 benchmarks alongside the default model list).
- **Per-language data folders:** `labs/common/samples/en/` (household documents, labelled
  questions, recorded commands with transcripts, HA custom sentences); `he/` is added
  later with the same file names and structure.
- **User-facing strings in the lab tools** (`homelab doctor`, `bench`, the sizing
  simulation) live in one strings file per language; the simulation layout works
  right-to-left (`dir="rtl"`) and is tested once with a dummy Hebrew strings file.
- **Lessons keep language-specific parts in marked blocks** (the voice, the command
  phrases, the sample file names), so a Hebrew version swaps those blocks instead of
  rewriting the lesson.
- **Phase 1 checks what Hebrew support actually exists:** Whisper accuracy on Hebrew
  commands, available Piper Hebrew voices, Home Assistant Assist intents in Hebrew, and
  how a small model handles Hebrew tool calls. The result goes in `references/` and
  decides what the later Hebrew version can promise.
- The Academy import contract is English only today (ai-native-org §19.1); a Hebrew
  version will need the importer to support a second language. Noted in
  `TODO_FOR_TAL.md`, not solved here.

---

## 9. Capstone rubric

| Criterion | What "meets the bar" looks like |
|---|---|
| Sizing | Prediction vs measured tokens/s and RAM for the chosen models, with the gap explained |
| Model choice | Own eval set of ≥ 20 tasks; chosen model per job justified with scores and speed |
| Private files (only if M6 was taken) | RAG over a real folder; 10 labelled questions; grounded-answer rate reported; deleting a file removes it from answers |
| Voice pipeline | Wake word (or typed route) → STT → intents/LLM → TTS; per-stage latency table filled; misfire rate on 30 commands reported |
| Guardrails | Exposed entity list justified; risky actions need confirmation; tool calls logged |
| Security | No service reachable from the internet (checked from outside via the VPN-off test); remote access only via VPN; versions pinned; update routine written; `doctor` shows no 0.0.0.0 warnings |
| Operations | Backup + a completed restore drill; idle power and RAM measured |
| No cloud | Outbound-blocked test passes with every feature still working |
| Reproducibility | One `docker compose up` (plus a documented native Ollama step, if used) rebuilds the stack from the repo and `.env.example` |

The one-page write-up defends every choice with the learner's own numbers.

---

## 10. Build phases

1. **Spike: doctor + bench + minimal stack.** `homelab doctor`, `homelab bench`, a Compose
   file with Ollama + Open WebUI + Home Assistant + Wyoming Whisper/Piper. Run on Tal's
   machines; fill §4.2–4.4 with our own numbers. Checkpoint: Tal signs off on the spike and
   on the default model list before phase 2.
2. **Sample data:** fictional household document folder, 10–20 labelled questions,
   recorded command set (30 commands, several voices, with transcripts), demo HA entity
   config.
3. **Part 1** (M0–M2) + sizing simulation + troubleshooting pages.
4. **Part 2** (M3–M6). M6 is built now; its "go deeper" links point to rag-course's plan
   and playground and are updated when rag-course lessons are published.
5. **Part 3** (M7–M10).
6. **Part 4** (M11–M12), including the isolated exposure lab, + capstone brief and rubric.
7. **QA and verification:** every lab run end to end on Windows and on Linux (WSL2) on
   Tal's laptop, including a 16 GB memory-capped run; macOS steps marked "not verified by
   us" unless a tester is found; every quiz YAML parsed and checked against the Academy quality rules;
   test import into tals-academy with its course-creator adapter; links, licenses and
   pinned versions verified; `last_verified` set. Quarterly re-check for
   implementation-volatile lessons.

---

## 11. Success criteria

- A learner with a 16 GB CPU-only laptop completes every lab, including voice, with no GPU
  and no paid service.
- Every first visible result in §6 is reached in its target time on the tier A test
  machine.
- Every performance number in a lesson is either cited with a source or measured by us,
  names the machine, and is shown next to "measure yours".
- The tier A voice pipeline meets the §4.4 budget (≤ 2 s intents, ≤ 5 s LLM fallback) on
  the test machine, or the lesson states the measured number honestly.
- No lab publishes a service on 0.0.0.0 before M11, and the exposure lab never touches a
  network beyond the learner's own Docker network.
- Every voice lab has a text-only route.
- M6 stands alone with short explanations; depth is linked to rag-course, not duplicated;
  skipping M6 leaves the rest of the course and the capstone completable.
- The course imports into tals-academy with zero adapter errors and every quiz passes the
  quality script.

---

## 12. Decisions (Tal, 2026-09-30)

1. **Name — decided (Tal, 2026-09-30):** "Private Home AI: A CPU-only Home Lab"; folder
   `private-home-ai`.
2. **Runtime — decided (Tal, 2026-09-30):** Ollama is the default runtime in every lab;
   llama.cpp (`llama-bench`, `llama-server`) is used for measuring (M2). Lessons that touch
   runtime settings add a short optional "Do it yourself with llama.cpp" note for
   experienced users who want to run `llama-server` and tune its parameters by hand (§16).
3. **Home Assistant install type — decided (Tal, 2026-09-30):** all labs use HA Container
   in the Compose stack (any OS with Docker, starts in a minute). For the final always-on
   setup the learner may stay on Container or move to HA OS on a mini PC; one lesson (M12)
   covers the move.
4. **Docker — decided (Tal, 2026-09-30):** Docker Compose is required for everyone from M3
   onwards; no native-install path is maintained after M2 (Ollama itself may still run
   natively on the host, as in M1–M2).
5. **Default models — decided (Tal, 2026-09-30):** chosen after the phase 1 benchmarks on
   Tal's machines; the phase 1 checkpoint includes signing off the default model list.
6. **RAG module — decided (Tal, 2026-09-30):** M6 is optional and stands alone, with a short
   plain explanation of each concept and rag-course as the "go deeper" link. It is built
   now; links are updated when rag-course lessons are published. Skipping M6 removes only
   lesson 10.4 and the capstone's "Private files" criterion.
7. **Language — decided (Tal, 2026-09-30):** English only for now; Hebrew added later, so
   everything is built Hebrew-ready (§8.4).
8. **Hardware purchases — decided (Tal, 2026-09-30):** both optional. Home Assistant Voice
   Preview Edition (~$69) and an always-on mini PC are mentioned as optional upgrades (09.3,
   03.1, 12.4); no lab or capstone criterion requires buying anything.
9. **Benchmarks — decided (Tal, 2026-09-30):** only our own measurements and cited sources;
   no community results table.
10. **Virtualisation — decided (Tal, 2026-09-30):** no Proxmox module; one host with
    Docker. Lesson 12.4 gets a short "going further" note on Proxmox for learners building
    a dedicated always-on box (needs a spare machine, wipes it, splits RAM between VMs).
11. **Test machines — answered (Tal, 2026-09-30):** one machine only: Tal's Windows 11
    laptop, Intel Core Ultra 7 255H (16 cores), 32 GB DDR5-5600 (reported as one module;
    whether it runs dual-channel is to be confirmed by `bench`), Intel integrated graphics,
    no discrete GPU. Consequences for the plan:
    - Tier B numbers are measured on this laptop.
    - Tier A (16 GB) is tested by capping memory on the same laptop (WSL2 `memory=16GB`,
      Docker limits): this proves what fits in 16 GB, but speed numbers are this laptop's,
      so tier A speed stays cited (§4.2).
    - Tier C (Pi 5 / N100) stays cited only; lessons say so.
    - Linux is tested through WSL2; macOS is not tested by us. Phase 7 marks macOS steps as
      "not verified by us" unless a tester is found.
12. **Spike first — decided (Tal, 2026-09-30):** build the phase 1 spike (`doctor`, `bench`,
    minimal stack) before any lesson; lessons start only after Tal signs off on it.

---

## 13. Feasibility questions (to resolve in phase 1)

1. Does Home Assistant Container reach an Ollama running natively on Windows/macOS without
   binding Ollama to 0.0.0.0 (e.g. via `host.docker.internal`)? The M11 safe-default story
   depends on it.
2. Can a microphone be used reliably from a Wyoming satellite on Windows, or does the
   Windows voice path stay WAV-file only?
3. Does a 1–3B tool-capable model reach an acceptable misfire rate on the 30-command set?
   If not, M10 defaults to intents-first with the LLM for questions only.
4. End-to-end voice latency on tier A: is the §4.4 budget achievable with Whisper base or
   small, or must the default be Speech-to-Phrase?
5. RAM on tier A with everything loaded at once (chat model, embedder, Whisper, Piper,
   HA, Open WebUI, vector store): does it fit in 16 GB with a browser open?

---

## 14. Revision log

**2026-09-30 — first draft.** Written from TODO item #9, using rag-course/plan.md as the
format template and ai-native-org's Academy import contract for the repository layout.
Research on public courses, CPU benchmarks, voice components and home-network security
recorded in §3–5; our own measurements are still to come (phase 1).

**2026-09-30 — Q1 decided.** Name "Private Home AI: A CPU-only Home Lab"; folder renamed
from `home-lab-course` to `private-home-ai`.

**2026-09-30 — Q2 decided.** Ollama is the default runtime; llama.cpp is used for measuring;
optional "Do it yourself with llama.cpp" notes for experienced users (§16).

**2026-09-30 — Q3 decided.** Labs use HA Container; final setup may stay on Container or move
to HA OS on a mini PC; new lesson 12.4 covers the move (M12 grows to 4 lessons).

**2026-09-30 — Q4 decided.** Docker Compose required for everyone from M3; no separate
native-install path.

**2026-09-30 — Q5 decided.** Default model families chosen after the phase 1 benchmarks.

**2026-09-30 — Q6 decided.** M6 made optional and self-contained (short explanations,
rag-course for depth), built now; 10.4 and the capstone "Private files" criterion marked
as needing M6.

**2026-09-30 — Q7 decided.** English only for now, built Hebrew-ready (new §8.4).

**2026-09-30 — Q8 decided.** Voice PE and a mini PC are optional; nothing requires a
purchase.

**2026-09-30 — Q9 decided.** Only our own and cited benchmark numbers; no community table.

**2026-09-30 — Q10 decided.** No Proxmox module; a short note in 12.4.

**2026-09-30 — Q11 answered.** One test machine (32 GB Core Ultra 7 laptop): tier B
measured, tier A by memory cap, tier C and macOS not verified by us; §4.5 and phase 7
updated.

**2026-09-30 — Q12 decided.** Spike first; all §12 questions now decided.

---

## 15. Repository layout (Academy import contract, as in ai-native-org)

```text
private-home-ai/
  plan.md                  ← this file
  CLAUDE.md                ← build guide for agents (lesson template, rules, import contract)
  README.md                ← H1 = course title; first paragraph = catalog description
  _sidebar.md              ← the only table of contents the importer reads
  index.html               ← docsify config
  TODO_FOR_TAL.md          ← handoff / open items
  PROGRESS.md              ← build progress (not imported)
  glossary.md              ← terms, each linked to the lesson that introduces it
  brief/                   ← brief (not imported)
  curriculum/              ← course-outline.md, module-NN-plan.md, sources (not imported)
  lessons/module-NN/
    lesson-MM.md           ← frontmatter + `# NN.M · Title`
    lesson-MM.quiz.yaml    ← 3–5 question knowledge check
    lesson-MM.instructor.md← instructor notes (not imported)
  assessments/
    module-NN-quiz.md      ← intro page: what it covers, pass mark
    module-NN-quiz.quiz.yaml ← 8–10 scenario questions
    capstone.md, capstone-rubric.md
  labs/
    common/                ← compose.yaml (profiles: core, rag, voice, secure), .env.example,
                             homelab doctor/bench scripts, sample data, recorded WAVs
    module-NN/             ← README (Requirements, Contents table, Quick start), exercises/,
                             solutions/, checks/ — offered as the module zip
  simulations/sizing/      ← sizing calculator (index.html + js/css, vendored, offline)
  templates/               ← measure-yours tables, security checklist, capstone write-up
  assets/                  ← SVG/PNG diagrams (stack map, Assist pipeline, network zones)
  references/              ← pinned model list with licenses, pinned versions, source list
```

Sidebar format: `- **Module N — Title**`, lesson lines `  - [NN · Title](lessons/module-NN/lesson-MM.md)`
(global running number), then `  - [Module N quiz](assessments/module-NN-quiz.md)`; part
lines are plain `- Part 1 — First light` (ignored by the importer).

Quiz YAML (the only copy of questions and answers): each entry has `id`, `question`,
exactly 4 `options`, `correct` (0–3), `explanation`; wrong options are plausible
misconceptions; similar lengths; no "all/none of the above"; `correct` spread evenly.

Allowed content: plain markdown and YAML, GitHub alerts, mermaid, KaTeX; raw HTML only
`<details>`, `<summary>`, `<kbd>`, `<sub>`, `<sup>`, `<br>`; relative links only; no
iframes (simulations embedded with a `Simulation: …` link). Every lab that can cause harm
(M11 exposure lab, anything touching router or firewall settings, secrets) opens with a
`> [!WARNING]` or `> [!CAUTION]`. No `course.py`/`progress/` tracker (Academy tracks
progress).

Hosting: GitHub Pages (docsify) plus Academy import. No model files are hosted by us;
labs pull pinned models from their official registries.

---

## 16. Lesson template

```markdown
---
id: "02.3"
module: 2
minutes: 15
practice_minutes: 30
prerequisites: ["02.2"]
objectives:
  - Measure prompt-processing and generation speed of a model on your machine.
  - Explain why more threads speed up the prompt but not generation.
volatility: implementation     # concept | implementation
hardware: "CPU-only, tier A+"  # course-specific field; ignored by the importer if unknown
sources:
  - title: "llama.cpp — llama-bench"
    url: https://github.com/ggml-org/llama.cpp
last_verified: "2026-10-15"
---

# 02.3 · Measure it: prompt speed vs generation speed
```

Sections, in order:

1. **Why it matters** — the home situation (slow answers, voice lag, RAM running out).
2. **How it works** — the mechanism, with a small worked example (bandwidth ÷ size).
3. **Show me** — our measured run on a named machine, with the numbers.
4. **Try it** — the lab: predict first (write the number down), then run, then compare.
   Links to `labs/module-NN/`. Commands for Windows / macOS / Linux where they differ.
5. **Break it** — a controlled failure (context too large, 0.0.0.0 bind, wrong Whisper
   size).
6. **Fix it** — the fix and why it works.
7. **How do I know it works?** — a check command or measured target (e.g. `doctor` passes,
   latency table filled).
8. **Use / don't use** — when this choice is right at home and when it is not; "If you have
   a GPU" note where relevant; optional "Do it yourself with llama.cpp" note (a few lines:
   the equivalent `llama-server` command and the parameters worth playing with) in
   lessons that touch runtime settings.
9. **Reflect** — one or two questions about the learner's own setup.
10. **Sources** — every cited number and doc.

The knowledge check lives in `lesson-MM.quiz.yaml`, not in the lesson.
