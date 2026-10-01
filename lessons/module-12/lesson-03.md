---
id: "12.3"
module: 12
minutes: 14
practice_minutes: 30
prerequisites: ["04.3", "12.1", "11.3"]
objectives:
  - >-
    Test the claim that nothing leaves your house, instead of asserting it, and say what a passed test
    does and does not prove.
  - Prove that a container on the stack's internal network has no route out, and that the failure is
    the network rather than your internet.
  - Find the things that phone home, and decide for each one whether to disable, block or accept it.
volatility: implementation
sources:
  - title: "Open WebUI documentation — environment variables and feature flags"
    url: https://docs.openwebui.com
  - title: "Docker — internal networks, and why they have no gateway"
    url: https://docs.docker.com/engine/network/
  - title: "Home Assistant — integration alerts and security"
    url: https://alerts.home-assistant.io/
last_verified: "2026-09-30"
---

# 12.3 · Prove there is no cloud

Everything in this course has claimed that your data stays at home. This is the lesson where the
claim becomes a measurement — and where the honest answer might turn out to be "almost, and here is
the exception".

> [!WARNING]
> This lesson changes how your machine reaches the outside world.
>
> - The method the course recommends — the stack's own `internal: true` network — needs no firewall
>   rule and no router change, and it is already in place. You are testing it, not adding it.
> - If you go further and write **host firewall rules** to block outbound traffic, a wrong rule can
>   cut you off from your own machine, including the session you are reading this in. Read the rules
>   back before you apply them, and know how to remove them without the machine being reachable.
> - The bluntest version of this test — switching off your internet at the router — also takes your
>   VPN down with it. That is expected, and it is part of what the test shows.
> - Nothing here forwards a port, and nothing here changes a router's forwarding rules.

## Why it matters

"No cloud" is the promise the whole course rests on, and it is a promise about a machine that runs
for months at a time without you looking at it. Promises about long-running software decay quietly:
a feature gets enabled by default in an update, an integration is added because it was convenient,
a check for updates becomes a check for a licence, and none of it was ever a decision you made.

The stack is unusually well placed here, and it is worth being clear about *why*. The `ai` and
`voice` networks are declared `internal: true`, which means Docker attaches no gateway to them at
all — so the long-running services in your stack already have no route to the internet. They never
had one. A compromised chat interface in this stack has nothing to call home to.

Which means the interesting work in this lesson is not proving the network does what the file says.
It is finding the things that are **not** in that network: the browser, the host, and the
integrations you added to Home Assistant by hand.

## How it works

### Three levels, in increasing order of evidence

| Level | Method | What it proves | What it misses |
|---|---|---|---|
| **1. Inspect** | Read the configuration for outbound settings | That you did not enable anything | That nothing enabled itself |
| **2. Observe** | Browser network tab, service logs, the host's connection table | What actually left, while you were using it | Anything that only happens monthly |
| **3. Enforce** | Cut the route, then use every feature | That the features you rely on do not need it | The features you do not use, which you have not tested |

Level 3 is the capstone's criterion, and it is worth doing exactly once, deliberately, with the list
of features in front of you.

### What "no cloud" has to cover

| Component | What could leave | The course's position |
|---|---|---|
| The model server | Nothing — it serves weights | No route out, by design |
| The chat interface | Auto-titling, tag and follow-up generation, web search, code execution, a page you paste a URL into | All four flags are off in `compose.yaml`; verify, do not assume |
| The browser | Anything the page loads: fonts, analytics, a remote avatar, a CDN-hosted asset | This is the one most people forget, and it is not the stack's to control |
| Home Assistant | Each integration talks to something; some of those somethings are the internet | Write down, per integration, what it talks to |
| The host | Update checks, telemetry, DNS | Deliberate, and worth naming |

The browser row is the one that changes how people read this course. Open WebUI served from
`127.0.0.1` is a page your browser has fetched from your own machine, and everything that page then
loads is a separate outbound request that the stack has no control over. The network tab is where
you see it.

### The test, in the right order

The order matters, because the failure you expect to see is the same one you would see if your
internet were simply down. So run the control first:

```bash
# the control: a container on Docker's default bridge can reach the internet
docker run --rm alpine:3.20 sh -c "wget -T 5 -qO- http://example.com >/dev/null && echo 'HOST: internet reachable' || echo 'HOST: no internet'"

# the test: a container on the stack's internal network cannot
docker run --rm --network homelab-ai alpine:3.20 sh -c "wget -T 5 -qO- http://example.com >/dev/null && echo 'NETWORK: LEAK' || echo 'NETWORK: no route out, as intended'"
```

The first line is a control and the second is the experiment. If the first says no internet, fix
that before reading anything into the second. A test without a control is a feeling.

