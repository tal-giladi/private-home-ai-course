---
id: "04.3"
module: 4
minutes: 11
practice_minutes: 30
prerequisites: ["04.2"]
objectives:
  - Set up a chat interface you can defend: local accounts, no telemetry, no outbound calls.
  - Explain which settings turn a private stack back into one that talks to a third party.
  - Decide what a shared chat interface on your network would need before you publish one.
volatility: implementation
sources:
  - title: "Open WebUI documentation"
    url: https://docs.openwebui.com
  - title: "Open WebUI security advisories"
    url: https://github.com/open-webui/open-webui/security
last_verified: "2026-09-30"
---

# 04.3 · A chat UI you can trust

A chat interface is a web server with your entire conversation history in its database. The
interesting question is not whether it is convenient — it is whether anything it does leaves your
machine. This lesson is the checklist, and it is short, because a UI you have to fight is one you
will switch off.

## Why it matters

Every web interface wants to help you in ways that involve the internet: generate a conversation
title, suggest a follow-up question, embed a YouTube link, search the web, run a snippet of code,
fetch a URL you paste. Each of those is a feature, and each of those is data leaving your house.

None of them is needed for a private stack, which is the useful observation: the private
configuration is not a restricted version of the product, it is the product with a box ticked.

## How it works

There are three categories of thing a chat interface might do that you have not asked for, and they
are worth keeping separate.

| Category | Example | What leaves |
|---|---|---|
| **A call you triggered** | You ask a question, the model answers | Nothing — the model is local |
| **A call the UI makes for convenience** | Auto-titling chats, suggested follow-ups, web search | Your prompt text, to a third party |
| **A call the UI makes about you** | Update checks, crash reports, error telemetry | Your version, your IP, sometimes your prompt |

The course's compose file turns off the whole middle row and most of the third:

```yaml
      OLLAMA_BASE_URL: "http://ollama:11434"
      WEBUI_AUTH: "True"
      ENABLE_TAGS_GENERATION: "False"
      ENABLE_TITLE_GENERATION: "False"
      ENABLE_AUTOCOMPLETE_GENERATION: "False"
      ENABLE_WEB_SEARCH: "False"
      ENABLE_CODE_EXECUTION: "False"
```

Note what is *not* there: no API key, no provider, no account. That is the strongest possible
setting, because there is nothing configured to leak to.

### Accounts

`WEBUI_AUTH: "True"` means the first person to open the interface creates the admin account, and
there is no access without an account afterwards. On a port bound to `127.0.0.1` that is a
household-level precaution rather than a serious control; on a published port it is the only thing
between your chat history and a stranger.

**Sign-up** is a separate setting and is worth turning off. With sign-up on, anyone who reaches the
port can create an account, and "anyone" on a home network includes the guest Wi-Fi.

### Sharing a chat interface on your network

This is the decision Module 11 exists to make properly, but the UI side of it is worth stating
now. If you publish it on the LAN:

- authentication must be on, with a real password in a password manager;
- sign-up should be off, or restricted to named accounts;
- it will show up in your router's device list and be reachable by anything on that network,
  including a compromised smart device;
- every request goes through your model server, so the interface is a *proxy* to it. A
  vulnerability in the interface is a vulnerability in your stack.

## Show me

The settings a private local chat interface should have, and what each one stops:

| Setting | Value here | What turning it off prevents |
|---|---|---|
| `WEBUI_AUTH` | `True` | Anonymous access to your conversations |
| Sign-up | Off | Anyone on the network creating an account |
| `ENABLE_WEB_SEARCH` | `False` | Sending your prompt to a search provider |
| `ENABLE_CODE_EXECUTION` | `False` | Running code on the host or in a remote sandbox |
| `ENABLE_TITLE_GENERATION` | `False` | A model call per conversation, purely cosmetic |
| `ENABLE_AUTOCOMPLETE_GENERATION` | `False` | A model call as you type |
| `ENABLE_TAGS_GENERATION` | `False` | A model call to label your chats |
| Provider configuration | None | Nothing to send anything to |
| `WEBUI_BIND` in `.env` | `127.0.0.1` | Reachability from the rest of your network |

Every one of those is a checkbox, and all of them default to a state chosen to make the product
pleasant. That is not a criticism — it is why the defaults need reading once, deliberately, and
why [43 · Prove there is no cloud](../module-12/lesson-03.md) exists later to check the result
rather than trust it.

## Try it

1. Open the interface and create the admin account with a password from a password manager.

2. Go to the settings and check, one at a time, that each row of the table above is as stated. The
   exact names move between versions; the behaviour does not. If a setting is not where you expect,
   search the interface's settings for the behaviour rather than the label.

3. Turn off sign-up for everyone except the admin, in the authentication settings. If your version
   does not offer per-user sign-up control, disable sign-up entirely and create named accounts.

