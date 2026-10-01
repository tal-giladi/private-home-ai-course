---
id: "04.1"
module: 4
minutes: 14
practice_minutes: 40
prerequisites: ["03.3"]
objectives:
  - Call a local model over HTTP with `curl` and read the streaming response.
  - Explain what "OpenAI-compatible" means, and which parts of the API actually match.
  - Write a twenty-line script that talks to your own model, with no cloud key and no account.
volatility: implementation
sources:
  - title: "Ollama API documentation"
    url: https://docs.ollama.com/api
  - title: "Ollama FAQ — host, context size and keep-alive"
    url: https://docs.ollama.com/faq
last_verified: "2026-09-30"
---

# 04.1 · Talk to your model over HTTP

The chat interface is one client. Home Assistant will be another. Your own scripts will be a third.
All of them need the same thing: a URL, a model name, and a way to send a message and read a reply.
That is the whole API, and you can drive it from a command line before you ever write code for it.

## Why it matters

Two reasons, and the second is the important one.

The first is control. Every setting you make in a web interface is a setting you made through that
interface. Once you can send a request yourself, you can see exactly which fields exist, which ones
your model actually respects, and what a bad one looks like.

The second is portability. The reason local model runtimes expose an endpoint shaped like OpenAI's is
so that the enormous number of existing clients — scripts, libraries, agent frameworks, Home
Assistant's own integration — work against a model on your desk without being rewritten. Learn the
shape once and every one of them is available to you, for free, with no key.

## How it works

There are two APIs on the same port, and they are not the same shape.

**The native API.** Ollama's own endpoints: `/api/generate`, `/api/chat`, `/api/embed`,
`/api/tags`. Rich, stable, and Ollama-specific. Use these when you are writing code that only ever
talks to Ollama.

**The OpenAI-compatible API.** `/v1/chat/completions`, `/v1/embeddings`, `/v1/models`. Deliberately
shaped like the hosted service, so existing clients work unchanged. Use this one when you want an
existing tool to work.

| | Native `/api/chat` | Compatible `/v1/chat/completions` |
|---|---|---|
| Message shape | `messages: [{role, content}]` | same |
| Streaming | `stream: true`, one JSON object per line | same, plus `data:` prefixes and a terminator |
| Token counts in the final object | `prompt_eval_count`, `eval_count` | `usage` with the OpenAI field names |
| Extra options | Many, nested under `options` | Fewer; unsupported ones are ignored |
| Who uses it | Your own code | Everyone else's code |

A request looks like this:

```json
{
  "model": "qwen3:4b",
  "messages": [
    { "role": "system", "content": "Answer in one sentence." },
    { "role": "user", "content": "Why is my local model slow?" }
  ],
  "stream": true,
  "options": { "temperature": 0.2, "num_ctx": 4096 }
}
```

The three fields that matter most:

- **`stream: true`.** The reply comes back token by token. This is not a nicety — it is the
  difference between an interface that feels responsive and one that sits blank for eight seconds
  and then dumps a paragraph.
- **`options.temperature`.** Low is deterministic and repetitive; high is varied and occasionally
  wrong. The default of 0.8 is a reasonable middle, and 0 is what you want when you are measuring.
- **`options.num_ctx`.** The context window *for this request*. It is the single setting most worth
  understanding, because it is a memory setting as much as a length setting — see
  [05 · Settings that change the answer](../module-01/lesson-03.md).

> [!NOTE]
> `llama-server` from llama.cpp exposes the same OpenAI-compatible API, and so do several other
> runtimes. That is what makes a swap in Module 5 a one-line change rather than a project.

## Show me

The real thing, on your machine. The model server in the Compose stack is **not** published to a
host port — that is the design from [12 · The shared stack](../module-03/lesson-03.md). So `curl`
from your shell cannot reach it, and the lesson has to start by fixing that without undoing the
security property.

The clean way: ask the network from inside it.

