---
id: "12.2"
module: 12
minutes: 13
practice_minutes: 35
prerequisites: ["03.3", "12.1"]
objectives:
  - >-
    Separate what must be backed up from what is re-downloadable, and say why models are the largest
    thing you own and the worst thing to back up.
  - Take a verified backup of the state that cannot be regenerated, using a portable command.
  - >-
    Complete a restore into a separate volume and bring the stack up from it, which is the only
    evidence that a backup exists.
volatility: implementation
sources:
  - title: "Home Assistant — backups, and the automatic backup process"
    url: https://www.home-assistant.io/common-tasks/general/#backups
  - title: "Docker — volumes, and how to move data in and out of them"
    url: https://docs.docker.com/engine/storage/volumes/
  - title: "Docker Compose file reference — the volumes a service declares"
    url: https://docs.docker.com/reference/compose-file/services/#volumes
last_verified: "2026-09-30"
---

# 12.2 · Backups and a restore drill

A backup you have never restored is a hypothesis. This lesson is short and slightly boring on
purpose, and its success criterion is not "I ran the command" — it is "I brought a stack back up
from a file, and the stack knew my automations".

> [!WARNING]
> This lesson handles your data and your `.env`, and the last step in it is deliberately
> destructive.
>
> - `.env` holds the numbers for your machine, not passwords. Passwords live in the web interfaces'
>   own settings and in a password manager. **Never commit `.env`**, and never paste a real
>   password into a file, a lesson or a chat message.
> - Take the backup, **verify the archive is readable**, and only then run the destructive drill at
>   the end. The order is the whole lesson.
> - The drill writes into a separate, clearly named volume. Your real one is not touched until the
>   last step, which is the step you only run when the verified backup already exists.
> - Do not run `docker compose down -v` at any point in this lesson. It deletes volumes, not
>   containers, and it does not ask.

## Why it matters

Everything in this stack is recoverable except one category, and that category is small: your Home
Assistant automations, your chat history, the folders you chose to index, the settings you changed
in a web interface at 11 p.m. Everything else — models, Whisper weights, Piper voices, the container
images themselves — is re-downloadable, and the course deliberately keeps it that way.

That asymmetry is the design. A model is large, it is public, and it is addressed by a tag that
resolves. Your automations are small, private, and exist nowhere else. Backing up the first is
expensive and buys nothing; backing up the second is cheap and is the only thing standing between a
mistake and starting again from nothing.

The second reason this lesson exists is boring and decisive: **you will not know whether a backup
works until you have used it.** A tar command that has never been extracted is a belief.

One asymmetry worth knowing before you start: **Home Assistant Container has no Supervisor**, so
there is no backup button to press and nothing in the interface that knows what a backup is. The
volume *is* the backup unit, and taking one is a job you schedule. Home Assistant OS, which
[44 · Your always-on home](./lesson-04.md) covers, has a Supervisor that does it for you — with the
trade-off that its backups are its own format, and not something a Container install can produce.

## How it works

### What to back up, and what not to

| Thing | Back it up? | Why |
|---|---|---|
| `homelab-ha-config` | **Yes** | Automations, entities, custom sentences, the recorder database. Exists nowhere else |
| `homelab-open-webui-db` | **Yes, if you care about the history** | Accounts, chats, settings. Rebuildable, but the history is yours |
| `homelab-qdrant-data` | **Nightly at most** | An index of files you still have. Rebuild it if the embedding model ever changes |
| `compose.yaml` and any override files | **Yes** | The thing that rebuilds the stack |
| `.env` | **Yes, into a password manager** | Your numbers and choices. Gitignored, and it should stay that way |
| `homelab-ollama-models` | **No** | Re-downloadable by tag, and the largest thing you own |
| `homelab-whisper-models`, `homelab-piper-voices` | **No** | Same argument, smaller |
| Container images | **No** | `docker compose pull` fetches them from a pinned tag |

A note on why models are the wrong thing to back up, because it is counter-intuitive: they are
*re-downloadable*, and a backup is a promise about future availability. A tag that resolves today
may not resolve in five years; a copy on your own disk will. The course's default models are all
public and widely mirrored, so re-downloading is a reasonable bet. If you ever add a model from a
source that might disappear, that one model becomes the exception — and it should be written down as
such rather than discovered during an outage.

### One detail that will bite you: copy a database while nothing is writing to it

The chat interface stores its history in a database inside a volume. Tarring that volume while the
service is running produces an archive that may be internally inconsistent — the file exists, the
size looks right, and the extraction is a corrupt database. The fix is not clever tooling; it is
stopping the service first.

```bash
docker compose stop open-webui
# ... take the archive ...
docker compose start open-webui
```

Home Assistant writes a recorder database on the same principle. If you are taking a copy while it
is running, stop it.

### The drill, in three levels

