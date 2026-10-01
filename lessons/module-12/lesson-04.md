---
id: "12.4"
module: 12
minutes: 15
practice_minutes: 30
prerequisites: ["12.2", "07.1", "11.3"]
objectives:
  - >-
    Decide between staying on Home Assistant Container and moving to Home Assistant OS, and say what
    each one costs you in RAM, ports and effort.
  - >-
    Migrate from a Container install to Home Assistant OS through a verified backup, and check what
    actually carried across before you switch over.
  - >-
    Point a separate Home Assistant instance at the model and voice services on the stack host, using
    one narrow published address rather than a general exposure.
volatility: implementation
sources:
  - title: "Home Assistant — installation types, and which one to choose"
    url: https://www.home-assistant.io/installation/
  - title: "Home Assistant OS — common tasks, apps, backups and the command line"
    url: https://www.home-assistant.io/common-tasks/os/
  - title: "Home Assistant — the Ollama conversation agent integration"
    url: https://www.home-assistant.io/integrations/ollama/
  - title: "Wyoming protocol — the services Home Assistant discovers"
    url: https://github.com/rhasspy/wyoming
last_verified: "2026-09-30"
---

# 12.4 · Your always-on home

The last lesson is the one where you decide what "always-on" means for your house. The stack on
your laptop works. The question is whether it should become a box in a cupboard, and if so, what
changes — because the honest answer is that one of the two options costs you a published port, and
that is worth understanding before you buy anything.

> [!WARNING]
> The migration in this lesson destroys data, and one of the steps destroys a disk.
>
> - **Installing Home Assistant OS wipes the drive you install it on.** Check twice which disk is
>   selected, and do not start it on the drive holding anything you have not backed up elsewhere.
> - Do the [backup and restore drill](../module-12/lesson-02.md) *before* the migration, not during
>   it. A migration you have not rehearsed is a coincidence with good intentions.
> - Publishing the model server's port on a LAN address is the one place in this course where you
>   deliberately make something reachable by other machines. It is legitimate, it is narrow, and it
>   is only defensible once your IoT devices are on a separate network.
> - Nothing here forwards a port on your router, and nothing here changes a router's forwarding
>   rules. One router setting is involved — a DHCP reservation for the stack host's address — and
>   that is it.

## Why it matters

A laptop that sleeps is not an always-on home assistant, and a desktop that is off is not one
either. The two realistic answers are the machine you already own — kept awake, with the stack on it
— and a small dedicated box that does nothing but run Home Assistant. They are genuinely different
setups, and the difference is not the software: it is where your RAM goes, who can reach what, and
what happens when Docker has a bad day.

The second reason this lesson exists is that the move is not free in the way people expect. The
model server in this course publishes no port at all, and that is deliberate — its API has no
authentication. A separate machine cannot reach a service that is not published. So moving Home
Assistant somewhere else means publishing that port, on a specific address, and living with it. That
is a real cost of the OS route, and it is why the IoT segmentation from
[11.3](../module-11/lesson-03.md) stops being optional the moment you take it.

## How it works

### Two installs, compared honestly

| | Home Assistant Container (the course default) | Home Assistant OS on a dedicated box |
|---|---|---|
| What it is | One container in the stack you already run | A minimal operating system with Home Assistant, a Supervisor and an app store on it |
| What it needs | Nothing beyond the Docker stack | A machine of its own, or a virtual machine |
| Startup | Starts with the stack, after the model server is healthy | Starts on its own, in seconds, and survives a Docker problem |
| Apps | **None.** There is no Supervisor and no app store | An app store: Samba share, Studio Code Server, File editor, Terminal & SSH, and more |
| Backups | You tar the volume, as in 12.2 | `ha backups new`, `ha backups restore`, optionally to an NFS or CIFS share |
| Updates | Your monthly routine, by hand | The Supervisor updates Home Assistant, itself, the OS and the apps |
| Reaching the model server | By service name on the internal network | **By a published port on a LAN address** |
| RAM | Shares the host's budget with the model server | Needs its own allocation, taken from the machine's total |
| The risk that bites | `docker compose down -v` | The installer wiping the wrong disk |

