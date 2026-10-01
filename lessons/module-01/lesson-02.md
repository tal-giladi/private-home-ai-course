---
id: "01.2"
module: 1
minutes: 12
practice_minutes: 15
prerequisites: ["01.1"]
objectives:
  - Decode any model tag into family, parameter count, variant and quantisation without guessing.
  - Predict a download size and a rough speed class from a tag, before starting the download.
  - Explain why Q8_0 costs roughly twice the RAM and roughly twice the read time of Q4_K_M.
  - Tell an instruct model from a base model, and say why a `.bin` or `.pkl` weight file is a
    supply-chain risk rather than a convenience.
volatility: concept
sources:
  - title: "Ollama library — Qwen3 tags with their real file sizes and context windows"
    url: https://ollama.com/library/qwen3
  - title: "Hugging Face — the GGUF file format"
    url: https://huggingface.co/docs/hub/en/gguf
  - title: "Hugging Face — why pickle files are a security risk"
    url: https://huggingface.co/docs/hub/en/security-pickle
last_verified: "2026-09-30"
---

# 01.2 · Reading a model tag

A model name is not a label, it is a specification. `qwen3:4b-instruct-q4_K_M` tells you which
family it belongs to, roughly how many parameters it has, that it was tuned to follow
instructions, and how many bits each weight is stored in — which between them determine the
download size, the RAM it needs, and roughly how fast it will generate. Five minutes of learning
this saves an evening of downloading the wrong thing and wondering why it is slow.

## Why it matters

The failure this prevents is specific and common: you read a name, `llama3.1:8b`, imagine "a big
model", pull nearly 5 GB, and discover that on a 16 GB laptop it leaves no room for anything and
generates at a couple of tokens per second. Nothing about that experience tells you what went
wrong, because from the outside "too big" and "too slow" look identical.

It is also the skill that survives the course. The specific defaults here — `qwen3:4b`,
`llama3.2:3b`, `gemma3:1b` — will be replaced by something else eventually. What does not change is
that the name tells you the size, and the size is what your machine has to pay for.

> [!NOTE]
> macOS steps below are the same commands; the output is identical in shape. **They are not
> verified by us** — the course has one Windows test machine — and the one place a Mac genuinely
> differs is the download, because Apple Silicon machines usually have more spare disk than the
> Windows laptop this course was written on.

## How it works

### The shape of a tag

Ollama names a model `<family>:<tag>`, and the tag usually follows `<parameters>-<variant>-<quant>`.
The short tags people actually type are aliases for a specific full tag, and you can always see
which one you really have.

```bash
# the full information: architecture, parameter count, context window, quantisation
ollama show qwen3:4b

# the file it points at, layer by layer
ollama show --modelfile qwen3:4b
```

| Part | Example | What it decides |
|---|---|---|
| Family | `qwen3`, `llama3.2`, `gemma3` | Training data, licence, tool-calling support, personality |
| Parameters | `1b`, `3b`, `4b`, `8b` | Quality ceiling, download size, speed, RAM |
| Variant | `instruct`, `it`, or nothing | Whether the model answers questions or continues text |
| Quantisation | `Q4_K_M`, `Q5_K_M`, `Q8_0`, `F16` | Bytes per weight, and therefore memory and speed |

### Parameters: the big number

Parameters are the weights in the network, counted in billions. They set the ceiling on quality and
they set the floor on everything else. From Ollama's own library page for the Qwen3 family, the
file sizes at the default quantisation are:

| Tag | Size on disk | Context window listed |
|---|---|---|
| `qwen3:0.6b` | 523 MB | 40K |
| `qwen3:1.7b` | 1.4 GB | 40K |
| `qwen3:4b` | 2.5 GB | 256K |
| `qwen3:8b` | 5.2 GB | 40K |
| `qwen3:14b` | 9.3 GB | 40K |

Two lessons in one table. First, size grows faster than the parameter count, because the
vocabulary of the tokeniser is a large share of a small model's weights. Second, the context window
is a property of the *model*, and a large window in the model card is not a promise that you can
afford it — [05 · Settings that change the answer](../module-01/lesson-03.md) is where that bill
arrives.

Quality does not scale linearly with parameters, and the curve has a shape worth knowing: a 1B
model is a toy, 3–4B is where ordinary tasks start working, and 8B is where reasoning and
instruction-following become noticeably better — if your machine can pay for it. Below 1B, expect
to be disappointed in ways that are not your fault.

### Quantisation: the number after the letters

Quantisation stores each weight in fewer bits than the 32-bit floating point it was trained in.
Q8_0 is about 8 bits per weight, Q5_K_M about 5, Q4_K_M about 4. The `_K_M` suffix means a
specific block-wise scheme: 32 weights at a time, each block with its own scale, most blocks
quantised more carefully than the rest. Which scheme is *better* is an argument for people who
convert models; which scheme is *smaller* is arithmetic, and that is all this lesson needs.

