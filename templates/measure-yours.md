# Measure-yours tables

One table per job. Fill them in on your own machine; the "cited range" column is what other people
found on *their* hardware, and your job is to see whether you are near it or an outlier.

**Machine:** ____________________________________
**CPU:** ____________________________________
**RAM (total, speed, how many sticks):** ____________________________________
**Storage:** ____________________________________
**Tier (from `homelab.py doctor`):** ____

## Generation and prompt speed (Module 2)

One row per model you actually plan to use. `homelab.py bench` prints these columns.

| Model tag | Parameters | File size (GB) | Predicted gen (tok/s) | Measured gen (tok/s) | Predicted prompt (tok/s) | Measured prompt (tok/s) | Peak RAM (GB) |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

**Prediction rule you used:** tokens/s ≈ usable memory bandwidth ÷ file size in bytes, times an
efficiency factor you chose. What factor did you pick, and why?

**Biggest gap between prediction and measurement:** ____________________________________
**What you think explains it:** bandwidth not fully used / thermal throttling / swap / other
programs / something else: ____________________

## Thread sweep (Module 2, optional)

| Threads | Prompt tok/s | Generation tok/s |
|---|---|---|
| 2 | | |
| 4 | | |
| 8 | | |
| All physical cores | | |

**Where generation stopped improving:** ______ threads
**Where prompt processing stopped improving:** ______ threads

## RAM bill (Module 2)

| Item | Size on your machine | How you got the number |
|---|---|---|
| Model weights on disk | | `ls -lh` / File Explorer |
| Model weights in RAM (after load) | | `homelab.py bench` peak |
| KV cache at your context length | | `bench` output |
| Ollama / llama-server overhead | | |
| Open WebUI | | |
| Home Assistant | | |
| Vector store + embeddings | | |
| Whisper / speech-to-text | | |
| Piper / text-to-speech | | |
| Operating system | | |
| Browser | | |
| **Total** | | |
| **Free RAM left** | | |

**Headroom at 8 GB free or more:** yes / no
**What you would drop first if the answer is no:** ____________________

## Per-job model decision (Module 5)

| Job | Model chosen | Why this one | Tokens/s on my box | Score on my eval set |
|---|---|---|---|---|
| Chat | | | | |
| Tool calling | | | | |
| Summarising | | | | |
| Embeddings | | | | |

**Total RAM with all of them loaded at once:** ______ GB
**What happens when chat and voice ask at the same time:** ____________________

## Voice stage timings (Module 8)

Measured with `homelab.py bench --voice` on the three sample commands, then again on your own voice.

| Stage | Sample commands (s) | Your voice (s) | Budget (s) | Within budget? |
|---|---|---|---|---|
| End-of-speech detection | | | 0.3–0.5 | |
| Speech-to-text | | | 1.0 | |
| Built-in intent match | | | 0.1 | |
| LLM with tools (1–3B) | | | 3.0 | |
| Text-to-speech to first audio | | | 0.5 | |
| **End of speech → first audio, intents** | | | **2.0** | |
| **End of speech → first audio, LLM** | | | **5.0** | |

**Where your time actually goes:** ____________________
**What you would change:** ____________________

## Command misfire rate (Module 10)

Thirty commands from `labs/common/samples/en/commands/`, all spoken, all scored.

| Run | Model / mode | Correct | Wrong action | Refused to act | Asked for help |
|---|---|---|---|---|---|
| 1 | Intents only | /30 | /30 | /30 | /30 |
| 2 | LLM with tools | /30 | /30 | /30 | /30 |
| 3 | Intents first, LLM fallback | /30 | /30 | /30 | /30 |

**Misfire rate (wrong action ÷ 30):** intents ____ % · LLM ____ % · hybrid ____ %
**Which commands did the LLM get wrong that intents did not:** ____________________
**Which entities did you decide not to expose, and why:** ____________________
