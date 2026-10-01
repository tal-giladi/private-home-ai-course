---
id: "02.3"
module: 2
minutes: 14
practice_minutes: 30
prerequisites: ["02.2"]
objectives:
  - Measure prompt throughput and generation throughput separately, on your own machine, with
    `homelab.py bench` and with `llama-bench`.
  - Calibrate your own efficiency factor from a measurement, so your predictions stop being guesses.
  - Run a thread sweep and identify where generation stops improving and where prompt processing
    does not.
  - Record peak memory for a loaded model on your own platform, including Windows.
volatility: implementation
sources:
  - title: "llama-bench documentation — usage, thread sweeps and output formats"
    url: https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md
  - title: "Qwen3-4B-GGUF — the official GGUF repository, and the model card's llama.cpp commands"
    url: https://huggingface.co/Qwen/Qwen3-4B-GGUF
  - title: "Stratosphere — LLM performance on Raspberry Pi 5"
    url: https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html
last_verified: "2026-09-30"
---

# 02.3 · Measure prompt speed and generation speed

You have a prediction. Now you find out whether it was any good. Two commands, one for the
course's own quick measurement and one for the reference tool that everything else is calibrated
against, and about half an hour including the thinking. The deliverable is not a number — it is
your own efficiency factor, which turns every future prediction on this machine from an assumption
into arithmetic.

## Why it matters

Prediction and measurement are only useful together, and the interesting part is the **gap**. If
your prediction lands within 20% of the measurement, the model in
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md) is validated for your machine
and you can size a 7B model with confidence. If it is off by a factor of two, something specific is
happening — single-channel memory, a throttling laptop, a page file — and *finding that out* is
worth more than the model you were going to pick.

There is a second reason to measure both numbers. "Speed" is two different things limited by two
different resources, and an average of the two tells you nothing. Generation is bandwidth-bound
and barely cares how many cores you have. Prompt processing is compute-bound and does. A machine
can be excellent at one and poor at the other, and which one you need depends entirely on whether
you are chatting or asking questions over your own files.

## How it works

### What each number means

**Time to first token** is what a user experiences as waiting. It is the sum of two different
costs: loading the model if it is not already resident, and processing the prompt. For a chat
question of twenty tokens, the first term dominates. For a retrieval-augmented question of two
thousand, the second dominates completely.

**Generation throughput** is the steady rate at which the reply appears once it has started. It
does not depend much on how long the prompt was — which is exactly why it is the easier number to
predict and the less interesting one.

Put them together and you get the number that actually matters for a design:

$$\text{reply time} = \text{load time (if cold)} + \frac{\text{prompt tokens}}{\text{prompt tok/s}} + \frac{\text{reply tokens}}{\text{generation tok/s}}$$

### Tool one: `homelab.py bench`

The course's own script. It sends two prompts to the model server you already run — one short, one
deliberately long — with temperature 0 and a 64-token answer cap, and prints a table you can paste
straight into [the measure-yours template](../../templates/measure-yours.md).

```bash
# from the course's lab folder
cd labs/common
python homelab.py bench

# skip the voice section, which you do not need yet
python homelab.py bench --models-only

# measure a specific model rather than the one in .env
python homelab.py bench --model llama3.2:3b
```

The output ends with the two rows that matter. **The values below are invented to show the shape
of the output — they are not a measurement of any machine, yours included:**

```text
  your numbers (copy these into templates/measure-yours.md)
    run              prompt tok    gen tok/s    prompt tok/s    TTFT s
    short prompt             9         21.34              38         0.24
    long prompt            2558         19.80              51        50.16
```

The first row's time-to-first-token includes the model load if the model was not already resident,
which is why the warm-up step in the lab below comes first.

Three honest caveats, all of which the course states rather than hides: the token counts are
approximated from character counts, so treat them as ratios rather than exact figures; the long
prompt is a fixed piece of text, so your prompt rate is measured at one prompt length and not at
several; and **peak resident memory cannot be read from a script on Windows**, where the script
says so and tells you to watch Task Manager instead.

That 50 seconds in the illustration is the point of the whole lesson. Two and a half thousand
prompt tokens, and the wait before the first word is measured in tens of seconds while generation
itself is comfortable. If your long-prompt row looks like that, retrieval over your own files is a
project with a prompt-length budget attached, and you will know that before Module 6 asks you to
build it.

### Tool two: `llama-bench`