| Level | What it proves | Destructive? |
|---|---|---|
| 1. List the archive | The backup was written and is readable | No |
| 2. Restore into a new volume and start the stack from it | The archive is complete and the stack boots from it | No |
| 3. Destroy the original volume and restore into it | The whole path works, including the real volume name | **Yes** |

Level 2 is the one to do every month. Level 3 is the capstone-grade proof, and it is only safe
because level 1 has already run.

## Show me

The backup command, in full, and what each part is for. It works on every platform because the work
happens inside a throwaway container rather than in your shell:

```bash
# Linux / macOS
docker run --rm \
  -v homelab-ha-config:/src:ro \
  -v $(pwd)/backup:/backup \
  alpine:3.20 \
  sh -c "tar czf /backup/ha-config.tar.gz -C /src . && ls -l /backup"
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path backup | Out-Null
docker run --rm `
  -v homelab-ha-config:/src:ro `
  -v "$(pwd)/backup":/backup `
  alpine:3.20 `
  sh -c "tar czf /backup/ha-config.tar.gz -C /src . && ls -l /backup"
```

| Part | What it does | Why it is there |
|---|---|---|
| `-v homelab-ha-config:/src:ro` | Mounts the volume read-only inside the container | A backup tool that can write to the source is a second way to lose it |
| `-v $(pwd)/backup:/backup` | Points the container at a folder on your disk | The archive must end up somewhere that is not a Docker volume |
| `alpine:3.20` | A small image with `tar` in it | The same command on every platform, with nothing installed |
| `tar czf ... -C /src .` | Compresses the volume's contents into one file | One file is something you can copy, check and restore |
| `&& ls -l /backup` | Shows the size immediately | A zero-byte archive is a failed backup that looks like a successful one |

> [!NOTE]
> We have not run a restore drill on the course's test machine yet — the measurement spike is still
> ahead of us. What this lesson gives you is the command, the order of operations, and the checks
> that make the result trustworthy. Running it is the part we cannot do for you.

## Try it

1. Create the backup folder, and put today's date in the archive name yourself:

   ```powershell
   # Windows PowerShell
   New-Item -ItemType Directory -Force -Path backup | Out-Null
   ```

   ```bash
   # Linux / macOS
   mkdir -p backup
   ```

2. Stop the two services that write databases, take the archives, and start them again:

   ```bash
   docker compose stop open-webui homeassistant

   docker run --rm -v homelab-ha-config:/src:ro -v $(pwd)/backup:/backup alpine:3.20 \
     sh -c "tar czf /backup/ha-config.tar.gz -C /src ."

   docker run --rm -v homelab-open-webui-db:/src:ro -v $(pwd)/backup:/backup alpine:3.20 \
     sh -c "tar czf /backup/open-webui-db.tar.gz -C /src ."

   docker compose start open-webui homeassistant
   ```

   If you built a vector index, add `homelab-qdrant-data` the same way. Name each file with today's
   date rather than overwriting the previous one, and keep a few generations.

   The `docker run` lines are identical on all three platforms — only the line-continuation
   character changes (a backslash in PowerShell, written as a backtick). If your shell is fighting
   you, put the whole command on one line.

3. **Level 1 — prove the archive is readable.** This step is the whole point, and it takes twenty
   seconds:

   ```bash
   docker run --rm -v $(pwd)/backup:/backup:ro alpine:3.20 \
     sh -c "tar tzf /backup/ha-config.tar.gz | head -40; echo '---'; tar tzf /backup/ha-config.tar.gz | wc -l"
   ```

   You should see `configuration.yaml`, a `.storage` directory, and a file count in the hundreds or
   more. A `Unexpected EOF` or a zero count means the backup failed — go back rather than onwards.

4. Copy `compose.yaml`, any override files, and `.env` into your password manager as a secure note.
   Keep `compose.yaml` in version control, where it belongs. Keep `.env` out of it, where it does
   not.

5. **Level 2 — restore into a separate volume.** Create a small override file of your own, beside
   `compose.yaml`:

   ```yaml
   # ha-restore.yaml
   services:
   homeassistant:
     volumes:
       - restore-ha:/config
   volumes:
     restore-ha:
       name: homelab-ha-config-restore
   ```

6. Fill that new volume from the archive, and start Home Assistant from it:

   ```bash
   docker volume create homelab-ha-config-restore
   docker run --rm -v homelab-ha-config-restore:/dst -v $(pwd)/backup:/backup:ro alpine:3.20 \
     sh -c "tar xzf /backup/ha-config.tar.gz -C /dst && ls -a /dst"
   docker compose -f compose.yaml -f ha-restore.yaml up -d homeassistant
   ```

7. Open the interface and check three specific things: your account still exists, one automation you
   wrote is still listed, and the entities you exposed are still exposed. Those three answers are
   the drill's result. A service that starts is not evidence; a service that starts *with your
   configuration* is.

8. Put it back:

   ```bash
   docker compose -f compose.yaml -f ha-restore.yaml stop homeassistant
   docker compose -f compose.yaml -f ha-restore.yaml rm -f homeassistant
   docker volume rm homelab-ha-config-restore
   docker compose up -d homeassistant
   ```