Home Assistant's own documentation calls the OS the recommended installation type for most users,
and it is a better product: the Supervisor exists, updates are somebody else's problem, and the app
store is a real answer to "how do I edit a YAML file without an SSH client". What the course has
been building is the other option, because it needs no second machine and no second operating
system, and because a container you can read is a container you can reason about.

**Stay on Container** if the machine you have is a machine that is always on, and you want one RAM
budget rather than two. **Move to the OS** if Home Assistant is the thing that must never be down,
or if you want the app store and the automatic backups.

### What the app store actually gives you

The four that this course's workflows would reach for, all installed from **Settings → Apps →
Install app** on an OS install:

| App | What it is for here |
|---|---|
| **File editor** | Edit `configuration.yaml`, automations and custom sentences from a browser |
| **Terminal & SSH** | A web terminal plus the `ha` command line, and SSH for your own tooling |
| **Studio Code Server** | A full editor in the browser, with the `ha` command line in its terminal |
| **Samba share** | Mount Home Assistant's directories from another machine, to copy files in |

Two things to hold onto. First, the Supervisor's backups are *its* format — a Container install
cannot produce one, which is why 12.2 is a different lesson from this one. Second, you can add
third-party app repositories, and Home Assistant's documentation is blunt about it: it cannot
guarantee the quality or security of third-party apps. Every app you install is software you are
responsible for updating, and one of them — cloud backup storage — is exactly the kind of thing
this course is avoiding. Point backups at an NFS or CIFS share you own instead.

### The port you will have to publish, and how narrowly

This is the part to read twice. A separate machine cannot reach a service that publishes nothing.
So for Home Assistant OS to use the model server, the model server needs a port, and the only
defensible shape is one address:

```dotenv
# .env — the stack host's fixed LAN address, from the DHCP reservation in 11.3
STACK_LAN_IP=192.168.1.50
```

```yaml
# ollama-publish.yaml — your override file, beside compose.yaml. The shared file is untouched.
services:
  ollama:
    ports:
      - "${STACK_LAN_IP}:11434:11434"
  wyoming-whisper:
    ports:
      - "${STACK_LAN_IP}:10300:10300"
  wyoming-piper:
    ports:
      - "${STACK_LAN_IP}:10301:10301"
  wyoming-openwakeword:
    ports:
      - "${STACK_LAN_IP}:10200:10200"
```

Read that binding carefully: it is a specific address, not `0.0.0.0`, and not a bare `11434:11434`.
A socket bound to one interface does not appear on any other, so the service answers on the trusted
LAN and not on the guest network, not on the tailnet and not anywhere else.

> [!IMPORTANT]
> `homelab.py doctor` will now report the model server's port as reachable from your network, and it
> will be right to. The tool cannot tell "reachable from my own trusted LAN" apart from "reachable
> from the internet", so when you publish deliberately, **write the exception into the security
> checklist with the address and the reason**, rather than silencing the warning and forgetting you
> published it.

## Show me

The migration, as a sequence with a checkpoint between each pair of steps. The order is the content
of this lesson; the commands are in "Try it".

| Stage | What happens | Checkpoint before moving on |
|---|---|---|
| 0. Rehearse | Complete 12.2 levels 1 and 2 | You have restored the archive into a separate volume and started from it |
| 1. Install | Home Assistant OS on the dedicated box; it wipes the target disk | Onboarding completed, and the old box still running |
| 2. Move the configuration | Copy `/config` from the old volume onto the new install | The new instance lists your automations and exposed entities |
| 3. Re-point | Ollama and Wyoming now addressed by the stack host's LAN address | One chat answer, one typed Assist command, one spoken command |
| 4. Verify, then cut over | Run the smoke test for a week before retiring anything | The security checklist is updated with the new topology |
| 5. Re-measure | Two machines, two memory budgets | Fresh numbers in [measure yours](../../templates/measure-yours.md) |

Stage 2 deserves its own honest note. What usually carries across a Container → OS move is the YAML,
the automations, custom components, the `.storage` directory and the recorder database. What does
not carry is anything Supervisor-shaped — but a Container install has no add-ons, no Supervisor
backups and no app-store certificates, so there is nothing of that kind to lose. **We have not run
this migration on the course's test machine**, so treat the "usually carries" list as the expected
behaviour to verify on one file before you rely on it, not as a guarantee.

