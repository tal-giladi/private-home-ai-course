---
id: "11.2"
module: 11
minutes: 16
practice_minutes: 35
prerequisites: ["11.1", "03.3"]
objectives:
  - >-
    Tell the difference between what an application binds to and what Compose publishes, and explain
    why both have to be right before a service is unreachable from outside.
  - >-
    Run the isolated exposure lab, observe what an unauthenticated model server gives away, and
    repeat the run with the exposure removed to see the same request fail.
  - Explain why port forwarding is never the answer, and what to run instead.
volatility: implementation
sources:
  - title: "Ollama FAQ — the API has no authentication, and how to change the bind address"
    url: https://docs.ollama.com/faq
  - title: "Wiz — CVE-2024-37032 Probllama, a path traversal to remote code execution"
    url: https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032
  - title: "Cyera — CVE-2026-7482 Bleeding Llama, an unauthenticated memory leak"
    url: https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform
  - title: "Docker — published ports and network isolation"
    url: https://docs.docker.com/engine/network/
last_verified: "2026-09-30"
---

# 11.2 · Bind addresses and ports

Reachability is a chain of two links, and the lesson before this one was about the chain. This
lesson is about the last link, the one you can check mechanically instead of from memory — and it
ends with you breaking it on purpose, safely.

> [!CAUTION]
> **This lesson runs a deliberately vulnerable service.** The lab below starts a model server bound
> to `0.0.0.0` on a Docker network that exists only inside your own machine.
>
> - Nothing outside your own computer is contacted. The two lab containers are on a network declared
>   `internal: true`, so they can reach each other and nothing else — not the internet, not your
>   LAN, not any other machine.
> - There is no scanning, no third-party target, no internet search engine, and no port forwarding at
>   any point in this lesson. The "attacker" is an Alpine container on the same isolated network,
>   talking to a service that was created for the purpose.
> - No port of yours is opened, and no router setting is changed. Read [39 · Remote access the safe
>   way](../module-11/lesson-03.md) before you change anything on your router, ever.
> - `exposure-victim` and `exposure-attacker` share the Compose project name with your real stack, so
>   **never run `docker compose down` in this lesson.** Use `stop` and `rm` on the two service names
>   only. A `down` would take your chat interface with it.

## Why it matters

The stack is safe today because of one design decision that is easy to type and hard to see: the
model server has no `ports:` line, and it sits on a network Docker gives no route out. Change either
of those and you have created something that is, in the words of Ollama's own documentation, an API
with no authentication — where anyone who arrives can list, pull and delete models and use your
compute.

That is not a hypothetical shape. Cisco found 1 100+ internet-exposed Ollama servers through Shodan,
with later counts reported around 175 000 and around 300 000. The people who ran them were not
careless in an interesting way; almost all of them had set one environment variable, for a good
reason, usually so that a container in another network could reach the model server.

Two documented vulnerabilities make the consequence concrete rather than theoretical. CVE-2024-37032
("Probllama") was a path traversal that became remote code execution, and was worst exactly where
these guides put Ollama — running as root inside a container, bound to every interface; it was fixed
in 0.1.34. CVE-2026-7482 ("Bleeding Llama") is an unauthenticated memory leak through a malformed
GGUF file, fixed in 0.17.1. Both need a reachable port, and both stop at an unreachable one.

## How it works

### Two switches, not one

This is the part that catches people, so it is worth being precise. A service becomes reachable
from outside its container only when **both** of these are true:

| In the container | In `compose.yaml` | Who can connect |
|---|---|---|
| Binds `127.0.0.1` | no `ports:` line | Nobody outside that container's own loopback |
| Binds `0.0.0.0` | no `ports:` line | Other containers on the same Docker network |
| Binds `0.0.0.0` | `"127.0.0.1:8080:8080"` | This machine only |
| Binds `0.0.0.0` | `"0.0.0.0:8080:8080"`, or just `"8080:8080"` | Every device that can route to this host |
| Binds `0.0.0.0` | published **and** the router forwards it | The internet |

