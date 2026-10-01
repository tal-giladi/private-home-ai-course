# Course details (for registering the course in the Academy and filling Admin)

- **Suggested slug:** `private-home-ai`
- **GitHub repo:** `tal-giladi/private-home-ai-course` (public; nothing behind a paywall and no
  secrets in the tree, so a public repo imports without a token)
- **Free or paid:** free. Tal decides; the plan targets a public course.
- **Risk notice:** the course asks you to open firewall, router and microphone permissions on your own
  machine, and includes a deliberately vulnerable local lab. Everything runs against your own
  computer only; never port-forward a model server.
- **One-line summary:** Turn an ordinary 16–32 GB computer into a private home AI stack — local chat,
  question answering over your own files and an offline voice assistant for Home Assistant — with no
  GPU, no cloud account and no subscription.
- **Who it is for:** developers, IT people, makers and Home Assistant hobbyists who are comfortable
  in a terminal and want AI at home without sending their data to a cloud service.
- **Format:** 13 modules, 44 lessons (10–12 h core path, +8–10 h voice path, +6–8 h ops path), each
  lesson a read plus a lab, every module with a multiple-choice quiz, and a capstone on the learner's
  own machine.
- **Prerequisites:** terminal basics (cd, editing a file, running a command), installing software, and
  the words router and IP address. No ML background, no Docker (on-ramp in M3), no Home Assistant
  experience, no smart-home hardware. Python is used but never required to write.

## What you will learn

- Run quantized 1–8B models locally with Ollama and llama.cpp, and read a model tag (size,
  quantization, context, instruct vs base) correctly.
- Predict generation speed and RAM use from memory bandwidth and model size, then measure your own
  machine, and pick the largest model that still meets your speed target.
- Run a persistent stack with Docker Compose — model server, chat UI, vector store — on volumes that
  survive upgrades, with pinned versions.
- Choose a model per job (chat, tool calling, embeddings) using an evaluation set built from your own
  tasks instead of a leaderboard.
- Build a fully local Assist pipeline over the Wyoming protocol (wake word → speech-to-text → intent
  or LLM → text-to-speech) and measure its end-to-end latency stage by stage.
- Let a local LLM control Home Assistant through tools while limiting what it can touch and
  requiring confirmation for risky actions.
- Threat-model a home AI stack, keep every service off the public internet, reach it over a VPN, and
  run an update, backup and model-supply-chain routine.
- Prove the "no cloud" claim by blocking outbound traffic and showing every feature still works.

## Notes for Tal

- macOS steps are written but **not verified by us** (only one Windows test machine, plan §12 Q11).
  Every macOS lab section is labelled accordingly.
- The phase-1 spike (`homelab doctor` / `homelab bench` numbers on Tal's Core Ultra 7 laptop) is not
  done. Lessons use cited numbers with the source machine named, plus a "measure yours" step, and
  never present a speed as a guarantee.
- M6 (RAG) is optional and self-contained; `rag-course` is the "go deeper" link, not a prerequisite.
