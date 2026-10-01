---
id: "02.4"
module: 2
minutes: 12
practice_minutes: 25
prerequisites: ["02.3"]
objectives:
  - Turn a job into a numeric speed target, in tokens per second, for chat, voice and retrieval.
  - Apply three filters — RAM, generation speed, prompt speed — and take the largest model that
    survives all three.
  - Predict first, measure second, and write down the gap and its explanation.
  - Name what you would give up, in order, if nothing on your list meets your target.
volatility: concept
sources:
  - title: "Stratosphere — LLM performance on Raspberry Pi 5, with the memory specification"
    url: https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html
  - title: "Home Assistant — the local voice pipeline and its stages"
    url: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
  - title: "Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard"
    url: https://github.com/geerlingguy/ai-benchmarks
last_verified: "2026-09-30"
---

# 02.4 · Pick the largest model that meets your target

The last lesson of Module 2 is a decision, and the decision has a shape: a hard memory limit, a
speed requirement, and a preference for the best answer you can actually afford. Apply those three
in that order and the choice stops being a matter of taste. Get it wrong and nothing else in the
course matters, because every service you build afterwards inherits the answer.

## Why it matters

Two numbers describe almost every home AI disappointment. "It fits in RAM" and "it is fast enough"
are different claims, and the first one is the one people check. A 7B model on a 16 GB laptop
satisfies the first and fails the second, every time, and it fails *quietly*: the answer arrives,
correctly, a character at a time, and the user concludes the model is bad.

The inverse failure is just as common and less discussed. People who benchmark on a fast machine
and deploy on a slow one pick a model that meets a target on a desktop and misses it by a factor of
three on the machine that has to run it. The number that matters is the one from *your* machine,
and you have it now — in [08 · Measure prompt speed and generation
speed](../module-02/lesson-03.md)'s table, with your own efficiency factor in it.

## How it works

### Step 1: turn the job into a number

A target you cannot write down is a wish. These are the course's starting targets, all of them
**targets rather than measurements**, and the reasoning is in the
[latency budget](../../references/benchmarks.md):

| Job | What the user experiences | Target | What that means in tok/s |
|---|---|---|---|
| Chat | Answer appears as it is written | 8–10 tok/s | Comfortable to read; roughly a fast typist |
| Voice assistant brain | Speech ends, reply starts | 3 s budget for this stage | About 20–25 tok/s for a 3-second spoken answer |
| Question over your own files | Nothing, then everything | Prompt stage under 2–3 s | A prompt rate high enough for 2 000 tokens to fit in that |

Pick the row that matches what you are building first, and write the number next to it. If you
are doing chat, 8 tok/s is the target. If you are building a voice assistant, the 3-second stage
budget is the target and it is much harder, because the whole spoken round trip has a 5-second
ceiling of which this stage is the largest part.

### Step 2: apply three filters, in order

**Filter 1 — memory, and it is a hard stop.** The model must fit with 8 GB to spare, using the
bill from [07 · The RAM bill](../module-02/lesson-02.md). A model that does not fit is not a slow
model, it is a machine that will start paging, and paging is roughly two orders of magnitude
slower than memory.

**Filter 2 — generation speed.** Multiply your peak bandwidth by your measured efficiency factor,
divide by the file size, and compare with the generation target. Models that fall below the target
are out.

**Filter 3 — prompt speed.** Same arithmetic against the file size, compared with your prompt target.
This filter only bites for retrieval, and when it bites it removes everything, because prompt
throughput depends on cores and instructions rather than on the file.

**Then, and only then, take the largest survivor.** The reason this rule is right rather than
merely tidy: quality moves in steps — a 1B is a toy, 3–4B is where ordinary tasks work, 7–8B is
where reasoning improves — while speed falls continuously as the file grows. So the largest model
that still clears your bar is always at least as good as every smaller one, and there is no
trade-off left to agonise over.

### Step 3: the worked decision

On a Raspberry Pi 5, where the memory specification is published and four models have been
measured. Effective bandwidth: 17.1 GB/s × 0.5 = 8.55 GB/s.

