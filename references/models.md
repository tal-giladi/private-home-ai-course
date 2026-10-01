# Pinned models and licences

The default list the labs use. One model per tier for chat, one small model for tool calling, one
embedder, one speech-to-text model, one text-to-speech voice.

> [!IMPORTANT]
> This list is **provisional**. The course plan ([`curriculum/course-details.md`](../curriculum/course-details.md))
> says the defaults are chosen after benchmarks on the maintainers' own machines, and that has not
> happened yet. Everything here is a defensible starting point, not a measured winner. After
> Module 2 and Module 5, replace anything that does not fit your machine or your tasks.

Licences are what the publisher states; **the publisher's own page is the authority**, and it is
linked for every entry. Re-read it before you redistribute a model or sell something built on it.

## Chat models

| Tier | Model tag | Parameters | Q4_K_M file, about | Licence | Publisher |
|---|---|---|---|---|---|
| C | `gemma3:1b` | 1 B | 0.8 GB | Gemma Terms of Use | [Google DeepMind](https://ai.google.dev/gemma/docs) |
| C / A | `qwen2.5:1.5b` | 1.5 B | 1.0 GB | Apache-2.0 | [Qwen](https://qwenlm.github.io/blog/qwen2.5/) |
| A | `llama3.2:3b` | 3 B | 2.0 GB | Llama 3.2 Community Licence | [Meta](https://www.llama.com/llama3_2/) |
| A | `qwen3:4b` | 4 B | 2.5 GB | Apache-2.0 | [Qwen](https://qwenlm.github.io/blog/qwen3/) |
| B | `qwen2.5:7b` | 7 B | 4.7 GB | Apache-2.0 | [Qwen](https://qwenlm.github.io/blog/qwen2.5/) |
| B | `llama3.1:8b` | 8 B | 4.9 GB | Llama 3.1 Community Licence | [Meta](https://ai.meta.com/blog/meta-llama-3-1/) |

Sizes are approximate for the Q4_K_M quantisation and differ by a few percent per quant. Check the
real number on your disk rather than trusting this column:

```bash
ollama show qwen3:4b --modelfile | head -20   # lists the blob it pulls
ls -lh ~/.ollama/models/manifests              # macOS / Linux
```

**Why these and not others.** A 3B or 4B instruct model is the sweet spot for a 16 GB laptop: it
leaves room for a browser, an embedder and the voice services at the same time. A 7–8B is worth it
on 32 GB only if your bandwidth supports it — see
[09 · Pick the largest model that meets your target](../lessons/module-02/lesson-04.md).

> [!NOTE]
> The Llama community licences are not OSI open source: they carry an acceptable-use policy and a
> monthly active-user clause above 700 million. For a private home stack this does not affect you.
> If you want a chat model with no strings attached, `qwen2.5` and `qwen3` are Apache-2.0.

## Tool calling (Module 10)

| Model tag | Why | Licence |
|---|---|---|
| `qwen3:4b` | Ships with tool-calling support and fits a 16 GB machine | Apache-2.0 |
| `qwen2.5:7b` | Fewer malformed tool calls, needs 32 GB | Apache-2.0 |

Small models are unreliable at tool calls. That is why Module 10 measures a misfire rate on a fixed
30-command set instead of trusting a model card, and why the default pipeline is *intents first,
LLM as fallback*.

## Embeddings (Module 6)

| Model tag | Size | Licence | Notes |
|---|---|---|---|
| `nomic-embed-text` | 274 MB | Apache-2.0 | 768 dimensions, needs a `search_` prefix for best results |
| `bge-m3` | 1.2 GB | MIT | multilingual, 1024 dimensions, better for non-English folders |
| `snowflake-arctic-embed2` | 570 MB | Apache-2.0 | A good small English-only option |

`nomic-embed-text` was trained partly on English web text; `bge-m3` is the safer default for a mixed
Hebrew/English folder. Embedding a folder is CPU work but it is short prompts and high throughput, so
it finishes in minutes, not hours — see [17 · One model per job](../lessons/module-05/lesson-01.md).

## Speech-to-text (Module 8)

| Model | File, about | RAM, about | Licence | Notes |
|---|---|---|---|---|
| Whisper `tiny` (multilingual) | 75 MB | 273 MB | MIT | Rough; fine for "stop", digits |
| Whisper `base` (multilingual) | 142 MB | 388 MB | MIT | The default for a 16 GB machine |
| Whisper `small` (multilingual) | 466 MB | 852 MB | MIT | Noticeably better; 32 GB machines |
| Whisper `medium` (multilingual) | 1.5 GB | 2.1 GB | MIT | Too slow for voice on most CPUs |

Memory figures are from the [whisper.cpp README](https://github.com/ggml-org/whisper.cpp). Real-time
factors and the reasoning behind the choices are in
[27 · Speech-to-text on your CPU](../lessons/module-08/lesson-02.md).

> [!IMPORTANT]
> Use the **multilingual** models, never the `.en` variants. The `.en` English-only models are
> smaller and slightly faster, which makes them very tempting — and they silently produce garbage on
> anything that is not English. The course is built Hebrew-ready and the lab samples are English only
> for now.

Alternative: **Speech-to-Phrase**, Home Assistant's own model that only recognises phrases you
declare. It is fast enough to stay under a second on a Raspberry Pi, at the cost of a fixed command
set. Covered in [27 · Speech-to-text on your CPU](../lessons/module-08/lesson-02.md).

## Text-to-speech (Module 8)

| Voice | Size | Quality | Licence |
|---|---|---|---|
| `en_US-lessac-medium` | ~60 MB | Good, the default | See the voice's MODEL_CARD |
| `en_US-amy-medium` | ~60 MB | Clearer, slightly slower | See the voice's MODEL_CARD |
| `en_GB-alba-medium` | ~60 MB | Scottish English | See the voice's MODEL_CARD |
| `en_US-hfc_female-medium` | ~60 MB | Natural cadence | See the voice's MODEL_CARD |

Piper voices are **licensed individually**, and the licences are not all the same: some are MIT,
some are CC-BY, and the community voices are donated under their own terms. The repository is
[rhasspy/piper-voices](https://github.com/rhasspy/piper-voices); check the `MODEL_CARD` for the exact
voice you pick before you publish anything with it. Hebrew voices are scarce and mostly community
contributions — see the note in [28 · Text-to-speech with Piper](../lessons/module-08/lesson-03.md).

## Wake word (Module 9)

| Model | Size | Licence | Notes |
|---|---|---|---|
| openWakeWord "prebuilt" bundle | ~20 MB | Apache-2.0 | ~20 models, 15–20 run in real time on one Pi 3 core |
| openWakeWord "verified" custom models | varies | Apache-2.0 | Use when you train your own on a few hours of your own voice |

Targets from the [openWakeWord README](https://github.com/dscripka/openWakeWord): fewer than 0.5
false accepts per hour and fewer than 5% false rejects. Both are goals for a trained model on a quiet
room, not guarantees on yours.

## Where model files come from

- **Chat and embedding models:** pulled by Ollama from its own registry, from the publisher's
  official organisation page. `ollama pull <tag>` is the only command the labs use.
- **Whisper:** downloaded by `faster-whisper` / Home Assistant from Hugging Face under
  `openai/whisper-*`, or compiled into whisper.cpp releases.
- **Piper:** downloaded by Home Assistant's Piper integration or by the `piper-tts` packages.
- **GGUF weights for llama.cpp:** from a named quantiser's Hugging Face repository. Never a `.bin`,
  never a `.pkl`, never a "converter script" someone sent you.

Model supply chain is Module 11's subject, and the short version is in
[40 · Updates, CVEs and model supply chain](../lessons/module-11/lesson-04.md).

## Swapping a default

You do not need to edit a lesson to use a different model. Every lab takes the model name from
`labs/common/.env`:

```dotenv
CHAT_MODEL=qwen3:4b
TOOL_MODEL=qwen3:4b
EMBED_MODEL=nomic-embed-text
STT_MODEL=base
TTS_VOICE=en_US-lessac-medium
```

Change it, re-run `python homelab.py bench`, and write the new number in your measure-yours table.
That is the whole point of the course: the method, not the list.
