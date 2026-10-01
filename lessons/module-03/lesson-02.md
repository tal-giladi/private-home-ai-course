---
id: "03.2"
module: 3
minutes: 15
practice_minutes: 40
prerequisites: ["03.1"]
objectives:
  - Read a compose file and say what each of service, image, ports, volumes, networks and profiles does.
  - Start and stop the course's stack with one command, and explain what `down` keeps and what `down -v` deletes.
  - Explain why this course publishes only one port, and what would change if that were not true.
volatility: implementation
sources:
  - title: "Docker Compose file reference"
    url: https://docs.docker.com/reference/compose-file/
  - title: "Docker Compose profiles"
    url: https://docs.docker.com/compose/how-tos/profiles/
  - title: "Docker Desktop WSL2 backend"
    url: https://docs.docker.com/desktop/features/wsl/
last_verified: "2026-09-30"
---

# 03.2 · Docker Compose on-ramp

From here to the capstone, the stack is one YAML file. This lesson is the on-ramp: enough Compose
to read the file, start it, and understand the three decisions in it that matter for security —
which is why they are introduced now and explained properly in Module 11.

## Why it matters

A home AI stack is genuinely several programs: a model server, a chat interface, a vector store, a
home automation system, and eventually a speech pipeline. Installing those by hand means six
installers, six sets of start-up scripts, and a machine that breaks on reboot. Compose turns all of
it into one file you can read, and one command you can undo.

It also gives this course something valuable: **an internal network**. Docker can attach a network
with no gateway to the outside world, so containers on it can talk to each other and to nothing
else. That is how the model server ends up reachable by Home Assistant and unreachable by every
other device in your house, without binding anything to `0.0.0.0`.

## How it works

### The six keys you will meet

| Key | What it means | Example in this course |
|---|---|---|
| `image` | Which program to run, at which exact version | `ollama/ollama:0.35.0` |
| `ports` | Map a container port to a port on your machine | `"127.0.0.1:8080:8080"` |
| `volumes` | Data that must survive a restart or an upgrade | `ollama-models:/root/.ollama` |
| `networks` | Which internal networks the container joins | `ai`, `voice` |
| `profiles` | Opt-in groups of services, so optional parts only start when asked | `voice`, `secure` |
| `environment` | Configuration passed in as environment variables | `OLLAMA_KEEP_ALIVE: "5m"` |

### Services, containers, images

An **image** is a frozen program with its dependencies. A **container** is a running copy of an
image. A **service** in a compose file is a declaration that says "this image should be running
like this". `docker compose up` reads the file, downloads any missing images, and makes reality
match it. If reality is wrong, `up` fixes it; if the file is wrong, nothing will.

### Ports, and the part people get wrong

`"8080:8080"` maps host port 8080 to container port 8080. The left number is on your machine. The
full form is `"<bind address>:<host port>:<container port>"`, and in this course the bind address is
always explicit:

```yaml
    ports:
      - "127.0.0.1:8080:8080"   # only this computer
      - "0.0.0.0:8080:8080"     # every network interface: the LAN, and the router
```

The second line is the one that appears in blog posts and the one that turns a private stack into a
public one, because the Ollama API has no authentication at all. The course's compose file uses the
first form, and for the model server and Home Assistant uses **no** `ports` line at all — they are
only reachable from other containers. `python homelab.py doctor` fails loudly if it finds a stack
service reachable from another device.

### Volumes

Anything you would be sad to lose goes in a named volume: downloaded models, chat history, Home
Assistant's configuration, the vector index. This is what makes `docker compose down` safe — it
removes the containers and leaves the data. `docker compose down -v` removes the volumes too. That
second command deletes your models, your chat history and your Home Assistant database, and it does
it without asking again.

### Profiles

The stack grows through the course, but you should not be running a speech-to-text engine in
Module 3. Profiles let one file hold optional services that only start when named:

```bash
docker compose up -d                      # the core stack
docker compose --profile voice up -d      # add speech in and out
```

