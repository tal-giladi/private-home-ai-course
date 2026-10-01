---
id: "07.1"
module: 7
minutes: 13
practice_minutes: 40
prerequisites: ["03.3"]
objectives:
  - Start Home Assistant in the Compose stack and complete onboarding without buying any hardware.
  - >-
    Load the course's demo entities so the stack has lights, sensors and a heater to control.
  - Explain why this course uses HA Container rather than HA OS, and when that choice changes.
volatility: implementation
sources:
  - title: "Home Assistant installation — Docker Compose"
    url: https://www.home-assistant.io/installation/linux#docker-compose
  - title: "Home Assistant documentation — installation"
    url: https://www.home-assistant.io/docs/
last_verified: "2026-09-30"
---

# 07.1 · Home Assistant Container in the stack

Home Assistant is the reason this course is about a home lab rather than a chat window. It is also
the largest single dependency in the stack and the one most people get wrong on the first try, so
this lesson is deliberately about getting it running with nothing but Docker and a demo light.

## Why it matters

Home Assistant gives you three things a language model cannot:

- **State.** It knows that the kitchen light is off right now, and it knows whether that is because
  nobody is home or because the switch is broken.
- **An action vocabulary.** Every device exposes a small set of well-defined operations. A model
  does not need to invent them; it chooses between them.
- **A history.** Everything that happened, which is what makes "the hall light has been on since
  19:00" a question with an answer.

Putting the model *into* that system rather than beside it is what turns a chatbot into an
assistant. This module builds the system; Module 10 adds the model.

## How it works

### Container, not OS

Home Assistant ships in two shapes that matter here:

| | Home Assistant Container | Home Assistant OS |
|---|---|---|
| What it is | The application, in a Docker container | An operating system image with the application |
| Add-ons | **No** — you run them yourself in Compose | Yes, one-click installs |
| Hardware support | Whatever your machine already has | Needs a dedicated boot medium |
| Fits this course | **Yes** — starts with the stack, any OS with Docker | Not yet; it is lesson 12.4 |

The add-on store is the real difference. Under HA OS you get Whisper and Piper as add-ons. Under
Container you run them yourself — which is exactly what the `voice` profile in
`labs/common/compose.yaml` does, and what Modules 8 and 9 build on. It is more work and it is more
understandable, which is the trade this course makes deliberately.

### Demo entities, so no hardware is needed

The stack ships a file of template entities in `labs/common/samples/en/homeassistant/`: three
template lights, two temperature sensors, a humidity sensor, a thermostat-style heater, a door
sensor, a lock that deliberately refuses to unlock, two appliance-state selectors and a shopping
list. They are all simulated, all of them real to Home Assistant, and all of them free.

This matters more than it sounds. It means the whole voice path in Modules 8 to 10 can be built and
measured without owning a single smart bulb, and it means a failure is a software failure.

### Where the configuration lives

Two places, and they behave differently:

- **`/config/demo/`** — read-only, mounted from the repository, holds the demo entities and custom
  sentences. It is versioned, so it survives and you can restore it.
- **`/config/.storage/`** — Home Assistant's own state: your account, automations you create in the
  UI, the recorder database. It is a Docker volume, and it is what Module 12's backup lesson is
  about.

Confusing the two is the most common early mistake, and it is worth ten minutes to know which is
which before you have anything of your own in there.

## Show me

The service in the course's compose file:

```yaml
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:2026.9.4
    container_name: homelab-homeassistant
    restart: unless-stopped
    profiles: ["core", "rag", "voice", "secure"]
    environment:
      TZ: "${TZ:-UTC}"
    volumes:
      - homeassistant-config:/config
      - ./samples/en/homeassistant:/config/demo:ro
    networks:
      - ai
      - voice
    depends_on:
      ollama:
        condition: service_healthy
```

Four decisions in it. The image is pinned to an exact version, because Home Assistant ships a
release a month and a surprise upgrade during a course is a bad afternoon. The `TZ` comes from your
`.env`, because timestamps are unreadable in UTC when you are trying to find out when the hall
light came on. The demo folder is read-only, so Home Assistant cannot rewrite the version-controlled
file. And it joins two networks — `ai` so it can reach the model server, `voice` so it can reach
speech services later — neither of which is published to your machine.

## Try it

1. Start the stack with Home Assistant included. It is in the `core` profile, so there is nothing
   extra to pass:

   ```bash
   docker compose up -d
   docker compose ps
   ```

   The first start unpacks a large image and takes a minute or two. Home Assistant is not a web
   service until it says it is; check with `docker compose logs -f homeassistant` and wait for the
   banner.

2. **Make Home Assistant reachable.** It publishes no host port — that is the design — so from your
   browser there is nothing at `127.0.0.1:8123` yet. For the duration of this module, add the
   binding deliberately:

   > [!CAUTION]
   > The next step publishes Home Assistant on your local network. Read
   > [38 · Bind addresses and ports](../module-11/lesson-02.md) before you decide whether to keep
   > it. Home Assistant's own documentation is explicit that simply opening a port is not secure
   > access. Bind it to `127.0.0.1` unless you understand why you would not.

   ```yaml
     ports:
       - "127.0.0.1:8123:8123"
   ```

   ```bash
   docker compose up -d homeassistant
   ```

   Open <http://127.0.0.1:8123>.