## Try it

1. **Decide, and write the decision down.** Container or OS, and one sentence of why. If you are
   staying, this lesson's remaining steps are for later, and the honest thing is to come back after
   the capstone.

2. **Rehearse the backup.** Do 12.2 levels 1 and 2. Do not skip to step 3 because the new machine is
   in front of you and the drill is boring; the drill is the part that works when the new machine is
   already installed and the old one is already gone.

3. **Reserve the stack host's address.** In your router, pin the stack host to
   `192.168.1.50` (or whatever you choose) with a DHCP reservation. Everything in the next steps
   depends on that address being stable, and changing it later means changing three configuration
   files.

4. **Publish the two services, narrowly.** Create the override file above, put `STACK_LAN_IP` in
   `.env`, and apply it:

   ```bash
   docker compose -f compose.yaml -f ollama-publish.yaml up -d
   docker compose ps
   ```

   Confirm from another machine on the trusted LAN that the model server answers, and from a device
   on the guest network that it does not. The second test is the one that matters.

5. **Install Home Assistant OS on the dedicated box**, from the official image, choosing the disk
   deliberately. Read the wipe warning again. Complete onboarding and create the account you will
   actually use, not `admin`/`admin`.

6. **Move the configuration across.** With the old Container stack still running and untouched,
   copy `/config` from the old volume to the new machine. The easiest route is the Samba app on the
   new install, or `docker cp` on the old one:

   ```bash
   docker run --rm -v homelab-ha-config:/src:ro -v $(pwd)/migrate:/dst alpine:3.20 \
     sh -c "cp -a /src/. /dst/ && ls -a /dst"
   ```

   Then copy that folder to the new install, by Samba, by the File editor app, or by any means you
   trust. **Keep the old stack running** until the new one is verified.

7. **Re-point the integrations.** Every URL that said `http://ollama:11434` now says
   `http://192.168.1.50:11434` — that is the Ollama conversation agent's base URL, and anything else
   you configured by service name. For the voice services, the Wyoming integration is pointed at the
   host's address and the three published ports.

8. **Run the smoke test three times:** one chat answer, one typed Assist command, one spoken
   command. If all three work, the topology is right.

9. **Update the security checklist.** New machine, new addresses, one deliberate published port with
   a written reason, and the `doctor` warning you are choosing to accept rather than fix.

10. **Re-measure.** Two machines means two memory budgets and two sets of numbers. Fill in fresh
    figures, because the capstone's sizing and operations criteria are about *your* machine as it
    finally is.

11. **Only then**, retire the old arrangement — and not by deleting it. Stop the services, keep the
    volume, and keep the backup. "Retired" should mean "not running", not "gone".

## Break it

**Break it with `0.0.0.0:11434:11434` in the override file.** It is one character shorter and it
publishes the model server to every interface, including the guest network and the tailnet. The
whole of 11.2 exists to make that specific keystroke feel expensive.

**Break it by installing Home Assistant OS on the wrong disk.** The installer wipes what it is
installed on, and "wrong disk" is a thing that happens to people with two drives. The rehearsal in
step 2 is what makes this recoverable; nothing else is.

**Break it by skipping the backup and starting fresh.** You lose the automations, the custom
sentences, the entity names you trained the voice model on, and the exposed-entity list you spent
Module 10 justifying. None of it is anywhere else.

**Break it by moving the configuration and not the addresses.** `/config` copies cleanly and the
integrations still point at a service name that no longer resolves from the new machine. The
symptom is a Home Assistant that starts and cannot answer, which is the same symptom as a dozen
other things.