> [!NOTE]
> The one-off container from Module 3 that pulls models attaches to the default bridge on purpose,
> and it is removed with `--rm` the moment it finishes. After your models are in place, nothing in
> the stack needs the internet — which is what makes the test above possible without unplugging
> anything.

### Cutting the route, once, deliberately

The blunt version, and the one that answers the capstone's question. It touches the router, so read
the caution at the top first.

1. Turn off the router's internet connection, or disconnect its WAN cable — not the Wi-Fi your
   devices are on, the uplink to your provider.
2. Exercise **every** feature you actually use, from the list: chat, a new conversation, a document
   question, a typed Assist command, a spoken command, the voice satellite, the interface's
   settings pages.
3. Write down what broke. The correct answer is "nothing I use".
4. Restore the connection.

The VPN going down at the same time is expected and is itself informative: it confirms that remote
access depends on the tunnel rather than on anything being publicly reachable, which is the property
[11.3](../module-11/lesson-03.md) was for.

## Show me

The three levels applied to one feature, so the shape of the evidence is clear before you go looking
for it. This is the configuration as it stands in the course's Compose file — read it, do not trust
it:

| Feature | Flag in `compose.yaml` | What to look for in the network tab | Verdict to record |
|---|---|---|---|
| Automatic chat titles | `ENABLE_TITLE_GENERATION: "False"` | No extra request when a conversation is created | Off |
| Tag generation | `ENABLE_TAGS_GENERATION: "False"` | No request after a few messages | Off |
| Suggested follow-ups | `ENABLE_AUTOCOMPLETE_GENERATION: "False"` | No request after a reply | Off |
| Web search | `ENABLE_WEB_SEARCH: "False"` | No search-engine request, ever | Off |
| Code execution | `ENABLE_CODE_EXECUTION: "False"` | No sandbox service contacted | Off |
| Anything the browser loads | Not a stack setting | Any request whose host is not `127.0.0.1` or your own address | Yours to fix |

And the honest limit of that table, which matters more than the table: **a passed test covers the
features you exercised.** Turn web search back on six months from now, never use it, and this test
will still pass. That is why the security checklist asks for the list of features rather than a yes
or a no, and why the capstone asks for the test to be run with the features in hand.

## Try it

1. Run the control and the test from "How it works" above, in that order. Write down both lines
   verbatim — they are the first evidence in your notes.

2. Open the chat interface, open the browser's developer tools, and watch every request while you
   use the features you actually rely on:

   | Browser | Where |
   |---|---|
   | Chrome, Edge, Firefox | <kbd>F12</kbd> or <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>I</kbd>, then the **Network** tab |
   | Safari | Developer menu, then **Network** |

   Filter to fetch and document requests, clear the list, and then: start a new conversation, send a
   message, open a second tab and come back. Every request should be to `127.0.0.1` or to your own
   tailnet address. Anything else is something to decide about.

3. Watch the services' own logs while you use them. An outbound attempt that failed leaves a
   hostname and a connection error in the log, which is the most reliable "it tried to phone home"
   evidence you will get:

   ```bash
   docker compose logs --since=5m open-webui homeassistant
   ```

4. Look at the host's live connections while a chat is running. The stack's own traffic should be
   loopback and Docker network addresses, and nothing should be going anywhere else:

   ```bash
   # Linux / macOS
   ss -tpn state established
   ```

   ```powershell
   # Windows PowerShell
   Get-NetTCPConnection -State Established |
     Select-Object LocalPort, RemoteAddress, RemotePort, OwningProcess |
     Sort-Object RemoteAddress
   ```

5. Make an inventory of your Home Assistant integrations, one line each, and name what each one
   talks to. This is the step that finds things, because integrations are added by clicking rather
   than by editing a file. For anything that reaches the internet, decide now: disable it, or accept
   it in writing in the security checklist.

6. Do the cut. Follow the four steps above with your feature list in hand, and write down every
   feature that did not work. If a feature you did not expect fails, that is a genuine finding and it
   belongs in the write-up.

7. Restore the connection, and confirm the stack is fully functional again — the same three-feature
   smoke test as the update routine: one chat message, one typed Assist command, one spoken command.

8. Record the whole thing: the date, the method, the features you exercised, and the failures (if
   any), in [the security checklist](../../templates/security-checklist.md). An unrecorded test
   cannot be distinguished from a claim at capstone time.

## Break it

**Break it by treating a quiet log as a pass.** Logs are truncated, rotated to 10 MB, and only show
what the process tried. A service that phones home once a day, or on a schedule, produces a quiet
log for the whole time you were watching.