So the bind address is what the process listens on, and the published port is what the host offers
on your behalf. Compose will happily publish a port for a service that is bound to loopback, and the
result is a port that answers with nothing on it — the symptom of a misconfiguration people spend an
afternoon on. The useful habit is to treat the two lines as one decision.

### What the course's stack publishes

| Service | Container port | Published on the host? | Why |
|---|---|---|---|
| `ollama` | 11434 | **No** | Its API has no authentication at all |
| `open-webui` | 8080 | `127.0.0.1:8080`, from `WEBUI_BIND` | The one thing a browser opens, and it has accounts |
| `homeassistant` | 8123 | **No** | Reached through the chat-interface port or a VPN, never directly |
| `qdrant` | 6333 | **No** | The interface talks to it; you never open it in a browser |
| `wyoming-*` | 10200, 10300, 10301 | **No** | The satellite runs on the host and speaks to them by name |

The voice satellite in Module 9 is the one exception, and it is worth naming: the satellite runs
*natively on your host* with the microphone, so it does publish 10200 and 10300/10301 there. Bind
those to `127.0.0.1` or to your VPN address, exactly as you would any other port. Nothing else in
the stack needs a host port at all.

### What `doctor` checks, and why it is the standing test

`python homelab.py doctor` walks the stack's known ports, tries each one on `127.0.0.1`, and then
tries the same port on your machine's routable addresses. Loopback only is reported as *loopback
only*. A port that answers on a routable address is reported as *reachable from your router; this is
the one to fix*, and it is reported as a failure. Run it before and after anything in this module:
it is the one check here that produces a verdict rather than an opinion.

## Show me

The lab's two services, exactly as they are defined in
[`labs/common/compose.yaml`](../../labs/common/compose.yaml) — read that section before you run it,
because everything below depends on those four lines:

```yaml
  exposure-victim:
    image: ollama/ollama:0.35.0
    container_name: homelab-exposure-victim
    restart: "no"
    profiles: ["secure"]
    entrypoint: ["ollama", "serve"]
    environment:
      OLLAMA_HOST: "0.0.0.0"   # the mistake, made on purpose, inside an isolated lab
      OLLAMA_KEEP_ALIVE: "0"
    networks:
      - exposure
    # No volumes and no ports: no models, and nothing published to the host.
    # (the deploy/resources memory limit in the real file is elided here — it does not affect the lab)

  exposure-attacker:
    image: alpine:3.20
    container_name: homelab-exposure-attacker
    restart: "no"
    profiles: ["secure"]
    depends_on:
      - exposure-victim
    networks:
      - exposure
    entrypoint: ["sh", "-c", "sleep 3600"]

  exposure:
    name: homelab-exposure
    internal: true
```

Four properties of that definition, and each one is doing a job:

1. **`internal: true`** gives the network no gateway, so neither container can reach the internet.
2. **No `ports:` on either service** means nothing about this lab is visible on your host, your LAN
   or your router — `doctor` will not even see it.
3. **`restart: "no"`** means a stopped lab stays stopped instead of quietly running overnight.
4. **No volume on the victim** means the lab has no models and cannot touch yours. The model list it
   returns will be empty, and the reason is containment, not a bug in your setup.

> [!NOTE]
> We have not run this lab end to end yet — the course's measurement spike is still to come. What
> follows is the sequence of commands and the shape of what to look for, taken from the Compose
> file and Ollama's documented API. Your exact wording will differ. What matters is the yes or no:
> does the request get answered, or does it fail?

## Try it

1. Bring the lab up, and only the lab:

   ```bash
   docker compose --profile secure up -d exposure-victim exposure-attacker
   ```

2. Confirm the isolation before you do anything else. Both of these should succeed, and the second
   should fail:

   ```bash
   # the network is internal, as the file says
   docker network inspect homelab-exposure --format '{{.Name}} internal={{.Internal}}'

   # a container on it has no route out
   docker compose exec exposure-attacker wget -T 3 -qO- http://example.com
   ```

   If the second one *succeeds*, stop and check your Docker installation before continuing, because
   that is the one condition under which this lab is not what it claims to be.