If a service you expected is simply not there, check whether its profile is active. This is the
single most common confusing thing about Compose, and it is not a bug.

### Windows: install Docker Desktop with the WSL2 backend

On Windows 10 (build 19045 or later) and Windows 11, install Docker Desktop and leave the
**Use the WSL2 based engine** option ticked. Two things then catch people out, and both bite later
in the course:

- **WSL2 has its own memory limit**, separate from Windows, and the smaller of the two wins. If your
  model server dies with no useful log line, check `.wslconfig` in your user profile.
- **Files inside the VM's virtual disk are slow.** Keep model files on a named volume or a real
  drive, never in a directory Docker manages for you.

macOS and Linux: install Docker Engine plus the Compose plugin. macOS has a memory limit in Docker
Desktop's settings too, and Apple Silicon images must be arm64 — the course's images are multi-arch.

## Show me

The real file is `labs/common/compose.yaml`, and here is the shape of it before you meet it in
detail:

```yaml
name: private-home-ai

services:
  ollama:
    image: ollama/ollama:0.35.0
    restart: unless-stopped
    environment:
      OLLAMA_KEEP_ALIVE: "5m"
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - ai
    # No "ports:" line on purpose. The API has no authentication, so it must not be
    # reachable from anything except the other containers on this network.

  open-webui:
    image: ghcr.io/open-webui/open-webui:v0.11.4
    profiles: ["core", "rag", "voice", "secure"]
    environment:
      OLLAMA_BASE_URL: "http://ollama:11434"
      WEBUI_AUTH: "True"
    volumes:
      - open-webui-db:/app/backend/data
    networks:
      - ai
    ports:
      - "${WEBUI_BIND:-127.0.0.1}:8080:8080"

networks:
  ai:
    internal: true

volumes:
  ollama-models:
  open-webui-db:
```

Two things to notice. `OLLAMA_BASE_URL` is `http://ollama:11434` — the **service name**, because
inside the network containers find each other by name. And `internal: true` is a single word that
removes the network's route to the internet, which is also where these containers pull models from
on first run. The course handles that with an explicit, one-time pull from the host; the reasoning
is in [12 · The shared stack](lesson-03.md).

## Try it

1. Copy the shared lab code somewhere you will keep it:

   ```bash
   # Windows PowerShell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\homelab" | Out-Null
   Copy-Item -Recurse .\common "$env:USERPROFILE\homelab"
   Set-Location "$env:USERPROFILE\homelab\common"

   # macOS / Linux
   mkdir -p ~/homelab && cp -r ./common ~/homelab/ && cd ~/homelab/common
   ```

2. Create your settings file. This is the file that makes the stack yours, and it is gitignored on
   purpose:

   ```bash
   Copy-Item .env.example .env    # Windows PowerShell
   cp .env.example .env           # macOS / Linux
   ```

3. Read the resolved configuration before you start anything. This is the single most useful habit
   in this lesson:

   ```bash
   docker compose config
   ```

   It prints the file with every variable substituted and every path resolved. If `docker compose
   config` looks wrong, nothing else will work, and it is far faster to find out here.

4. Start the core stack and watch what happens:

   ```bash
   docker compose up -d
   docker compose ps
   docker compose logs --tail=30 ollama
   ```

   The first run downloads about 3.7 GB of images. It takes a few minutes and it is a one-time cost.

5. Confirm the API answers, and confirm it is not reachable from outside:

   ```bash
   curl http://127.0.0.1:11434/api/version
   python homelab.py doctor
   ```

   `doctor` should show the model server on loopback and no `0.0.0.0` warnings. If it warns, stop
   and read [Troubleshooting](../../references/troubleshooting.md) before you go further.

## Break it

Four ways to break a compose file, in increasing order of how much time they cost you.

**Delete the port binding.** Remove the `127.0.0.1:` prefix so it becomes `"8080:8080"`, and restart.
Now the chat interface is reachable from every device on your Wi-Fi. With a weak password, that is
the whole ballgame, and the Ollama API is not even published, so there is nothing to protect it with
— the UI proxies to it. This is the exact configuration a great many guides recommend.

