---
id: "05.3"
module: 5
minutes: 11
practice_minutes: 30
prerequisites: ["05.2"]
objectives:
  - Tell apart the licences that matter for a private home use, and the ones that matter if you share or sell.
  - Explain why a model file can be an attack vector even when it is "just data", and what to check.
  - Find the authoritative licence and provenance for any model before you install it.
volatility: concept
sources:
  - title: "ReversingLabs — malicious models found on Hugging Face"
    url: https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face
  - title: "Piper voices repository"
    url: https://github.com/rhasspy/piper-voices
  - title: "Wiz — CVE-2024-37032 Probllama"
    url: https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032
last_verified: "2026-09-30"
---

# 05.3 · Licences and trusted sources

Two questions before you install anything: *may I use this?* and *do I trust it?* They are different
questions, and the second one is the one with a documented body of attacks behind it. Neither takes
long — but both are much harder to answer after you have indexed your documents and exposed your
home network.

## Why it matters

For a private stack, most model licences are fine: you download them, you run them at home, nobody
else sees the output. That is not the same as "they are all permissive", and the difference matters
if you ever build something somebody else runs.

The trust question matters more immediately. Model files are parsed by the runtime, they contain
their own chat templates, and they can be re-serialised in ways that execute code. Malicious models
have been found on a major model hub, and local model runtimes have had unauthenticated
remote-code-execution vulnerabilities through model file parsing — one of them, in the server this
course uses for everything, was a path traversal that became code execution and was worst exactly
where the docs put it: running as root inside a container, bound to every interface.

None of that requires an attacker to be clever about you. It requires one wrong file.

## How it works

### The licence families you will meet

| Licence | Where you meet it | What it means for you |
|---|---|---|
| **Apache-2.0** | `qwen2.5`, `qwen3`, `nomic-embed-text`, `gemma` tooling | Use freely, including commercially. No conditions. |
| **MIT** | `whisper` weights, `bge-m3`, `piper` code | Use freely, including commercially. Keep the notice. |
| **Community licences** (Llama, Gemma Terms) | `llama3.2`, `llama3.1`, `gemma3` | Use freely at home; an acceptable-use policy and, for Llama, a clause above 700 million monthly users |
| **Per-voice licences** | Piper voices | Varies per voice — CC-BY, MIT, or a community donor's terms. Check the voice's model card, not the code's. |
| **GPL** | Piper's current code release | Fine to run; matters if you distribute a modified binary |

> [!NOTE]
> Piper's active release moved to a GPL-licensed project, separate from the original MIT-licensed
> code. Running it at home is unaffected. Read the voice's own licence when you publish anything
> that speaks with it, because the voices are licensed separately from the engine.

For a course that is free and public, and for a learner running this at home, **Apache-2.0 and MIT
models are the comfortable default.** Prefer them when two models score the same on your eval set.
That is what [the model list](../../references/models.md) does, and why the defaults lean on Qwen.

### What makes a model file risky

A GGUF file is not an executable program, and yet:

- **Pickle-based formats run code on load.** `.pkl`, `.bin`, and the `torch.load` family execute
  arbitrary Python during deserialisation. Loading one is running untrusted code. There have been
  real cases of malware distributed this way on a public model hub.
- **Model files are parsed.** A malformed file has caused unauthenticated memory disclosure through
  the server that parses it. The fix on your side is an updated version and no exposed port.
- **A model card can contain a Jinja chat template**, and the template is executed at inference time
  by some runtimes. It is a small surface, but it is a surface.

### The four checks, in order

1. **Who published it?** A named organisation you recognise, or a person with a history you can see.
   Not a random upload with a good model name.
2. **What format is it?** GGUF or safetensors. Never a pickle, never a `.bin`, never a "conversion
   script" someone sent you in a message.
3. **What licence does the publisher's own page state?** Read it there. Not the summary in the
   download listing, and not this course's table — that table links to the authority and can be
   out of date.
4. **Does it match?** Compare the file's checksum with the one the publisher published, when they
   publish one.

## Show me

The course's default list, chosen for licence and provenance first and speed second:

| Model | Licence | Where the authority is |
|---|---|---|
| `qwen3:4b`, `qwen2.5:7b` | Apache-2.0 | [Qwen's own page](https://qwenlm.github.io/blog/qwen3/) |
| `gemma3:1b` | Gemma Terms of Use | [Google's Gemma docs](https://ai.google.dev/gemma/docs) |
| `llama3.2:3b` | Llama Community Licence | [Meta's Llama page](https://www.llama.com/llama3_2/) |
| `nomic-embed-text` | Apache-2.0 | [Hugging Face model card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) |
| Whisper (all sizes) | MIT | [github.com/openai/whisper](https://github.com/openai/whisper) |
| Piper voices | **per voice** | [piper-voices](https://github.com/rhasspy/piper-voices), the voice's own model card |
| openWakeWord | Apache-2.0 | [github.com/dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) |

And the rule the course follows everywhere: **if a licence is unclear, use a different model.**
There is no scenario in a home lab where being the first to try something is worth an unclear
provenance. This is the short version; Module 11 has the full routine and the monthly checklist.

## Try it

1. Pick any model from `ollama list` and find out where it came from:

   ```bash
   docker run --rm -v homelab-ollama-models:/root/.ollama ollama/ollama:0.35.0 ollama show qwen3:4b
   ```

   The output includes the licence and the parameter count. Treat the output as a pointer, not as
   the authority: open the publisher's page it names.

2. Do the four checks on one model you already have. Write the answers down:

   ```text
   Model: qwen3:4b
   Publisher: Qwen, Alibaba Cloud (named organisation, documented releases)
   Format:    GGUF, pulled from the runtime's own registry
   Licence:   Apache-2.0, stated on the publisher's blog page (linked)
   Checksum:  not published separately; the registry is the source of record
   ```

3. Do the same for a model you are curious about but have not installed — a fine-tune of a base
   model by somebody with no other releases, for example. Ask the four questions *before*
   installing it. Most of the time the answer to question one ends the conversation.

4. Check the voice, separately from the engine. Piper's repository has hundreds of community voices
   with different licences. Open the model card for the exact voice you plan to use and read it.
   This is the step people skip, because a TTS voice feels like an accessory rather than a work.

5. Record your decision, even when it is trivial, in one line in the
   [capstone write-up](../../templates/capstone-write-up.md):

   ```text
   Everything installed came from: the runtime's own registry, publishers named in references/models.md.
   I did not install any file from a direct link or a message.
   ```

6. Check your stack's running versions against the advisories once, so that the first time you need
   to do this you are not doing it for the first time:
   <https://github.com/ollama/ollama/security/advisories> and
   <https://github.com/open-webui/open-webui/security>.

## Break it

**Break it with a pickle.** Find a `.pth`, `.pkl` or raw `.bin` "model" offered as a faster
alternative to GGUF, and load it in anything that calls `torch.load`. That is arbitrary code
execution at load time, not a theoretical risk.

**Break it with a fine-tune of unknown provenance.** It performs well on your eval set, it is
faster than the official model, and the publisher is an account with one upload. Nothing about it
is checkable, and the whole point of a home stack is that you know what is running in your house.

**Break it with a stale runtime.** An exposed model server has had both a path-traversal remote code
execution and an unauthenticated memory disclosure through a malformed model file. Neither needs
anyone clever about you — they need an old version and a reachable port, and both are ordinary
things to have on a home network by accident.

**Break it by assuming "private means it does not matter".** It matters for one thing above all
others: what is allowed to *run* in your house. An indexer is the most exposed part of the stack
precisely because it processes every file you give it.

## Fix it

| Signal | What to do |
|---|---|
| `.pkl`, `.pt`, `.pth`, `.bin` offered as a model | Do not load it. Convert from a published GGUF instead. |
| Publisher is an account with no other releases | Do not install it, whatever it scores on your eval set |
| Licence unclear or "contact us" | Use a different model |
| Model file checksum does not match | Do not use the file; re-download, and if it differs again, stop |
| Voice licence is not stated on its own model card | Use a voice that states one |
| A runtime has a known advisory | Update before anything else; an exposed unauthenticated API is the priority |

The general form of the answer is always the same: **remove, do not mitigate.** In a home stack
there is a working alternative for every bad file, so there is never a reason to reason about the
risk instead.

## How do I know it works?

- [ ] Every model in your stack is listed in [references/models.md](../../references/models.md), or
      in your own notes with the same four fields.
- [ ] You know the publisher of each one and could find their page without searching.
- [ ] Every Piper voice you use has a licence you read on that voice's own model card.
- [ ] Nothing you installed came from a direct link, a chat message, or an unfamiliar account.
- [ ] You have visited your runtime's advisories page once, so you know what it looks like.

## Use it when / avoid it

**Read the licence whenever you install, not whenever you publish.** Retroactively checking is how
you end up with a stack you cannot legally redistribute and no time to fix it.

**Prefer permissively licensed models when the eval scores are close.** If `qwen3:4b` and another
model pass the same 17 of 20, take the one whose licence is Apache-2.0. It costs you nothing and it
keeps the option open.

**Do not treat a Hugging Face download count as provenance.** Popularity and trustworthiness are
different axes, and a malicious upload can be popular for exactly the week it is discovered.

**Avoid running two different people's stacks on the same network**, particularly a model indexer.
If you must, Module 11's segmentation is the answer.

> [!TIP]
> **Practical shortcut.** If a model is not on [the course's pinned list](../../references/models.md)
> and you cannot answer all four questions about it in two minutes, do not install it. That rule has
> never produced a regret, and the model you will install instead is almost always fine.

## Reflect

1. Name every licence in your stack, and say which one you would have to act on if you ever showed
   a friend how to build the same thing.
2. Which file in your stack was downloaded from the least obvious source, and what made you
   comfortable with it?
3. What would you do if a model scored 20 out of 20 on your eval set and you could not identify
   who published it?

## Sources

- [ReversingLabs — malicious machine-learning models on a public hub](https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face)
- [Wiz — CVE-2024-37032 "Probllama", a path traversal to remote code execution](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032)
- [Ollama security advisories](https://github.com/ollama/ollama/security/advisories)
- [Piper voices — per-voice licences](https://github.com/rhasspy/piper-voices)
- [Piper, current GPL release](https://github.com/OHF-Voice/piper1-gpl)
- [Pinned models and licences](../../references/models.md)
- [40 · Updates, CVEs and model supply chain](../module-11/lesson-04.md)