3. Get into the "other device on your network" and stay there. Alpine has no shell prompt worth
   photographing; use this:

   ```bash
   docker compose exec exposure-attacker sh
   ```

   You are now at `/#`. Everything in the next steps runs in there, and you leave with `exit`.

4. Ask the model server who it is. No credentials, no headers, no API key:

   ```sh
   wget -qO- http://exposure-victim:11434/api/version
   ```

   It answers with its version. That is the whole attack so far: one unauthenticated GET from a
   machine that is not yours.

5. Ask it what it has. This is the inventory step, and it is the one that maps an attacker's
   options:

   ```sh
   wget -qO- http://exposure-victim:11434/api/tags
   wget -qO- http://exposure-victim:11434/api/ps
   ```

   `tags` is the list of models it stores. Yours will come back empty, because the lab's victim has
   no volume and therefore no models. On a real box this is where the attacker learns which models
   you run, and `ps` shows which are loaded right now.

6. Ask the OpenAI-shaped endpoint, because clients do not distinguish it from a hosted one:

   ```sh
   wget -qO- http://exposure-victim:11434/v1/models
   ```

7. Now the two operations that cost you something. These need a JSON body, so write it on the host
   first and copy it in, which avoids every shell's quoting rules:

   ```bash
   # Linux / macOS
   printf '{"name": "qwen3:4b", "stream": false}' > pull.json

   # Windows PowerShell
   '{"name": "qwen3:4b", "stream": false}' | Set-Content -NoNewline pull.json

   # both
   docker cp pull.json homelab-exposure-attacker:/tmp/pull.json
   docker compose exec exposure-attacker sh -c "wget -qO- --header=Content-Type:application/json --post-file=/tmp/pull.json http://exposure-victim:11434/api/pull"
   ```

   On a real exposed server that request downloads a model onto your disk, on your broadband, without
   asking. Here it fails with a name-resolution or connection error, and the error is the lesson:
   **this is what the `internal: true` network is for.** The lab is contained by the same control
   the real stack uses.

   The matching delete needs no download and no model, so it is the sharper demo. The same
   mechanism, with `{"name": "qwen3:4b"}` in the file and `/api/delete` in the URL, is a deletion
   request accepted from any machine that can reach the port.

8. Leave the shell and check that your real stack has not moved:

   ```bash
   python homelab.py doctor
   ```

   No new `0.0.0.0` warnings, because the lab published nothing. That absence is worth noticing: a
   real exposure would not have shown up here either until the router was involved.

## Break it

**Break it the real way, in writing.** The classic sequence is: bind the model server to
`0.0.0.0` because a container needs to reach it, publish the port so the host can reach it, and then
have a router rule or UPnP open the last link. Every one of those steps has a plausible reason. The
result is an unauthenticated API with documented remote-code-execution history, visible to
everyone.

**Break it with a "temporary" bind.** `WEBUI_BIND=0.0.0.0` in `.env` while you test on your phone is
the single most common way this course's stack gets exposed, and it is the one that survives,
because nobody goes back. The `0.0.0.0` in this lab's victim service is the same mistake with the
consequence removed.

**Break it by trusting the network instead of the bind.** A service on an internal Docker network is
unreachable from the internet, and it is still perfectly reachable from every other container you
attach to that network. Isolation limits *where*, not *who*.

## Fix it

The fix is one environment variable, and you can see it working without touching the shared file.
Create an override beside `compose.yaml` — yours, not the course's:

```yaml
# exposure-fixed.yaml
services:
  exposure-victim:
    environment:
      OLLAMA_HOST: "127.0.0.1"
```

Then rebuild just the victim, with the same two containers on the same isolated network:

```bash
docker compose -f compose.yaml -f exposure-fixed.yaml --profile secure up -d --force-recreate exposure-victim
docker compose exec exposure-attacker sh -c "wget -T 3 -qO- http://exposure-victim:11434/api/version"
```