```bash
# Windows PowerShell
docker compose exec ollama ollama list

# macOS / Linux — the same
docker compose exec ollama ollama list
```

For HTTP calls from your shell, use a throwaway client container on the same network:

```bash
# Windows PowerShell, macOS and Linux
docker run --rm --network homelab-ai curlimages/curl:8.11.1 \
  http://ollama:11434/api/version
```

`curlimages/curl` is a tiny image containing only `curl`, which makes it a clean way to talk to
services on an internal network without publishing anything. It is the tool this course uses
throughout, and it is worth remembering as a pattern: **test from inside, do not open a port to
test.**

Alternatively, if you kept the native Ollama from Module 1 running on the host, `curl` works
directly against `127.0.0.1:11434`. Both are legitimate; the stack version is the one the rest of
the course uses.

## Try it

1. Ask what is available:

   ```bash
   docker run --rm --network homelab-ai curlimages/curl:8.11.1 http://ollama:11434/api/tags
   ```

2. One non-streaming reply, so you can see the whole shape at once:

   ```bash
   docker run --rm --network homelab-ai curlimages/curl:8.11.1 -s http://ollama:11434/api/chat \
     -d '{"model":"qwen3:4b","messages":[{"role":"user","content":"Say hello in five words."}],"stream":false}'
   ```

3. The same thing, streaming, which is what you want in practice:

   ```bash
   docker run --rm --network homelab-ai curlimages/curl:8.11.1 -N http://ollama:11434/api/chat \
     -d '{"model":"qwen3:4b","messages":[{"role":"user","content":"Count slowly from 1 to 10."}],"stream":true}'
   ```

   The text arrives word by word. That is the model generating, and it is the same mechanism the
   chat interface uses to make a 4B model feel less slow than it is.

4. The OpenAI-compatible endpoint, with a request that only differs in the URL:

   ```bash
   docker run --rm --network homelab-ai curlimages/curl:8.11.1 -N \
     http://ollama:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"qwen3:4b","messages":[{"role":"user","content":"What is 17 * 23?"}],"stream":true}'
   ```

   No API key, no account, no billing. If a client asks for a key, give it any non-empty string —
   the key is not checked, and that is also why this port must never leave your network.

5. Now write the twenty-line script. Save it as `chat.py` in your lab folder:

   ```python
   """Minimal client for a local model. No dependencies, no key, no cloud."""
   import json, sys, urllib.request

   BASE = sys.argv[1] if len(sys.argv) > 1 else "http://ollama:11434"
   MODEL = sys.argv[2] if len(sys.argv) > 2 else "qwen3:4b"
   PROMPT = sys.argv[3] if len(sys.argv) > 3 else "Explain memory bandwidth in one sentence."

   body = json.dumps(
       {"model": MODEL, "messages": [{"role": "user", "content": PROMPT}], "stream": True}
   ).encode()
   req = urllib.request.Request(
       f"{BASE}/api/chat", data=body, headers={"Content-Type": "application/json"}
   )
   with urllib.request.urlopen(req) as r:
       for line in r:
           if not line.strip():
               continue
           chunk = json.loads(line)
           print(chunk.get("message", {}).get("content", ""), end="", flush=True)
   print()
   ```

   Run it against the host's native Ollama if you have one:

   ```bash
   # Windows
   py -3 chat.py
   # macOS / Linux
   python3 chat.py
   ```

   Or inside the network:

   ```bash
   docker run --rm --network homelab-ai -v "$PWD:/w" -w /w python:3.12-slim \
     python chat.py http://ollama:11434 qwen3:4b "What is a KV cache?"
   ```

6. Change one thing and run it again: `temperature` 0.0, then 1.3. Then `num_ctx` 2048, then
   32768, watching how long the first word takes. Write both pairs in your
   [measure-yours table](../../templates/measure-yours.md).

## Break it

