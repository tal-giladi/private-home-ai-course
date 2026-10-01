# Glossary

Every term the course uses, with a link to the lesson that introduces it. If a word here is new to
you, that lesson is the right place to pick it up.

## A

- **Assist** — Home Assistant's built-in voice and text assistant, which turns a sentence into
  intent plus slots, or hands the sentence to a conversation agent. Introduced in
  [24 · Assist with typed commands](lessons/module-07/lesson-02.md).
- **Apple Silicon** — a Mac processor with unified memory shared by CPU and GPU. Introduced in
  [10 · Choose the host](lessons/module-03/lesson-01.md).

## B

- **Bandwidth, memory** — how many bytes per second the RAM subsystem can deliver to the CPU. It,
  not core count, is what limits generation speed. Introduced in
  [06 · Memory bandwidth sets your speed](lessons/module-02/lesson-01.md).
- **Bind address** — the network interface a service listens on. `127.0.0.1` is only this computer;
  `0.0.0.0` is every interface, including the one the router can reach. Introduced in
  [38 · Bind addresses and ports](lessons/module-11/lesson-02.md).
- **Binding, memory** — the row in a compose file that maps a container port to a port on the host.
  Distinguished from the bind address in [11 · Docker Compose on-ramp](lessons/module-03/lesson-02.md).

## C

- **Context window** — how many tokens the model can see at once: the system prompt, the
  conversation so far and the reply. Introduced in [04 · Reading a model tag](lessons/module-01/lesson-02.md).
- **Conversation agent** — the component in Home Assistant that lets an LLM decide which tools to
  call, as opposed to matching fixed intents. Introduced in
  [33 · The Ollama conversation agent](lessons/module-10/lesson-01.md).
- **CPU-only** — running inference without a GPU. The whole assumption of this course.

## D

- **Docker Compose** — one YAML file describing several services, their volumes and networks, so the
  whole stack starts and stops with one command. Introduced in
  [11 · Docker Compose on-ramp](lessons/module-03/lesson-02.md).

## E

- **Embedding** — a list of numbers that represents the meaning of a piece of text, so that similar
  texts land close together. Introduced in [17 · One model per job](lessons/module-05/lesson-01.md).
- **Eval set** — your own list of real tasks with known-good answers, used to compare models on the
  work you actually do. Introduced in [18 · Build your own eval set](lessons/module-05/lesson-02.md).
- **Exposure** — anything reachable from the internet that should not be. Discussed in
  [37 · Threat-model your home AI stack](lessons/module-11/lesson-01.md).

## F

- **False accept** — the wake word firing when nobody said it. Contrasted with a false reject in
  [30 · Wake words that do not lie to you](lessons/module-09/lesson-01.md).

## G

- **GGUF** — the file format local model weights come in. Introduced in
  [04 · Reading a model tag](lessons/module-01/lesson-02.md).
- **Groundedness** — whether an answer is actually supported by the text it cites, rather than
  fluent and made up. Introduced in [22 · Is the answer right?](lessons/module-06/lesson-03.md).

## H

- **Home Assistant (HA)** — the open-source home automation platform this course runs in a
  container. Introduced in [23 · Home Assistant Container in the stack](lessons/module-07/lesson-01.md).
- **Hot context** — the tokens the model has to re-read on every single token of the reply. Discussed
  in [06 · Memory bandwidth sets your speed](lessons/module-02/lesson-01.md).

## I

- **Intent** — a fixed, named action Home Assistant can perform, such as `HassTurnOn`, matched from a
  sentence by built-in or custom sentences. Introduced in
  [24 · Assist with typed commands](lessons/module-07/lesson-02.md).

## K

- **KV cache** — the memory holding what the model has read so far, so it does not re-read it for
  every new token. It grows with context length. Introduced in [07 · The RAM bill](lessons/module-02/lesson-02.md).

## L

- **Latency budget** — the maximum time each stage of a pipeline may take before the product feels
  broken. Introduced in [29 · Measure the voice pipeline](lessons/module-08/lesson-04.md).
- **llama.cpp** — the inference library, and the `llama-bench` and `llama-server` tools, used in
  this course to measure rather than to serve. Introduced in
  [03 · Install Ollama and run your first model](lessons/module-01/lesson-01.md).

## M

- **Misfire** — a voice command the assistant understood wrongly and acted on anyway. Measured in
  [35 · Tools and guardrails](lessons/module-10/lesson-03.md).
- **Model tag** — the whole name of a model, for example `qwen3:4b-instruct-q4_K_M`, read piece by
  piece in [04 · Reading a model tag](lessons/module-01/lesson-02.md).

## O