| Quantisation | Approx. bytes per weight | 3B model, roughly | 4B model, roughly | Quality |
|---|---|---|---|---|
| `F16` | 2.0 | 6.0 GB | 8.0 GB | The original; not reachable on a home machine |
| `Q8_0` | 1.06 | 3.2 GB | 4.2 GB | Very close to the original |
| `Q5_K_M` | 0.68 | 2.0 GB | 2.7 GB | Almost indistinguishable from Q8_0 on chat |
| `Q4_K_M` | 0.55 | 1.6 GB | 2.2 GB | The home default; a small, real quality cost |
| `Q3_K_M` and below | 0.4 and down | 1.2 GB | 1.6 GB | Visible loss; only for a machine with nothing else |

The "roughly" is honest: real files land a little above this table, because not every tensor is
quantised the same way and the embedding layers in particular usually stay at higher precision.
That is why a "4-bit, 4-billion-parameter" model is 2.5 GB on disk and not 2.0.

**The speed consequence matters more than the quality one.** Generation re-reads the weights for
every token, so generation speed is roughly bytes-per-token divided by memory bandwidth. Moving
from Q4_K_M to Q8_0 nearly doubles the bytes you read and therefore nearly doubles the time per
token, on the same machine. You are buying a quality difference most people cannot hear, with a
speed difference everybody can feel.

> [!TIP]
> Tal's other Academy course, `ai-inference`, teaches quantisation properly in its Module 4 — how
> the block schemes differ, how to convert a model yourself, and how to measure the quality cost.
> This lesson gives you the intuition that is enough to pick a tag today.

### Instruct, base, and the difference you will notice

An instruct model has been trained on examples of following instructions, and it ships with a chat
template that wraps your message in the format it was trained on. A base model is the raw next-token
predictor: give it a question and it will happily continue the text, invent a new question, or
ramble, because to it everything is a continuation.

Tells: instruct replies to a question; base continues a document, repeats your question back, or
produces a plausible-looking Q&A section out of nothing. Most tags make it explicit —
`qwen3:4b-instruct-q4_K_M`, `gemma3:1b-it-q8_0` — and Ollama's library usually maps the short tag
to the instruct build. Verify rather than assume: `ollama show <tag>` prints the template the model
declares.

### Where the file comes from, and the file you must never accept