**Break the model name.** Send `"model":"qwen3:99b"`. The native API returns a clear error naming
the model. The OpenAI-compatible endpoint does not always — some clients silently substitute a
default model and you get a confident answer to a different question. This is the compatibility tax
and it is worth knowing about before you trust a tool you did not write.

**Break the JSON.** Leave a trailing comma. Watch where the error lands: the runtime rejects it
with a parse error and a byte offset, which is a much better experience than a silent failure.

**Break the network.** Call `http://127.0.0.1:11434` from inside a container on the internal
network. You get a connection error, because that container's loopback is its own. This is the
exact mistake [Troubleshooting](../../references/troubleshooting.md) lists first, and it is why
`OLLAMA_BASE_URL` is a service name.

**Break the port.** Publish the model server to your LAN so `curl` works from your shell, then run
`python homelab.py doctor`. The warning appears. That is the right time to read
[38 · Bind addresses and ports](../module-11/lesson-02.md), not after something has happened.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Connection refused from a container | Using `127.0.0.1` | Use the service name: `http://ollama:11434` |
| "model not found" | Not pulled into the stack's volume | The one-off `docker run -v` pull from lesson 03.3 |
| A client demands an API key | It is written for a hosted provider | Any non-empty string; nothing is checked |
| The answer ignores your system prompt | Wrong endpoint or role format | Check the `role` names and that you are on the native API |
| Everything is slow to first token | Long context, or the model is loading | Check `num_ctx`; the first call after a restart always loads |
| Works from the host, not from a container | Container has no route to the host's loopback | Put the service in the Compose network, or use a client container |

## How do I know it works?

- [ ] `chat.py` prints a streamed reply on your machine with no API key and no account.
- [ ] You have seen the difference between a native and an OpenAI-compatible response body.
- [ ] You can say which of the two you would use for a new tool, and why.
- [ ] `python homelab.py doctor` still shows no `0.0.0.0` warning.

## Use it when / avoid it

**Use the native API** for your own code. It reports token counts, exposes more options, and is the
one with fewer surprises.

**Use the OpenAI-compatible API** to get an existing tool to work — an editor plugin, a notebook
library, a framework — with no code changes. Expect it to be a subset, and check what it ignored.

**Avoid running two model servers on the same port.** They will not share; the second fails to bind
and you spend twenty minutes looking for a configuration problem.

**Do not put an API key in your `.env` for a local model.** There is nothing to authenticate, so a
key is theatre. If a tool insists on one, that is information about the tool.

> [!TIP]
> **Do it yourself with llama.cpp.** Every command in this lesson has a `llama-server` equivalent
> that exposes the same OpenAI-compatible API with more parameters to play with:
>
> ```bash
> llama-server -m qwen3-4b-instruct-q4_K_M.gguf --host 127.0.0.1 --port 8081 \
>   -c 4096 -t 8 --parallel 1
> ```
>
> The three parameters worth turning: `-c` (context, same memory story as `num_ctx`), `-t`
> (threads, which mostly affects prompt processing), and `--parallel` (how many requests at once,
> where 1 is almost always right on a CPU). Run it on a different port from the stack so both can
> exist, and compare.

## Reflect

1. You want to use an existing Python library that only knows how to talk to OpenAI. Which endpoint
   do you point it at, what do you put in the key field, and what could silently go wrong?
2. The native API reports `prompt_eval_count` and `eval_count`. What could you compute from those
   that you cannot compute from a streamed reply?
3. This lesson used a throwaway client container instead of publishing the model server. Write down
   one more task where that pattern would work, and one where it would not.

## Sources

- [Ollama API documentation](https://docs.ollama.com/api)
- [Ollama FAQ — host, context size and keep-alive](https://docs.ollama.com/faq)
- [llama.cpp — `llama-server`](https://github.com/ggml-org/llama.cpp)
- [Pinned versions](../../references/versions.md)
- [Troubleshooting](../../references/troubleshooting.md)