| Candidate | File | Predicted generation | Chat target 8 tok/s | Voice target 22 tok/s |
|---|---|---|---|---|
| `gemma3:1b` | 0.8 GB | 10.7 tok/s | passes | fails |
| `llama3.2:1b` | 0.8 GB | 10.7 tok/s | passes | fails |
| `qwen2.5:1.5b` | 1.0 GB | 8.6 tok/s | passes | fails |
| `llama3.2:3b` | 2.0 GB | 4.3 tok/s | fails | fails |
| `qwen2.5:3b` | 2.0 GB | 4.3 tok/s | fails | fails |

The predictions line up with the published measurements on that machine — 11.5 tok/s for Gemma 3
1B, 11.2 for Llama 3.2 1B, 10.0 for Qwen2.5 1.5B, 4.6–4.9 for Llama 3.2 3B and 5.2 for Qwen2.5
3B, all from [Stratosphere](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html)
— which is the check that the filter is measuring the right thing. And the decision follows:

- **Chat on a Pi 5:** `llama3.2:3b` at 4.6 tok/s is too slow to read comfortably; the largest model
  that passes is a 1.5B, or a 1B if you want margin. Chat is where a Pi 5 feels the constraint.
- **The voice brain on a Pi 5:** nothing passes. 10.7 tok/s against a 22 tok/s target, and the
  largest gap in the table. The correct answer here is *not* a smaller download: it is a different
  design — fixed intents first, the model only as a fallback — which is exactly the default
  pipeline in Module 10, and it is why that module is designed the way it is.