**Break it by publishing before segmenting.** A published model server on a flat network is an
unauthenticated API reachable by the television. The order is 11.3 first, this lesson second.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| Home Assistant OS cannot reach the model server | The port is not published, or is bound elsewhere | Publish on `STACK_LAN_IP`; check `docker compose ps` shows the mapping |
| It works from the stack host but not from the new machine | The service is bound to loopback in the container | Bind to `0.0.0.0` inside the container and publish on the LAN address |
| Everything works on the LAN and also from the guest network | You published `0.0.0.0`, or the guest network does not isolate | Publish the specific address; fix or replace the guest network |
| The voice pipeline fails after the move | Wyoming still points at a service name or the old address | Repoint the Wyoming integration at `STACK_LAN_IP` and the three ports |
| `doctor` reports a port warning you expected | It cannot distinguish your LAN from the internet | Record the exception in the checklist with the address and the reason |
| The new box is slow, or Docker is thrashing | Two machines competing for one RAM budget | Re-measure both; lower the limits that 12.1 set |

The general form: **make the new topology explicit, one address at a time, and prove each link
before you retire the one that works.**

## How do I know it works?

- [ ] Your decision between Container and Home Assistant OS is written down, with one sentence of
      reason, and the rest of this lesson is either done or deliberately deferred.
- [ ] The backup and restore drill from [42 · Backups and a restore
      drill](../module-12/lesson-02.md) was completed *before* anything was installed or moved.
- [ ] The stack host has a DHCP reservation, and the published ports use that fixed address rather
      than `0.0.0.0`.
- [ ] A machine on the trusted LAN reaches the model server, and a device on the guest network does
      not — tested, not assumed.
- [ ] One chat answer, one typed Assist command and one spoken command all work from the new
      install.
- [ ] The old stack is still running, or was retired by stopping it rather than deleting it.
- [ ] The security checklist names the new machine, the new addresses, and the one deliberate
      published port with its reason.
- [ ] Fresh idle memory and idle power figures exist for every machine you now run, because two
      machines mean two budgets.

## Use it when / avoid it

**Move to Home Assistant OS when Home Assistant has to be up when the stack is not.** That is the
real argument for it: it starts on its own, it survives Docker, and the Supervisor keeps it
current. A box in a cupboard running one job is a better home for Home Assistant than a laptop that
is also your laptop.

**Stay on Container when RAM is the binding constraint.** One machine with one budget beats two
machines with two, on a 16–32 GB box, and that is the machine most people reading this have.

**Avoid publishing the model server wider than the trusted LAN.** One address, one DHCP reservation,
one written reason. If the second machine is on the guest network, the answer is to move the machine,
not to widen the binding.

**Avoid doing the migration and the move in the same weekend.** Rehearse, migrate, verify, then cut
over — four separate occasions, each of which you can abandon.

> [!NOTE]
> **Going further: Proxmox.** If you have a spare machine, Proxmox is a legitimate answer and this
> course deliberately does not teach it. We are not recommending it here for three reasons, in
> order: it needs a second machine you are currently using for something else; installing it **wipes
> that machine**, so you need somewhere to put what is on it first; and it splits your RAM between
> virtual machines, which is the one resource this whole course has been careful never to assume.
> On a 16–32 GB box, running the stack in a Linux VM *and* Home Assistant in another VM is how a
> working setup becomes a slow one. If you do have a spare machine, the path is Proxmox, a Linux VM
> running this course's Docker stack unchanged, and Home Assistant OS as a second VM. There is no
> lab for it here, and that is a decision about scope rather than a judgment about the tool.

## Reflect

1. Is your machine actually always on — sleep, lid closed, updates, power cuts? What would have to
   change for it to be?
2. You now have to publish one port that was previously unpublished. Write the one sentence that
   justifies it, and decide what has to be true for that sentence to stay true.
3. The OS route costs you RAM and buys you an app store and automatic backups. Which of those two
   matters more to you, and what does that say about the machine you should be running this on?

## Sources

- [Home Assistant — installation types, and which one to choose](https://www.home-assistant.io/installation/)
- [Home Assistant OS — common tasks: apps, backups, storage, the `ha` command line](https://www.home-assistant.io/common-tasks/os/)
- [Home Assistant — the Ollama conversation agent integration](https://www.home-assistant.io/integrations/ollama/)
- [Wyoming protocol — the services Home Assistant discovers](https://github.com/rhasspy/wyoming)
- [The shared stack's Compose file](../../labs/common/compose.yaml)
- [42 · Backups and a restore drill](../module-12/lesson-02.md)
- [39 · Remote access the safe way](../module-11/lesson-03.md)