4. Find where a URL gets fetched. Paste a web address into a chat with a model and ask it to
   summarise the page. If the interface silently fetched it, the page loader is enabled and your
   prompt content has left the machine. Turn that off.

5. Check the browser side, which is the half people forget. Open the developer tools' network tab,
   reload the page, and look at the hosts being contacted. A private instance should talk to
   `127.0.0.1:8080` and to nothing else. This is a two-minute check and it is the single most
   convincing evidence you can produce.

6. Check the model side, which is the other half:

   ```bash
   # Windows PowerShell
   docker compose logs --tail=100 open-webui | Select-String -Pattern "http|fetch|request to"

   # macOS / Linux
   docker compose logs --tail=100 open-webui | grep -iE "http|fetch|request"
   ```

   Entries pointing at hosts other than `ollama` are the ones to explain away.

7. Write down three accounts: who can reach this interface, what they can see, and what they can
   spend. If the answer to the first is "anyone on my Wi-Fi", that is a fact to record now and
   revisit in Module 11.

## Break it

**Break privacy with a convenience setting.** Turn `ENABLE_WEB_SEARCH` back on and configure a
search provider with a key, then ask a question about something private. The prompt content goes
to that provider. Nothing warns you; the answers simply arrive.

**Break access with sign-up.** Leave sign-up open, publish on the LAN, and hand the address to
someone. They can create an account and read your model list, your knowledge bases, and — depending
on the version — your conversations. This is a real class of problem, not a hypothetical: Open WebUI
has had advisories covering account takeover and stored cross-site scripting, both of which assume
an authenticated user.

**Break the port.** `WEBUI_BIND=0.0.0.0`, `docker compose up -d`, then `python homelab.py doctor`.
The tool fails on the published port. That is the loop working: change, check, understand.

**Break it the boring way.** Model a 7B, ask a long question, and conclude the model is broken
because the answer is a minute away. It is not broken. Watch the first-token time separately from
the per-token rate with the commands in [08 · Measure prompt speed and generation
speed](../module-02/lesson-03.md), and the confusion disappears.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Prompts feel slower after an update | A new feature made a model call per message | Turn the relevant toggle off in settings |
| The interface is slow on the first message | The model is loading from disk | Normal; `keep-alive` controls how often |
| Anyone on the network can reach it | `WEBUI_BIND` is not `127.0.0.1` | Put it back, or read Module 11 before widening it |
| A pasted URL came back summarised | The page loader is on | Turn it off; it is a fetch, and a fetch leaves |
| You cannot find a setting | Labels change between versions | Search for the behaviour, not the label |
| The interface is using a lot of RAM | Long chats, many models, or a reranker | Prune chats; check the admin panel's model list |

## How do I know it works?

- [ ] Authentication is on, and the admin password is in a password manager, not in your head.
- [ ] Sign-up is off or restricted to named accounts.
- [ ] The browser's network tab shows only `127.0.0.1:8080`.
- [ ] Web search, code execution, and the cosmetic model calls are all off.
- [ ] `python homelab.py doctor` shows no `0.0.0.0` warning.
- [ ] You have written down who can reach the interface and what they can see.

## Use it when / avoid it

**Use a local interface** for anything you would not paste into a website. That is the whole test,
and it covers almost everything worth using a model for.

**Treat the interface as part of your attack surface.** It proxies to the model server, holds your
conversations, and renders whatever a model produces in your browser. That last one is why versions
matter here more than for most home services: keep it updated, from the
[update routine](../../templates/update-routine.md), and read the advisories when you do.

**Do not publish it on the LAN because it is convenient.** If you want it on your phone, Module 11
has the right way, and it is not a port forward.

**Do not paste a URL into a chat unless you intend the page to be fetched.** That is a small,
surprising leak, and it is the one that catches experienced people.

> [!TIP]
> **Do it yourself with llama.cpp.** `llama-server` serves a minimal built-in web UI at its own
> port, with nothing in it that phones home, because there is very little in it at all:
>
> ```bash
> llama-server -m qwen3-4b-instruct-q4_K_M.gguf --host 127.0.0.1 --port 8081 -c 4096
> ```
>
> It has no chat history, no accounts, no features to disable — which makes it the most private
> interface available and the least convenient one. Useful for a quick test, and worth knowing
> exists precisely so "turn everything off" has an extreme setting.

## Reflect

1. Name three things your interface does that a model server does not, and say which of them can
   send data off your machine.
2. If you publish the interface on your LAN, what is the single change that most reduces the risk,
   and what does it cost you?
3. Which browser tab check would you run to convince somebody else that your stack is private, and
   what would make that check fail?

## Sources

- [Open WebUI documentation](https://docs.openwebui.com)
- [Open WebUI security advisories](https://github.com/open-webui/open-webui/security)
- [Pinned versions](../../references/versions.md)
- [Security checklist](../../templates/security-checklist.md)
- [43 · Prove there is no cloud](../module-12/lesson-03.md)