- **The same Pi 5, same three models, different tier:** on an Intel N150 the same 3B model manages
  9.1 tok/s ([Geerling](https://github.com/geerlingguy/ai-benchmarks)), which clears the chat
  target. The model did not change; the machine did.

### The ladder, when nothing fits

If no model clears your target, the fix is one of these, in this order:

1. **Check the target.** Is it somebody else's number? 8 tok/s for chat is a course default, and
   you may be perfectly happy reading at 6.
2. **Drop a size.** 7–8B to 3–4B is the biggest quality step you can buy with bandwidth.
3. **Change the quantisation.** Q8_0 to Q4_K_M roughly doubles the speed. It costs a little quality
   and saves nothing in memory terms you were not already counting.
4. **Shorten the context.** Fewer bytes per token, so faster tokens, and less memory.
5. **Change the design.** For voice, intents first and the model as a fallback; for retrieval,
   smaller retrieved chunks and a reranking-free search.
6. **Change the machine.** This is the only step that fixes a voice target on a Pi 5, and
   [10 · Choose the host](../module-03/lesson-01.md) is where you make that decision with numbers
   rather than enthusiasm.

Step 6 is the honest one and the one people skip. If your target cannot be met on the hardware you
have, no amount of tuning reaches it, and the correct engineering answer is to say so out loud
rather than to ship something that misses the budget on every request.

### The long-prompt warning, one more time, because retrieval is where it bites

A retrieval-augmented question is not a chat question with a document attached. It carries the
retrieved chunks, the question, and often the conversation — thousands of prompt tokens — and then
generates a short answer. The generation target is easy to meet; the prompt target is the one that
fails, because the cited prompt rates in this course run from about 31 tok/s on a Ryzen AI laptop to
over 100 tok/s at `pp512` on a Ryzen 9 7950X. Do the arithmetic with **your** prompt rate, for
**your** typical chunk count, before you commit to the feature. If the first-word wait is 20
seconds, the honest options are smaller chunks, fewer of them, a model with a faster prompt stage, or
a design where the retrieval result is cached and the model only sees a summary.

## Show me

The worksheet. Copy this, fill it in with your own numbers from Module 2, and the decision writes
itself. The last column is the one that makes it a decision rather than a guess.

```text
My peak bandwidth:         ____ GB/s      (memory type x channels)
My efficiency factor:      ____           (from 02.3)
My headroom after the bill: ____ GB        (from 02.2)
My generation target:      ____ tok/s     (8-10 chat / ~22 voice)
My prompt target:          ____ tok/s     (whatever your longest prompt needs)

Candidate     File    RAM ok?   Predicted gen   Predicted prompt   Verdict
__________   _____   _______   ____________   ________________   _______
__________   _____   _______   ____________   ________________   _______
__________   _____   _______   ____________   ________________   _______
__________   _____   _______   ____________   ________________   _______

My decision:  ____________________  predicted ____ tok/s
Predicted prompt stage for a 2 000-token question: ____ tok/s = ____ seconds
```

And here is the version of that worksheet with the two most common machine classes already filled
in from published numbers, so you can see the shape of a finished decision:

| Machine | Memory | Effective bandwidth | Chat target 8 | Voice target 22 | Largest that passes for chat |
|---|---|---|---|---|---|
| Raspberry Pi 5, 8 GB | 17.1 GB/s | 8.6 GB/s | 1.5B | none | 1.5B (10 tok/s cited) |
| Intel N150, 16 GB | about 25–30 GB/s | 12.5–15 GB/s | 3B | none | 3B (9.1 tok/s cited) |
| Ryzen mainboard | dual-channel DDR | 40 GB/s+ | 7–8B | 4B | 7–8B, pending your measurement |

Those effective bandwidths are arithmetic on published specifications, not measurements, and the
speeds are the cited ones with the machine named. Your row is the one you produce.

## Try it

Do the whole decision on paper first, then verify one number in it. Twenty-five minutes, and it
is the last thing this module asks of you.

1. **Write your target.** One number, from the table above, for the job you are building first.
2. **List three candidates** from the [pinned model list](../../references/models.md) — a small
   one, a middle one and a large one.
3. **Fill the worksheet.** Predicted speed for each, from your own efficiency factor.
4. **Check the RAM bill** for the winner at your context length.
5. **Measure the winner** with `python homelab.py bench --model <winner> --models-only`.
6. **Write the gap and explain it.** This is the deliverable, in these words:

```text
My target:                ____ tok/s generation, ____ tok/s prompt
My prediction for <winner>: ____ tok/s generation, ____ tok/s prompt
My measurement:            ____ tok/s generation, ____ tok/s prompt
Gap (measured / predicted): ____

The gap is explained by:  bandwidth not fully used / thermal throttling / swap /
                          other programs / the hot context / not yet known

For a 2 000-token question my first word arrives after ____ seconds.
```

If the gap is within about 20%, your method is calibrated and you can now size a 7B model with
arithmetic. If it is not, the explanation is the most valuable thing in this module, and
[the troubleshooting page](../../references/troubleshooting.md) starts from the same list of causes.

Then do the part that makes the decision real: **put the chosen model in the course's `.env`**, so
every later module uses it, and re-run `bench` to confirm the whole path still behaves.

```dotenv
CHAT_MODEL=qwen3:4b
```

```bash
cd labs/common
# Linux / macOS
cp .env.example .env
```

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

## Break it

**Break it by choosing the largest model that fits.** This is the default failure, and it is
rational: you did the RAM bill, you found a 7B fits with 8 GB spare, and you installed it. The
problem is that "fits" was the wrong filter, and you find out four lessons later when a voice
command takes eight seconds.

**Break it by importing somebody else's target.** A forum post says 13 tok/s is great, so 13 is
the target — on a Framework Ryzen mainboard, with a Ryzen AI laptop's prompt rate, for a job that
actually needs 22. Every number in that sentence came from a different machine, and the decision
that follows from them is fiction. The [benchmark reference](../../references/benchmarks.md) names
the machine for every published figure precisely so that this mistake is avoidable.

**Break it by optimising the wrong end.** A 3B model at Q8_0 instead of Q4_K_M doubles your
bandwidth cost for a quality change most people cannot detect. If you want more quality, buy it
with model size, which is where the step in the curve actually is — and buy it only if your
speed target still passes afterwards.

**Break it with a voice target on a machine that cannot meet it.** Ship a 10 tok/s model as the
brain of a voice assistant with a 3-second stage budget, and every reply is late. Nothing crashes;
the assistant just feels broken in a way people describe as "the AI is slow" rather than "the
budget was wrong". The design fix is intents first with the model as a fallback, and it is what
Module 10 builds by default.

## Fix it

1. **Write the target down before you look at any model.** A number in front of a list of options
   is a filter; a number after is a rationalisation.
2. **Apply memory, then generation, then prompt, in that order.** Out-of-order filtering is how a
   7B ends up on a 16 GB laptop: it was evaluated on speed and assumed to fit.
3. **Take the largest survivor, not the safest.** The safety margin belongs in the headroom budget,
   where you have already reserved it, not in a smaller model you did not need.
4. **Predict, then measure, then write down the gap.** An unexplained gap means your method is
   wrong somewhere, and it will be wrong again on the next machine.
5. **Re-decide when the machine changes.** A second memory module, a 32 GB upgrade, a different
   host in Module 3 — each one changes the filters, and the decision is five minutes of
   arithmetic.

> [!TIP]
> **Do it yourself with llama.cpp.** The decision above is a prediction about a hardware limit, and
> `llama-bench` is the tool that tests the limit directly rather than inferring it from a chat
> session. One sweep gives you the generation throughput for every candidate you are considering:
>
> ```bash
> llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 512 -n 128 -t 8
> ```
>
> The parameters that matter for this decision: `-p 512` and `-n 128` set the two test shapes you
> are deciding between, `-t` fixes the thread count so the comparison is fair, and `-ngl 0` keeps
> it on the CPU. Run it once per candidate with the same flags, put the `tg 128` and `pp 512`
> columns in your worksheet, and the "predicted" column becomes "measured" with a single command.
> `-hf` lets you name any GGUF repository directly, so a candidate that is not in the Ollama
> library can still be evaluated before you commit to it.

> [!NOTE]
> **If you have a GPU.** The filters above are a CPU model, and a GPU changes two of the three.
> Memory stops being the binding constraint as soon as the model fits in VRAM — and starts being a
> different binding constraint, because VRAM is usually much smaller than system RAM, so the
> context length rather than the model size is what will not fit. And bandwidth stops being DDR
> bandwidth, so the efficiency factor is no longer 0.5 and your prediction is no longer the
> arithmetic you did earlier in this module. The decision procedure is unchanged and still the
> right one: measure `llama-bench -ngl 0,20,40,99` to find the largest offload that still improves
> generation, check that the model plus its KV cache fits the card's memory, and then apply the
> same target. The one thing that does not improve is the prompt stage if the model is split across
> the PCIe link, which is worth measuring rather than assuming.

## How do I know it works?

- [ ] Your target is a number, written down, and derived from the job rather than from a
      benchmark.
- [ ] Three candidates went through all three filters, in order, and the worksheet shows the work.
- [ ] You chose the largest model that passed, and you can say which filter would have removed the
      one above it.
- [ ] You have a prediction, a measurement, the ratio between them and a sentence explaining the
      gap.
- [ ] You can state the first-word wait for a 2 000-token question on your own prompt rate, and
      whether that is acceptable for the job.
- [ ] The chosen model is in `.env` as `CHAT_MODEL`, and `bench` still behaves after the change.

## Use it when / avoid it

**Re-run the whole worksheet whenever the machine or the model list changes.** It takes twenty
minutes and it is the difference between choosing and guessing. Module 3's host decision, a RAM
upgrade, and any change of default model all invalidate the previous answer.

**Use the "nothing passes" answer.** A machine that cannot meet a target is information, and the
correct response to it is a different design or a different machine — not a smaller download that
misses the target by less. A voice assistant that answers in eight seconds is not a voice
assistant that is slightly slow; it is a product that does not work.

**Avoid moving the target to fit the model.** That is the failure mode of every "what can I run on
my Pi?" conversation. The target comes from the user's patience, and your job is to meet it or to
say plainly that this machine cannot.

**Avoid carrying this decision forward unexamined.** Module 5 replaces "largest that meets the
target" with "best on your own tasks", using a small evaluation set you build from real questions.
The decision here is about feasibility; that module is about quality, and you need both.

## Reflect

1. What is your target, in tokens per second, and where did that number come from? If you chose
      it yourself rather than taking the course's, what made you choose it?
2. Which filter removed the largest model you wanted, and by how much did it miss?
3. For your worst realistic prompt — the longest one your job will actually send — how long is the
      wait for the first word, and what would you change about the design to shorten it?

## Sources

- [Stratosphere — LLM performance on Raspberry Pi 5, with the memory specification](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html)
- [Geerling — ai-benchmarks on Pi 5, N150 and a Ryzen mainboard](https://github.com/geerlingguy/ai-benchmarks)
- [Benchmark numbers and where they come from — including the latency budget](../../references/benchmarks.md)
- [Home Assistant — the local voice pipeline and its stages](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- [Pinned models and licences](../../references/models.md) — the candidates to filter
- [10 · Choose the host](../module-03/lesson-01.md) — the lesson that changes the answer when the machine does
- [17 · One model per job](../module-05/lesson-01.md) — the module that replaces feasibility with quality