**Use `latest` instead of a pinned tag.** Change the Ollama image to `ollama/ollama:latest`, start
the stack, then pull again a week later and restart. The version you are running is now whatever
someone published most recently, which is a different statement every time.

**Run `docker compose down -v`.** All named volumes are deleted: every model you downloaded, your
chat history, your Home Assistant database. The command is not asking for confirmation, and there
is no recycle bin.

**Set a memory limit lower than the model needs.** Put `OLLAMA_MEMORY_LIMIT=3g` in `.env` with a 4B
model selected and restart. The container is killed mid-request, and the log line is unhelpfully
quiet about why.

## Fix it

| Symptom | Fix |
|---|---|
| A service is missing | Its profile is not active. `docker compose --profile <name> up -d`. |
| Port already allocated | `docker compose down`, or move the host side: `"8081:8080"`. |
| A service is reachable from the LAN | Put the bind address back: `"127.0.0.1:8080:8080"`. |
| The container dies during a request | The memory limit is too low. `docker inspect` shows the exit code; 137 is the OOM killer. |
| Everything is gone after a restart | You ran `down -v`. Recreate with `up -d`; models must be pulled again. |
| Model loads are slow on Windows | The models are inside Docker's virtual disk. Use a named volume, which the course's file already does. |
| `docker compose config` fails | A `.env` value has spaces and no quotes, or a missing tab where a space belongs in YAML. |

The general rule: **`docker compose config` first, `docker compose logs` second, guessing last.**

## How do I know it works?

- [ ] `docker compose config` prints a resolved file with no warnings.
- [ ] `docker compose ps` shows the core services as running, not restarting.
- [ ] `curl http://127.0.0.1:11434/api/version` returns a version.
- [ ] `python homelab.py doctor` shows no `0.0.0.0` warning.
- [ ] `docker compose down` then `docker compose up -d` brings everything back, with your chat
      history still there.

## Use it when / avoid it

**Use Compose from here on.** One file is the difference between a stack you can rebuild and a stack
you have to remember.

**Stay on Compose for a home lab.** The one-host, one-machine assumption is exactly right for this,
and it is why there is no Kubernetes anywhere in this course. If you later outgrow it — a second
always-on host, a shared database, real secrets management — that is a genuine reason to reach for
something heavier, and [44 · Your always-on home](../module-12/lesson-04.md) is where that
conversation belongs.

**Do not use `latest`, and do not use a bind-mounted directory for data you care about.** A bind
mount maps a folder from your host into the container, which is convenient for editing files and
awkward for permissions and for backups. Named volumes survive upgrades, compose file changes and
`down`, and `docker volume inspect` tells you where they live on disk.

**Avoid one compose file per service.** It works until something needs to change in two places, and
then the two files disagree.

> [!TIP]
> **Going further.** `docker compose watch` rebuilds on a change and is useful when you write
> configuration. `docker stats` shows live memory and CPU per container, which is the fastest way to
> find the thing eating your RAM. Neither is needed by this course; both are worth knowing.

## Reflect

1. Your stack has three services. Which of them has state you would be sad to lose, and where does
   that state live? Name the volume for each.
2. `ports: - "8080:8080"` and `ports: - "127.0.0.1:8080:8080"` are one character apart in the file.
   What is the practical difference on your network, and how would you verify it without running
   anything that could be mistaken for an attack?
3. You are about to add a service in Module 7. Which profile will it need, and what happens if you
   forget to pass that profile?

## Sources

- [Docker Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Docker Compose profiles](https://docs.docker.com/compose/how-tos/profiles/)
- [Docker networking](https://docs.docker.com/engine/network/)
- [Docker Desktop WSL2 backend](https://docs.docker.com/desktop/features/wsl/)
- [Pinned versions used by this course](../../references/versions.md)
- [Troubleshooting](../../references/troubleshooting.md)