The reference measurement harness, and the tool the rest of the published numbers were produced
with. Its virtue is that it reports the two throughputs as separate tests and repeats each one
several times, so you get an average and a spread.

```bash
# the default shape: 512 prompt tokens, 128 generated, 5 repetitions
llama-bench -m models/qwen3-4b-instruct-q4_K_M.gguf

# pull the file straight from the model's official repository instead
llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M

# isolate one test: -p 0 measures generation only, -n 0 measures prompt processing only
llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 0 -n 128
llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 512 -n 0
```

The `test` column tells you which is which: `pp 512` is prompt processing at 512 tokens, `tg 128`
is generation at 128 tokens, and the numbers beside them are tokens per second with a standard
deviation. `-r` sets the number of repetitions, `-t` the thread count, and `-o csv` prints a table
you can paste into a spreadsheet.

The thread sweep is one command, because `llama-bench` accepts a list:

```bash
llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 64 -n 16 -t 1,2,4,8,16 -r 3
```

Five thread counts, both tests, three repetitions each — a few minutes, and it produces the table
that tells you whether your machine behaves like the published one.

> [!NOTE]
> macOS: `llama-bench` builds and runs the same way, and `winget install llama.cpp` / the install
> script on the [model card](https://huggingface.co/Qwen/Qwen3-4B-GGUF) are the documented routes.
> **These steps are not verified by us** — the course has one Windows test machine. On Apple
> Silicon the unified memory changes the arithmetic in Module 2.1 completely, so treat any Mac
> number as its own measurement rather than a confirmation of the rule.

### The thread sweep, and what its shape means

From `llama-bench`'s own documentation, on a 7B Q4_0 model — the machine is not named there, so
read the shape rather than the numbers:

| Threads | Generation (`tg 16`) | Prompt processing (`pp 64`) |
|---|---|---|
| 1 | 4.05 | 6.17 |
| 2 | 7.80 | 12.31 |
| 4 | 12.22 | 23.18 |
| 8 | 16.71 | 32.29 |
| 16 | 15.32 | 33.52 |
| 32 | 16.41 | 59.00 |

Generation improves sharply to four threads, gains a little more to eight, and then stops — that
is the bandwidth ceiling of the lesson before this one. Prompt processing keeps climbing, because
it is compute. If your sweep looks like that, your machine is normal. If generation keeps climbing
to sixteen threads, you have something worth investigating: a very large cache that is absorbing
part of the model, or a memory subsystem better than you assumed.

### One memory module or two: what to expect, and why you do not have to test it

This is the one experiment in the course that requires hardware you may not have, so it is
explained rather than required. If you have ever had both configurations on the same machine, the
prediction is simple and it comes straight from
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md):

| | One DIMM | Two matching DIMMs, paired slots |
|---|---|---|
| Channels | 1 | 2 |
| Peak bandwidth (DDR5-5600) | 44.8 GB/s | 89.6 GB/s |
| Expected generation speed | half | full |
| Expected prompt speed | about unchanged | about unchanged |
| Memory available for everything else | unchanged | unchanged |

The asymmetry is the interesting part: adding a second stick doubles the bytes per second, so
generation — which is bandwidth-bound — roughly doubles. Prompt processing is arithmetic over a
batch, so it barely moves. And the RAM bill is identical, because two 8 GB sticks and one 16 GB
stick are the same amount of memory. If you do have the parts, one `llama-bench` run before and
after is the most convincing five minutes in this course; if you do not, the table above and the
published Pi 5 versus N150 comparison already make the case.

### Peak memory, on each platform

```bash
# Linux and macOS, while the model is loaded
ps -o rss= -C ollama | awk '{printf "ollama: %.2f GB\n", $1/1048576}'
```

```powershell
# Windows PowerShell, while the model is loaded: sort by working set, take the top five
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 5 Name,
  @{n='RAM_GB';e={[math]::Round($_.WorkingSet64/1GB,2)}}
```

Take the difference between the two measurements you make — before loading and while loaded — and
that is your runtime overhead figure, the one item in the RAM bill that only your machine can tell
you.

### Turning the measurement into a constant

The last step, and the one that makes the whole method portable. Rearranging the rule from
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md):

$$e = \frac{\text{measured generation tok/s} \times \text{file size in bytes}}{\text{peak bandwidth in bytes/s}}$$

Fill that in for your machine and you can predict any other model's speed by multiplication, with
no further measuring. Expect a number somewhere between a third and two thirds; a value far below
a third means something is limiting you that bandwidth does not explain, and the sweep above is
where you find it.