`ollama pull` fetches from Ollama's own library, which mirrors weights published by the model's
author under that author's organisation — the same GGUF files other runtimes use. The format,
[GGUF](https://huggingface.co/docs/hub/en/gguf), is a container: the weights, the quantisation
metadata, the tokeniser, the chat template and the model's own config in one file. That is why
`ollama show --modelfile` can tell you the context length and the template from a single object.

The alternative format is the dangerous one. Older checkpoints are PyTorch `.bin` or `.pkl` files,
and loading one is not a data load — it is a deserialisation that can execute arbitrary code on
your machine. Hugging Face documents this directly, and the rule it leads to is simple: **use
GGUF; never load a `.bin` or a `.pkl` from a stranger, and never run a "conversion script" somebody
sent you.** [Pinned models and licences](../../references/models.md) says the same thing in one
line, and Module 11's supply-chain lesson is where you will build the habit of checking where a
file came from before you run it.

## Show me

The three models this course defaults to, decoded:

| Tag | Family | Parameters | Variant | Quant | File, about | For |
|---|---|---|---|---|---|---|
| `qwen3:4b` | Qwen3 | 4 B | instruct | Q4_K_M | 2.5 GB | tier A and B chat, the default |
| `llama3.2:3b` | Llama 3.2 | 3 B | instruct | Q4_K_M | 2.0 GB | tier A chat, a little faster |
| `gemma3:1b` | Gemma 3 | 1 B | instruct | Q4_K_M | 0.8 GB | tier C, voice pipelines, cheap tasks |

`qwen3:4b` is an alias; the full tag behind it is in the `ollama show` output, and the alias is the
pin. Ollama tags are immutable — unlike a container tag of `latest`, `qwen3:4b` means the same file
today and next year, which is why [Pinned versions](../../references/versions.md) treats a model tag
as a version.

To see it for yourself, and to check a model you did not pull from this page:

```bash
# what is really in this model?
ollama show qwen3:4b

# compare three models on the fields that matter, in one screen
ollama show llama3.2:3b
ollama show gemma3:1b
```

## Try it

Pick three tags from the course's [pinned model list](../../references/models.md), decode them by
hand **before** you look anything up, then check yourself. This is the exercise that makes the
skill stick, and it takes five minutes.

```text
Tag 1: ______________________  family ____  params ____  variant ____  quant ____  size ~ ____ GB
Tag 2: ______________________  family ____  params ____  variant ____  quant ____  size ~ ____ GB
Tag 3: ______________________  family ____  params ____  variant ____  quant ____  size ~ ____ GB
```

Then verify the two numbers you are least sure about, the file size and the context window, from
the model itself rather than from this page:

```bash
ollama show <tag>          # Parameters, Quantization, Context Length
ollama list                # the size actually on your disk
```

Finally, make the size-versus-speed point real on your own machine with one extra download — a
higher quantisation of a model you already have:

```bash
# about 4.2 GB, against 2.5 GB for qwen3:4b
ollama pull qwen3:4b-instruct-q8_0
ollama run qwen3:4b-instruct-q8_0 --verbose "Explain in about 150 words why bridges have expansion joints."
```

Write both generation rates in [the measure-yours table](../../templates/measure-yours.md) and
compare them with the same question on `qwen3:4b`. The expected result is that the Q8_0 model is
slower, by roughly the ratio of the file sizes. If it is not slower, you have learned something
about your machine worth keeping — and you now own the number rather than the rule.

## Break it

**Break it with a size-based guess.** Read `qwen3:14b` as "14 gigabytes" and pull it on a 16 GB
laptop. The file is 9.3 GB, it loads, it answers — and it is unusable: no room for a browser, no
room for voice, and a generation rate measured in fractions of a token per second on a machine that
is also paging. The error message, if there is one, says "not enough memory", which is easy to
misread as "buy more memory" instead of "choose a smaller model".

**Break it with a base model.** Pull a base checkpoint and ask it something. It does not fail. It
produces text, which makes it look like a working model that is having a bad day: the question
repeated back, a fake transcript of a conversation that never happened, a list of twelve more
questions on the same topic. The instinct is to blame the runtime; the cause is in the tag.

**Break it with "let me have the quality".** Re-pull the same model at Q8_0 and watch memory
double and speed halve, on the same machine, with an answer that is not visibly better. This is the
break that wastes the most time, because the person doing it usually believes they are being
careful.

**Break it with a file somebody sent you.** A colleague's folder contains `model.bin` and a
`convert.py`. Running it means loading a file format that can execute code on your machine, from
someone's machine, with no signature. The result may be a perfectly good GGUF. That is the point:
it looks fine.

## Fix it

1. **Decode before you download.** Family, parameters, variant, quantisation, estimated size. If
   the estimated size is more than about a third of the RAM you want free afterwards, stop and use
   the next size down.
2. **Keep the quantisation at `Q4_K_M` unless you have a reason.** The reason is a task where you
   can see the quality difference; "it sounds more professional" is not a reason, because the
   speed cost is real and measurable.
3. **Check the variant.** If `ollama show` does not show a chat template, you have a base model and
   no setting will make it answer questions.
4. **Set the context from the model, not from ambition.** `ollama show <tag>` prints the context
   window; the default on a machine without a GPU is 4096, and every token of it costs memory.
5. **Only load files you can trace.** GGUF from a named publisher's own page, or through
   `ollama pull`. Never a `.bin`, never a `.pkl`, never a script you did not write.

## How do I know it works?

- [ ] You can decode an unfamiliar tag — family, parameters, variant, quantisation — and predict
      its download size to within about 20%.
- [ ] You have run `ollama show` on at least two models and matched the real quantisation and
      context window against your prediction.
- [ ] You have measured the same model at two quantisations and can say which one you would keep,
      with the two numbers behind that answer.
- [ ] You can explain, in one sentence, why `llama3.1:8b` is a bad idea on a 16 GB laptop.
- [ ] You know which of your local models is a base model, and what would happen if you asked it a
      question.

## Use it when / avoid it

**Read the tag before every pull, including the ones you are sure about.** The pull is the
expensive, slow, disk-consuming step; the tag is free. And read it for the *whole* name, not the
first two fields: a 3B model at Q8_0 is a 3.2 GB download, and a 4B at Q4_K_M is 2.5 GB, so the
quantisation can decide the download as much as the parameter count does.

**Change family before you change size, when the task is specific.** A model tuned for tool
calling will produce usable tool calls at 4B when a general 8B produces prose about tool calling;
that is a real difference in training, not a benchmark artefact, and it is the reason the course
measures a 30-command set in Module 10 rather than trusting a model card.

**Avoid reading a parameter count as a quality score.** Two models with 4B parameters can behave
very differently, and the one you will enjoy using is usually the one that was tuned for chat
rather than the one with the best numbers. Module 5 builds a small evaluation set out of your own
tasks for exactly this reason.

**Avoid downloading a model to test a theory about its size.** Compare tags on paper first; the
`ai-inference` course has the detail on why a given quantisation exists, and this course only
needs the three rows of the table above.

## Reflect

1. Which part of a tag do you still have to look up, and which part can you now read cold?
2. Your measured generation rate for `qwen3:4b` and for its Q8_0 build: what is the ratio, and does
      it match the ratio of the two file sizes? If it does not, what else could explain it?
3. Why is a `.pkl` weight file a different kind of risk from a `.gguf` weight file, when both
      arrive from a download?

## Sources

- [Ollama library — Qwen3 tags, file sizes and context windows](https://ollama.com/library/qwen3)
- [Hugging Face — the GGUF file format](https://huggingface.co/docs/hub/en/gguf)
- [Hugging Face — pickle files and the security risk they carry](https://huggingface.co/docs/hub/en/security-pickle)
- [Pinned models and licences](../../references/models.md) — the defaults, their licences and where the files come from
- [Pinned versions](../../references/versions.md) — why a model tag counts as a version
- [The Glossary](../../glossary.md) — token, context window, quantisation, GGUF