9. **Level 3 — the destructive version, only once you have done levels 1 and 2 cleanly.** Stop the
   service, remove the real volume, restore into the real volume, and start:

   ```bash
   docker compose stop homeassistant
   docker volume rm homelab-ha-config
   docker volume create homelab-ha-config
   docker run --rm -v homelab-ha-config:/dst -v $(pwd)/backup:/backup:ro alpine:3.20 \
     sh -c "tar xzf /backup/ha-config.tar.gz -C /dst"
   docker compose up -d homeassistant
   ```

   This is the capstone's "a completed restore drill", and it is the only version that proves the
   whole path. Do it on a day when you have time to notice that something was not in the backup.

10. Write the date and the result into [the security
    checklist](../../templates/security-checklist.md) and into the log table in
    [the update routine](../../templates/update-routine.md). A restore you cannot evidence did not
    happen.

## Break it

**Break it by backing up models.** The obvious, expensive, useless thing. Your backup is now bigger
than your disk's free space, the oldest archive is the only one that fits, and the thing you actually
needed — your automations — is in the copy you deleted to make room.

**Break it by tarring a live database.** The archive is created, it has a plausible size, and it is
internally inconsistent. This is the failure that teaches people that backups are not a thing you
can verify by looking at the file.

**Break it by backing up `.env` into a git repository.** It is gitignored, and that is the only
thing standing between a routine and a credential leak. The file holds no passwords by design, which
is exactly why it is safe to lose and exactly why people stop thinking before putting it somewhere
that syncs.

**Break it by never restoring.** A backup that has never been extracted may be empty, may be
missing the directory you assumed, may have been taken while the service was down. The failure
surfaces at the worst possible moment, which is the moment you need it.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| The archive is tiny, or listing shows almost nothing | Wrong volume name, or the service was not writing there | `docker volume ls` and check the name against `compose.yaml` |
| `tar xzf` reports unexpected EOF | Backup was interrupted, or the disk filled | Re-take it, and check `docker system df` for what filled the disk |
| The restored Home Assistant has no account | The database was copied while it was being written | Stop the service before archiving, every time |
| The restored stack starts but has no automations | The wrong volume was mounted in the override | Compare the mount targets; `/config` is the one |
| The restore is fine but the UI is not | The interface's own database was not restored | Back up `homelab-open-webui-db` as its own archive |
| The backup never gets taken | It is on the update routine with no date | Put it in a calendar, monthly, next to the version bump |

The general form: **back up the small private things, stop the writer first, verify by listing, and
prove it once by restoring.**

## How do I know it works?

- [ ] You have archives for `homelab-ha-config` and `homelab-open-webui-db`, named with dates.
- [ ] You can list the contents of an archive and see `configuration.yaml` in it.
- [ ] `compose.yaml`, your override files and `.env` are stored somewhere that is not a public
      repository, and `.env` is in your password manager.
- [ ] No archive contains a model file, and you could re-download every model you have in an
      afternoon.
- [ ] You have restored into a **separate** volume and started the stack from it, and you checked
      for your account, one automation and the exposed entities.
- [ ] The date of that restore is written in the security checklist.
- [ ] The backup is a line in a monthly routine with a date in a calendar, not a one-off you
      remember doing.

## Use it when / avoid it

**Back up on a schedule, keep a few generations, and delete them on purpose.** Three dated archives
of a few hundred megabytes cost nothing; a single undated one tells you nothing about when it was
taken.

**Stop writers before archiving anything with a database in it.** It is a ten-second pause and it is
the difference between an archive and a hope.

**Avoid backing up what a tag can restore.** The instinct to keep everything is what turns a backup
routine into the reason your disk is full. Models, images and voice weights are the exception to
"back up the small private things", and the exception is a decision to write down rather than a
default to apply.

**Do the destructive drill once, properly, before the capstone.** It is the only thing standing
between "I have a backup" and "I have restored a backup", and the gap between those two sentences is
where a bad week turns into a bad month.

## Reflect

1. Rank the five things in the table by how much you would miss them, and compare it with their size
   on disk. Does the ranking invert?
2. How long would it take you to re-download every model you have? If the answer is an afternoon,
   what is your archive actually for?
3. What is in your Home Assistant configuration that would be genuinely painful to rewrite — and is
   it in an archive you have listed, or only in one you have taken?

## Sources

- [Home Assistant — backups, and what the Supervisor does differently](https://www.home-assistant.io/docs/backup/)
- [Docker — volumes, and how to move data in and out of them](https://docs.docker.com/engine/storage/volumes/)
- [Update routine — the monthly backup list](../../templates/update-routine.md)
- [Security checklist](../../templates/security-checklist.md)
- [The shared lab files](../../labs/common/)
- [44 · Your always-on home](../module-12/lesson-04.md)