## Show me

The two commands, in the order to run them, and what each one produces:

```bash
# 1. the quick course measurement, on the model you already have loaded
cd labs/common
python homelab.py bench --models-only
```

```bash
# 2. the reference measurement, with a thread sweep
llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 64 -n 16 -t 1,2,4,8 -r 3
```

If `llama-bench` is not installed, it is optional: the course's `bench` script is enough to get
the two numbers, and `llama-bench` adds the sweep and the repetition. Get it from the
[llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases) or, on Windows, with
`winget install llama.cpp`.

Then fill in both tables in
[the measure-yours template](../../templates/measure-yours.md) — the generation and prompt speed
table, and the thread sweep table — with the machine name at the top. That table, not this page,
is what you will still care about in a year.

## Try it

Thirty minutes, and the payoff is a prediction method that works on your machine.

1. **Warm the machine first.** Ask one question and throw it away, so the load time is not in your
   measurement.
2. **Run `bench --models-only`** and copy the two rows into the template.
3. **Run the thread sweep** with `-t 1,2,4,8` and copy it into the sweep table.
4. **Measure peak memory** while the model is loaded.
5. **Compute your efficiency factor** and write it down.

```text
Machine: ____________________  CPU: ____________________
RAM: ______ GB, ______ modules at ______ MT/s, channels: 1 / 2

Model: qwen3:4b        File: 2.5 GB        Context: 4096

Measured generation:    ____ tok/s
Measured prompt:        ____ tok/s
Time to first token:    ____ s
Peak process memory:    ____ GB
My efficiency factor:   ____ = (gen tok/s x 2.5 GB) / (peak bandwidth ____ GB/s)

Prediction check, a model I have not measured: llama3.2:3b at 2.0 GB
  predicted = peak bandwidth x my e / 2.0 GB = ____ tok/s
  measured later: ____ tok/s          ratio: ____
```

That last pair is the real test of the method: a prediction for a model you have never run, made
with *your* efficiency factor, checked against a measurement. If the two agree within about 20%,
you can size the rest of the course from arithmetic.

## Break it

**Measure a cold model.** Run `bench` immediately after a restart, with no model loaded. The
first-token time now includes reading 2.5 GB from disk, and the "prompt tok/s" derived from that
first-token time is a mixture of load and prompt processing, so it looks far worse than the real
prompt rate. The generation rate is close to right — the script divides the generated tokens by the
whole request time — but a cold row is a little pessimistic for that reason too. This is the most
common way to get a badly wrong prompt number.

**Measure a busy machine.** Run the benchmark with the browser, a video call and Home Assistant all
going. Now you are measuring your working day rather than your hardware, and the number will be
both slower and unstable between runs.

**Measure on battery power.** A laptop on the battery plan is a different machine: the power
scheme caps the clock, and on some hardware the processor drops to the efficiency cores. Numbers
taken on battery are 20–40% lower and will make a perfectly good machine look broken. Check it
before you conclude anything:

```bash
# Linux
cat /sys/dev/power_supply/AC*/online 2>/dev/null; cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null
```

```powershell
# Windows PowerShell
powercfg /getactivescheme
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Power" -Name ProcessorFrequencyMin
```

**Average the two rates together.** "The model does 30 tokens per second" is meaningless when one
of those numbers is prompt processing and the other is generation. A machine at 400 tok/s prompt
and 6 tok/s generation is a machine that is excellent at your RAG prototype and unpleasant to chat
with, and a single number cannot express that.

**Measure with the model swapping.** If the machine is short of memory, the measurement will still
complete — it will just be measuring a disk. Watch available memory *during* the run, not before
it.

## Fix it

1. **Warm up, then measure.** One throwaway question first, so the load is not in the number.
2. **Close the rest.** Benchmark an idle machine, plugged in, on the performance power plan. Write
   those three conditions at the top of the measure-yours table so the number is interpretable in
   six months.
3. **Report two numbers, always.** Prompt and generation, with the prompt length. A generation
   rate without its prompt length is not a result.
4. **Repeat.** `llama-bench` repeats five times by default for a reason: the spread tells you
   whether a difference between two models is real. Use `-r 3` at minimum when you are comparing.
5. **Do not compare across machines without saying so.** A speed is a property of the model, the
   runtime, the context length and the machine. [The benchmark
   reference](../../references/benchmarks.md) names the machine for every published figure for
   exactly this reason, and your table should do the same.