- **Ollama** — the default model runtime in this course: it downloads, stores and serves models, and
  exposes an HTTP API. Introduced in [03 · Install Ollama and run your first model](lessons/module-01/lesson-01.md).
- **OpenAI-compatible API** — the shape of request and response that most local runtimes imitate so
  that ordinary client code works. Introduced in
  [14 · Talk to your model over HTTP](lessons/module-04/lesson-01.md).

## P

- **Pipeline** — a chain of services, such as wake word → speech-to-text → intent → text-to-speech.
  Introduced in [26 · The Wyoming protocol](lessons/module-08/lesson-01.md).
- **Port forward** — a router setting that exposes a device on your LAN to the internet. This course
  never uses one, and [38 · Bind addresses and ports](lessons/module-11/lesson-02.md) explains why.
- **Profile** — a named subset of services in a compose file, so optional parts start only when you
  ask. Introduced in [12 · The shared stack](lessons/module-03/lesson-03.md).
- **Prompt processing** — the work of reading the prompt, measured in tokens per second; it decides
  how long you wait before the first word. Contrasted with generation in
  [08 · Measure prompt speed and generation speed](lessons/module-02/lesson-03.md).

## Q

- **Quantization** — storing model weights in fewer bits so the file is smaller and faster to read.
  Introduced in [04 · Reading a model tag](lessons/module-01/lesson-02.md).

## R

- **RAG** — retrieval-augmented generation: find relevant chunks in your own files, put them in the
  prompt, and let the model answer from them. Introduced in
  [20 · Wire a local RAG service into the stack](lessons/module-06/lesson-01.md).
- **Real-time factor (RTF)** — how much faster than real time a stage runs. Below 1.0 is faster than
  live. Introduced in [29 · Measure the voice pipeline](lessons/module-08/lesson-04.md).
- **Retain, keep-alive** — how long a model stays in RAM after a request before it is unloaded.
  Introduced in [15 · Two models, one box](lessons/module-04/lesson-02.md).

## S

- **Satellite** — a device that listens for the wake word and streams audio, while the heavy
  services run elsewhere. Introduced in [31 · Your laptop as a voice satellite](lessons/module-09/lesson-02.md).
- **Speech-to-phrase** — a very small speech-to-text model that only recognises the phrases you
  define, and is fast enough to stay under a second on a Raspberry Pi. Introduced in
  [27 · Speech-to-text on your CPU](lessons/module-08/lesson-02.md).
- **Speech-to-text (STT)** — turning speech into text. Contrasted with text-to-speech in
  [08 · Speech in and out](lessons/module-08/lesson-01.md).

## T

- **Tailscale / WireGuard** — VPN software that gives your home services a private address reachable
  from your phone without opening any port. Introduced in
  [39 · Remote access the safe way](lessons/module-11/lesson-03.md).
- **Tier** — which of the three hardware bands your machine falls into: A (16 GB laptop), B (32 GB
  desktop or mini PC), C (8–16 GB low-power). Introduced in
  [02 · Find your tier with homelab doctor](lessons/module-00/lesson-02.md).
- **Token** — the unit a model reads and writes, roughly three-quarters of an English word.
  Introduced in [04 · Reading a model tag](lessons/module-01/lesson-02.md).
- **Tool call** — a structured request from a model to run a function with specific arguments.
  Introduced in [35 · Tools and guardrails](lessons/module-10/lesson-03.md).

## V

- **VLAN** — a separate network on the same cable, used to keep untrusted IoT devices away from your
  AI box. Introduced in [39 · Remote access the safe way](lessons/module-11/lesson-03.md).
- **Vector store** — the database that holds embeddings and finds the nearest ones. Introduced in
  [20 · Wire a local RAG service into the stack](lessons/module-06/lesson-01.md).

## W

- **Wake word** — the phrase that starts a voice interaction, like "hey jarvis". Introduced in
  [30 · Wake words that do not lie to you](lessons/module-09/lesson-01.md).
- **Whisper** — OpenAI's speech-to-text model family, open weights, multilingual, slow on a CPU in
  the larger sizes. Introduced in [27 · Speech-to-text on your CPU](lessons/module-08/lesson-02.md).
- **Wyoming protocol** — the small protocol that links wake word, speech-to-text, intent and
  text-to-speech services together. Introduced in [26 · The Wyoming protocol](lessons/module-08/lesson-01.md).

---

More depth on some of these topics lives in other Tal's Academy courses: RAG in `rag-course`,
inference and quantization in `ai-inference`, attacks on LLM services in `ai-security-course`, and
container networking in `kubernetes`. This course teaches the home-lab version of each and links out
rather than duplicating.