3. Complete onboarding. Create the owner account with a password from a password manager — this
   account is not created before anyone else can claim it, so do it now rather than "later". Set
   the time zone to match your `TZ` in `.env`.

4. Load the demo entities. In the Home Assistant UI: **Settings → Automations & scenes → Scenes →
   …**, or use the file you mounted. The cleanest path for a container install is a small
   `include` in your configuration, which you can add from the file manager:

   ```yaml
   # configuration.yaml, in the container
   default_config:

   !include demo/demo-entities.yaml
   ```

   Then restart Home Assistant from **Settings → System → Restart**.

5. Confirm the entities exist before you try to control any:

   ```bash
   docker compose exec homeassistant python3 -m homeassistant --script check_config -c /config
   ```

   Or, faster, look at the entity list in the UI and find "Kitchen light", "Hall heater" and
   "Washing machine state". If they are not there, the include is wrong or the file is not where the
   mount says it is.

6. Check where it is listening, from your own point of view:

   ```bash
   # Windows PowerShell
   Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq 8123 |
     Select-Object LocalAddress, LocalPort

   # macOS / Linux
   ss -tlnp | grep 8123
   ```

   `127.0.0.1` and nothing else. Then `python homelab.py doctor`, which agrees.

## Break it

**Break it with a bad include.** Reference a file that is not mounted, and restart. Home Assistant
refuses to start and says so in the logs — which is the good version of this failure, and worth
seeing once. Check `docker compose logs homeassistant | tail -30`.

**Break it with a wrong time zone.** Set `TZ: "UTC"` while you are in a different one. Every
timestamp is right and useless, and the symptom appears much later when you try to answer "when did
the heater come on last night".

**Break it with no free port.** Something else on your machine holds 8123. Change the host side to
`8124:8123` and note that the left-hand number is the only one you control.

**Break it by publishing on `0.0.0.0`.** Change the binding, restart, and run
`python homelab.py doctor`. The tool fails on that line, which is the entire point of having it. Put
it back.

**Break it by deleting the config volume.** `docker compose down -v` removes `/config`: your
account, your automations, your history. This is the failure Module 12 spends a lesson preventing,
and it is much cheaper to experience it now with no state worth losing than later with three months
of it.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Nothing at `127.0.0.1:8123` | No `ports:` entry — by design | Add `"127.0.0.1:8123:8123"` |
| Container restarts repeatedly | Configuration error | `docker compose logs homeassistant` and read the last 30 lines |
| Demo entities missing | `include` line missing or wrong path | Check the mount, then `check_config` |
| "Address already in use" | Another process holds 8123 | `"8124:8123"`, or stop the other process |
| Timestamps are in UTC | `TZ` not set in `.env` | Set it and recreate the container |
| Everything disappeared | `down -v` deleted the config volume | Recreate and re-onboard; this is why Module 12 comes before the capstone |
| Cannot reach the model server | Home Assistant is not on the `ai` network | Check `docker compose ps` shows both networks |

## How do I know it works?

- [ ] `docker compose ps` shows Home Assistant running and healthy.
- [ ] You can open the UI at <http://127.0.0.1:8123> and the owner account exists.
- [ ] The demo entities appear: at least one light, one temperature sensor, one heater.
- [ ] `python homelab.py doctor` shows 8123 bound to loopback and no `0.0.0.0` warning.
- [ ] You can say, out loud, which directory holds configuration you edited and which holds state
      you would miss.

## Use it when / avoid it

**Use HA Container** for this course and for a home lab you run on a machine that already boots.
It composes, it versions, and it does not need a second machine.

**Move to HA OS** in lesson 12.4 if you want the add-on store and a dedicated always-on box. That is
a real upgrade in convenience and a real change in architecture, and it is the right time to make it
once the stack is understood.

**Do not publish the port to your LAN** to make it convenient. If you want it on your phone, Module
11 has the right way, and it is a VPN.

**Do not put real devices and demo devices in the same breath when testing.** Demo entities are
meant to be safe to poke; once a lock or a heater is real, a misfiring tool call has a consequence.

> [!TIP]
> **Do it yourself, if you want to see the boundary.** Home Assistant's container can reach anything
> on `host.docker.internal`. Point a temporary `rest` command at your host's IP and you have
> confirmed the boundary exists. It also demonstrates why that is a one-way street: containers reach
> out, and nothing on the host can reach in without a published port.

## Reflect

1. Which of your two configuration locations holds the demo entities, and which would you back up
   tonight if you had something of your own in there?
2. The container publishes no port, yet you just opened it in a browser. What exactly changed, and
   which of the course's later lessons is about undoing that safely?
3. Why does this course run speech services in Compose instead of installing them as Home Assistant
   add-ons, and what do you gain and lose by that?

## Sources

- [Home Assistant installation — Docker Compose](https://www.home-assistant.io/installation/linux#docker-compose)
- [Home Assistant documentation](https://www.home-assistant.io/docs/)
- [Home Assistant remote access — why a port is not it](https://www.home-assistant.io/docs/configuration/remote/)
- [Pinned versions](../../references/versions.md)
- [Troubleshooting](../../references/troubleshooting.md)
- [12.4 · Your always-on home](../module-12/lesson-04.md)