6. **If the numbers do not match the prediction, do not adjust the prediction.** Find the cause.
   A gap of more than about 1.5× is a finding, and the candidates are short: single-channel
   memory, a throttling or battery-powered machine, a page file, or another process competing for
   bandwidth.

## How do I know it works?

- [ ] Two measured numbers for one model — prompt and generation — with the prompt length and the
      machine name written next to them.
- [ ] A thread sweep with at least four thread counts, showing where generation flattens and where
      prompt processing does not.
- [ ] Your own efficiency factor, computed from your own measurement, written in the template.
- [ ] One prediction for a model you have not measured, made with that factor, and the measured
      value beside it.
- [ ] Peak memory recorded on your platform, taken while the model was loaded.

## Use it when / avoid it

**Measure before choosing, and again after changing anything.** The prediction in
[06 · Memory bandwidth sets your speed](../module-02/lesson-01.md) is cheap; the measurement is the
thing that makes the next decision cheap. A runtime update, a new quantisation, a longer context —
each of them can move a number, and each is worth one line in the table.

**Use `llama-bench` when you want to compare, and `bench` when you want to know how your stack
feels.** The course script measures the real path — a real server, a real streaming response — and
`llama-bench` measures the engine in isolation, with repeats and a controlled prompt. Both are
right; they answer slightly different questions.

**Avoid measuring on someone else's numbers.** The tables in
[the benchmark reference](../../references/benchmarks.md) are there to calibrate your intuition
and to give you a plausible expectation, never to fill a cell in your own table.

**Avoid measuring everything.** Half an hour for the numbers in this lesson is enough. The
discipline that matters is repeating the same measurement on the same machine, not collecting
more of them.

> [!TIP]
> **Do it yourself with llama.cpp.** If you have not installed the reference tool, this is the
> whole of it — no runtime, no server, no convenience layer, just the engine and a timer:
>
> ```bash
> llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 512 -n 128 -t 8
> ```
>
> The parameters worth knowing: `-p` and `-n` set how many tokens each of the two tests processes,
> which is how you control the prompt length that matters for your job; `-t` is the thread count
> for the sweep; and `-ngl` is how many layers to put on a GPU. There is no model server and no
> HTTP involved, so nothing else can influence the result — which is exactly why the published
> numbers in this course were produced with it. From source it is two commands,
> `cmake -B build` and `cmake --build build -j --target llama-bench`.

> [!NOTE]
> **If you have a GPU.** Measure the offload boundary rather than assuming it, because this is the
> one case where a speed difference is not a bandwidth story. `llama-bench` takes `-ngl 99` (all
> layers on the GPU) and `-ngl 0` (pure CPU), so the sweep is one command:
>
> ```bash
> llama-bench -hf Qwen/Qwen3-4B-GGUF:Q4_K_M -p 512 -n 128 -ngl 0,20,40
> ```
>
> Read three things off the result: where generation stops improving, which tells you how many
> layers the card's memory bandwidth can actually feed; what prompt processing does at full
> offload, which is usually the dramatic one; and whether a partial offload is faster than pure
> CPU, which it often is not, because the KV cache then crosses the PCIe link on every token.
> `ollama ps` shows the same thing in one line, in its `PROCESSOR` column. If a GPU is present, run
> this once, write both numbers down, and then choose deliberately instead of by default.

## Reflect

1. What is your efficiency factor, and how far is it from the 0.5 the course starts with? What do
      you think explains the difference?
2. In your thread sweep, where did generation stop improving? Was it the same place as in the
      published sweep, and if not, what differs about your machine?
3. Take the largest model that would fit your RAM budget. What speed does your own arithmetic
      predict for it, and would that be usable for the job you chose in
      [00 · What a private home AI stack is](../module-00/lesson-01.md)?

## Sources

- [llama-bench documentation — usage, the thread sweep, and the output formats](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md)
- [Qwen3-4B-GGUF — the official GGUF repository, and its llama.cpp commands](https://huggingface.co/Qwen/Qwen3-4B-GGUF)
- [llama.cpp releases — prebuilt binaries](https://github.com/ggml-org/llama.cpp/releases)
- [Stratosphere — LLM performance on Raspberry Pi 5](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html)
- [Measure-yours tables — where the numbers go](../../templates/measure-yours.md)
- [Benchmark numbers and where they come from](../../references/benchmarks.md)