The second command now fails. The service is up, healthy and answering — for itself only. That is
the whole fix: the bind address decides who can connect, and the internal network is what stopped
the internet in the first place.

| Symptom | Cause | Fix |
|---|---|---|
| `connection refused` from a container | Service bound to `127.0.0.1` inside its own container | Bind to `0.0.0.0` in the container, and publish on `127.0.0.1` on the host |
| Port published, nothing answers | Bound to loopback, published anyway | Match the two: `0.0.0.0` in the container or nothing on the host |
| `doctor` reports a port as reachable from your router | Service bound to a routable address | Bind to `127.0.0.1`; for VPN access, bind to the VPN interface address instead |
| A container cannot reach another service | They are on different networks | Attach both to the same network; do not solve it with `0.0.0.0` on the host |
| You cannot pull a model | The network is `internal: true` | Pull from a one-off container on the default bridge, as Module 3 taught |

Tear the lab down without touching your stack:

```bash
docker compose --profile secure stop exposure-victim exposure-attacker
docker compose --profile secure rm -f exposure-victim exposure-attacker
```

## How do I know it works?

- [ ] `docker network inspect homelab-exposure` reports `internal=true`.
- [ ] From inside the attacker container, a request to the internet fails, and a request to
      `exposure-victim:11434` succeeds.
- [ ] `wget -qO- http://exposure-victim:11434/api/tags` returned a JSON document with no
      credentials of any kind in the command.
- [ ] With the override applied, the same request from the same container fails, while
      `docker compose ps` still shows the service running.
- [ ] The lab is stopped and removed with `stop` and `rm`, and `docker compose ps` shows your chat
      interface still running.
- [ ] `python homelab.py doctor` prints no port warning for your real stack.
- [ ] You can state which of the two switches — bind address or published port — is the one that
      made the lab work, and which one is the one your router would have to be trusted with.

## Use it when / avoid it

**Use `127.0.0.1` for everything by default, and widen only with a reason you can write down.** The
widenings this course endorses are two: the chat interface on a VPN interface address, and — if you
move to Home Assistant OS on a second machine — the model server published on one specific LAN
address in [44 · Your always-on home](../module-12/lesson-04.md). Both are deliberate, both are
narrow, and both are reversible.

**Avoid publishing a port you do not have a client for.** A published port exists to serve somebody.
If the only client is another container, the published line is not a convenience, it is an attack
surface with no purpose.

**Avoid `0.0.0.0` as a debugging shortcut.** If a container cannot reach a service, the cause is
almost always that the two are on different networks or the address is wrong — not that the service
needs to listen on every interface. Compose's own service names exist for this.

**Never port-forward anything in this stack.** Not the model server, not Home Assistant, not the chat
interface. Home Assistant's documentation is explicit that simply opening a port is not secure, and
[11.3](../module-11/lesson-03.md) is the lesson about what to do instead.

## Reflect

1. In the table at the top of this lesson, which single cell would you change to make a published
   port harmless — and what would that cost you?
2. The lab's victim has no models, so `api/tags` came back empty. What would the same command have
   told an attacker on a box where you *had* pulled models, and why is that enough to plan an
   outage?
3. Your phone needs the chat interface, and you are not on your own Wi-Fi. What is the smallest
   change to one line in `.env` that makes that work without touching the router?

## Sources

- [Ollama FAQ — the API has no authentication; how to change the host it binds to](https://docs.ollama.com/faq)
- [Wiz — CVE-2024-37032 "Probllama", path traversal to remote code execution, fixed in 0.1.34](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032)
- [Cyera — CVE-2026-7482 "Bleeding Llama", unauthenticated memory leak, fixed in 0.17.1](https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform)
- [Docker — published ports and internal networks](https://docs.docker.com/engine/network/)
- [The shared stack's Compose file](../../labs/common/compose.yaml)
- [Pinned versions](../../references/versions.md)
- [39 · Remote access the safe way](../module-11/lesson-03.md)