**Break it by blocking outbound and only testing the happy path.** If you cut the connection and try
one thing, you have learned almost nothing. The features that phone home are the ones you use
occasionally — web search, a URL you paste, an integration that fetches a forecast.

**Break it by forgetting the browser.** Everything the interface's page loads leaves from your
computer. A remote font, a hosted avatar, a documentation link that the help panel fetches — these
are real requests from a real machine, and they are not in `compose.yaml`.

**Break it by testing before pulling the models.** Obviously the stack needs the internet to
download a model, and obviously it does not need it afterwards. Test in the wrong order and the
failure looks like a broken stack rather than a passing one.

**Break it by assuming a denial proves the reverse.** Blocking traffic and seeing nothing fail
proves the features you used do not need it. It does not prove the app is incapable of sending; it
proves that on this run, with these features, it did not.

## Fix it

| Finding | What it is | What to do |
|---|---|---|
| A request in the network tab to an external host | The page loaded something remote | Find the setting that caused it, or accept it in writing |
| An integration reaching the internet | Somebody added it for convenience | Disable it if you do not need it; write it down if you do |
| A failed outbound call in the logs | A feature tried and was refused | Usually harmless; it is now visible, which is the win |
| The stack cannot pull a new model | The internal network, working as designed | Use the one-off container from Module 3, then remove it |
| A test fails only for an unused feature | You exercised a feature you do not rely on | Turn it off if you do not need it, and note the exception |
| Nothing failed at all | The test passed | Record it, with the feature list, and repeat it after each update |

The general answer for a finding is the same in every row: **turn the feature off, or write down
that you accepted it.** The version to avoid is leaving it on because it was convenient the one time.

## How do I know it works?

- [ ] You can show the control and the test output from the `homelab-ai` network experiment.
- [ ] Every request in the browser's network tab, while you used the features you rely on, went to
      `127.0.0.1` or your own tailnet address.
- [ ] You have a list of your Home Assistant integrations, each with what it talks to.
- [ ] You ran the cut, exercised every feature you rely on, and the only thing that stopped working
      was the VPN.
- [ ] The date, method and feature list are in the security checklist.
- [ ] Every feature you accepted as reaching the internet is written down, with a reason.
- [ ] You can say what this test does not cover, and you have a plan for when to run it again.

## Use it when / avoid it

**Run the full cut after a big change, not on a schedule.** An update, a new integration, a new
app, a browser change — those are the moments when a new outbound path can appear. Monthly, the
cheap version (network tab plus the integration list) is enough.

**Treat a finding as useful.** The point of this lesson is not to pass; it is to find the one thing
you did not know about. A stack where everything passed the first time is a stack where nobody
looked.

**Avoid treating "it works with the internet off" as permanent.** The test describes the stack as it
is today, with the features you used today. That is a real result and it decays, which is why it
goes in the checklist with a date.

**Avoid writing host firewall rules you cannot undo without a keyboard.** If you do add them, write
the removal command down before you add the rule, and test the rule on one service before you apply
it to the machine.

> [!TIP]
> **If you have a GPU.** A GPU changes throughput, not reachability, and nothing in this lesson
> changes. The one thing to re-check is the driver and the container runtime: a GPU passed into a
> container is a capability, and the rule that matters is unchanged — no route out means no route
> out, whatever hardware is doing the arithmetic. The one place a GPU is a genuine risk is a
> separate downloader or manager service on the host, which is another thing listening on the host
> and another row in the inventory.

> [!TIP]
> **Do it yourself with llama.cpp.** `llama-server` is a single binary with no registry, no
> background updater and no configuration service, so it shrinks the inventory rather than growing
> it: `llama-server -m ./model.gguf --host 127.0.0.1 --port 8081 --ctx-size 4096`. Run it on
> loopback and it has no route to anywhere, and the number of things that *can* phone home in your
> stack goes down by one. What you give up is `ollama pull`, and the convenience of a model store —
> which, for the privacy claim, is part of what you were trying to remove.

## Reflect

1. Run the network tab while you use the interface normally. How many requests went somewhere other
   than your own machine, and which setting caused each one?
2. Which of your Home Assistant integrations talks to the internet, and what would you lose by
   turning it off?
3. Name one feature this test did not cover, and say when you will test it.

## Sources

- [Open WebUI documentation — environment variables and feature flags](https://docs.openwebui.com)
- [Docker — internal networks and why they have no gateway](https://docs.docker.com/engine/network/)
- [Home Assistant — integration alerts](https://alerts.home-assistant.io/)
- [The shared stack's Compose file](../../labs/common/compose.yaml)
- [Security checklist](../../templates/security-checklist.md)
- [39 · Remote access the safe way](../module-11/lesson-03.md)
