---
id: "11.4"
module: 11
minutes: 14
practice_minutes: 30
prerequisites: ["11.3", "05.3"]
objectives:
  - >-
    Explain why an unpinned image tag is a security decision, and keep every service on an exact
    version.
  - Check the advisory list for each service in the stack and decide whether an entry applies to you.
  - >-
    Apply a four-question test to a new model file or image before you install it, and follow a
    written monthly update routine.
volatility: implementation
sources:
  - title: "Wiz — CVE-2024-37032 Probllama, a path traversal to remote code execution"
    url: https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032
  - title: "Cyera — CVE-2026-7482 Bleeding Llama, an unauthenticated memory leak"
    url: https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform
  - title: "SentinelOne vulnerability database — CVE-2025-64496"
    url: https://www.sentinelone.com/vulnerability-database/cve-2025-64496/
  - title: "ReversingLabs — malicious models found on a public model hub"
    url: https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face
  - title: "CISA known exploited vulnerabilities catalog"
    url: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
last_verified: "2026-09-30"
---

# 11.4 · Updates, CVEs and model supply chain

Half an hour a month is the whole commitment. The point is not that you patch everything — it is
that when a local model server turns out to have a remote-code-execution bug, you find out from an
advisory list rather than from an intruder.

## Why it matters

Two things change under you in a home lab, and neither announces itself. Software changes because
a container image tag is a name that means whatever it means *today*, and model files change because
a tag in a model registry is a name somebody chose. The first is a supply-chain decision you make
every time you write `docker compose up -d`; the second is a decision you made when you chose a
model.

Both are why this course pins every image to an exact tag. `latest` is banned here, and the reason
is not tidiness. An unpinned tag means you chose "whatever is published when I next start the
stack" — which on a Tuesday evening gives you a version you have never read the release notes of, in
a stack that is meant to be always-on, with state you care about. It is also how you end up running
a version with a known vulnerability without ever having chosen to.

The rest of this module is about the two questions that follow: how do you find out a new one
exists, and how do you tell whether it applies to *your* stack rather than to the internet in
general.

## How it works

### The four advisories that shaped this course

All four are real, all four are linked at the bottom of this lesson, and all four are already fixed
in the versions this course pins. They are here because they define the shapes you will meet again.

| Advisory | Shape | Fixed in | This course runs | Applicable? |
|---|---|---|---|---|
| **CVE-2024-37032** "Probllama" | Path traversal escalating to remote code execution; worst where the server runs as root in a container on `0.0.0.0` | Ollama 0.1.34 | `0.35.0` | No — fixed |
| **CVE-2026-7482** "Bleeding Llama" | Unauthenticated memory leak through a malformed GGUF file | Ollama 0.17.1 | `0.35.0` | No — fixed |
| **CVE-2025-64496** | Account takeover escalating to code execution | Open WebUI 0.6.35 | `v0.11.4` | No — fixed |
| **CVE-2025-46719** | Stored cross-site scripting | Open WebUI 0.6.6 | `v0.11.4` | No — fixed |

Read the third and fourth rows next to the second and notice something: two of these are in the
chat interface, which is the only web-facing service in the stack. Exposure and vulnerability are
different axes, and a service with a CVE is not automatically an urgent one.

### The test that turns an advisory into a decision

Version comparison alone is not a triage method — it will make you update things that could not
exploit you and ignore things that could. Four questions, in order:

1. **Is the component running at all?** An advisory against a vector store you skipped removes
   itself.
2. **Is the fixed version older than yours?** If your tag is above the fix, it is done. This is what
   makes pinning worth the annoyance: the question is answerable without reading a single line of
   the advisory.
3. **Could the advisory's precondition describe your deployment?** "Worst in Docker, running as root,
   bound to `0.0.0.0`" is three separate facts about *your* setup, not about the bug. This is the
   question people skip, and it is the one that most changes the answer.
4. **Who could reach it?** Unreachable from every network you do not control turns most advisories
   into a line in this month's log. Reachable on your LAN by a device with no updates turns the same
   advisory into today's work.

> [!IMPORTANT]
> Reachability decides urgency. It never decides whether to update. A model server with no
> published port and a stale version is a slow problem; a model server with a published port and a
> stale version is an emergency; and the thing that turns the second into the first is a line you
> wrote months ago, which is what the rest of this module is for.

### Where to look, service by service

| Service | Where its advisories live | What you are watching for |
|---|---|---|
| Ollama | The project's security advisories page on GitHub | Unauthenticated endpoints, path traversal, model-file parsers |
| Open WebUI | The project's security advisories page on GitHub | Account takeover, code execution, stored XSS |
| Home Assistant | The core repository's security advisories page | Anything reachable without a login |
| Wyoming voice services | The project's own repository and release notes | Newer than the tag you pinned |
| Everything | The CISA known exploited vulnerabilities catalog | Whether it is being exploited in the wild right now |

The four URLs are in [the update routine](../../templates/update-routine.md), pre-written, so the
first time you do this you are not doing it for the first time. Bookmark them today; the value is in
having visited them once when nothing was wrong.

### Where a model file comes from, and why the format matters

[05.3 · Licences and trusted sources](../module-05/lesson-03.md) covers the licence side. This is the
side that keeps the box running.

- **Pickle-based formats execute code while loading.** `.pkl`, `.pt`, `.pth` and the raw `torch.load`
  family run arbitrary Python during deserialisation. Loading one is running untrusted code, and
  malicious models have been found on a public model hub.
- **GGUF and safetensors do not, but they are still parsed.** A malformed GGUF file is exactly the
  vector for "Bleeding Llama". "Safe format" is not "safe file".
- **A chat template is code.** GGUF files carry a Jinja template that some runtimes execute at
  inference time. Small surface, real surface.

Four checks before installing anything, and they take two minutes:

1. **Who published it?** A named organisation, or a person with a visible history. Not an account
   with one upload and a good model name.
2. **What format is it?** GGUF or safetensors. Never a pickle, never a "conversion script" somebody
   sent you.
3. **What does the publisher's own page say?** Read it there, not in a listing and not in this course.
4. **Does it match?** Compare against a checksum the publisher published, when they publish one.

## Show me

The course's own stack, checked rather than asserted. The versions are in
[`labs/common/compose.yaml`](../../labs/common/compose.yaml) and mirrored in
[pinned versions](../../references/versions.md), where a bump is a visible act:

| Service | Image | Pinned tag | Notes |
|---|---|---|---|
| Model runtime | `ollama/ollama` | `0.35.0` | Docker Hub, the project's own namespace |
| Chat UI | `ghcr.io/open-webui/open-webui` | `v0.11.4` | The publisher's own registry |
| Home Assistant | `ghcr.io/home-assistant/home-assistant` | `2026.9.4` | The publisher's own registry |
| Vector store (optional) | `qdrant/qdrant` | `v1.19.1` | Only if you took Module 6 |
| Speech-to-text | `rhasspy/wyoming-whisper` | `1.4.0` | Marked *verify during the spike* in versions.md |

Two of those deserve a comment. The `ghcr.io` entries are the publishers' own registries rather
than a community mirror, which removes a whole category of "who re-uploaded this" risk for no
effort. And the Wyoming tags are the ones we have flagged as unverified, because the spike has not
run — an honest course marks what it has not checked instead of borrowing confidence from the other
four.

You can record the exact digest of every image you run, which is stronger than a tag:

```bash
# any OS
docker image inspect --format '{{index .RepoDigests 0}}' ghcr.io/open-webui/open-webui:v0.11.4
```

A tag is a name the publisher promises to mean something; a digest is the bytes. Pin the tag in
`compose.yaml`, record the digest in your notes.

## Try it

1. Write the routine down before you need it. Open
   [the update routine](../../templates/update-routine.md), fill in an owner and a day of the month,
   and put it in your calendar. A routine with no date in a calendar is a document, not a routine.

2. Establish today's baseline — this is the "known good" state you will return to:

   ```bash
   docker compose ps
   docker image inspect --format '{{.Repo.Image}} {{.Id}}' $(docker compose ps -q)
   ```

   On Windows PowerShell the second command needs the ids collected first:

   ```powershell
   docker compose ps -q | ForEach-Object { docker image inspect --format '{{.Repo.Image}} {{.Id}}' $_ }
   ```

3. Visit all four advisory pages and read nothing in particular. The goal is to have the tabs open
   in your browser, which is the single change that most reliably makes the second visit happen.

4. Apply the four-question test to the newest entry you find for Ollama. Write the answers down:
   is the component running, is the fix older than `0.35.0`, does the precondition describe your
   deployment, and who could reach it.

5. Check your models against the four provenance checks. For each one, record the name, the id and
   the size that `ollama list` prints, plus the publisher and format in your own notes. Treat the
   registry as the source of record and your note as a record of what you actually have.

6. Update something, on purpose, as a rehearsal — on a service where a rollback costs nothing. Use
   the order from [pinned versions](../../references/versions.md): read the release notes, bump **one**
   tag, `docker compose up -d`, `python homelab.py doctor`, then the smoke test (one chat message,
   one typed Assist command, one spoken command). If any of the three fails, go back to the pinned
   version before you debug further.

7. Re-measure, so an update's cost is a number rather than a surprise:

   ```bash
   python homelab.py bench --models-only
   ```

   Software updates routinely move generation speed by a noticeable fraction, and that belongs in
   your numbers rather than in your memory.

8. Take a backup before you change anything at all, and know that Module 12.2 is where you will
   practise restoring one.

## Break it

**Break it with `latest` on one service.** Change one tag, pull, and watch what you now know: a
version you did not read the notes for, in a service that has your chat history. It is a small
change and it is the exact one the course bans.

**Break it with a "faster" model file from a direct link.** It scores well on your eval set, it is
a third smaller, and it is a `.pth`. Nothing about the file is checkable, and the payload runs before
the first weight is read.

**Break it with a stale advisory list.** Six months of not looking is not a policy, it is an
accident that happens to have worked so far. This is the failure the routine exists to prevent, and
the only cure for it is the date in the calendar from step 1.

**Break it with an unreachability assumption.** "It is not on the internet, so the CVE does not
apply" is true of the box's *current* state and says nothing about the person who plugs it into a
guest network in six months, or the one who forwards a port to play a game. Reachability is a
property of the deployment, and deployments change.

## Fix it

| Signal | What to do |
|---|---|
| An image tag reads `latest` | Pin the exact version today; nothing else matters until this is done |
| An advisory's fixed version is newer than yours, and the service is unreachable | Put it in this month's window; write the decision in the log |
| The same advisory, and the service answers on a routable address | Update today, and fix the address in the same hour |
| A model arrives as a pickle, from an unfamiliar account | Do not install it; find a published GGUF instead |
| A model arrives in GGUF from a named publisher | Install it, record the digest, keep the runtime current |
| A release note changes a default you depend on | Change one thing at a time, so you know which one broke it |

The order of operations when an advisory does apply is the same every time, and writing it down is
what makes it survivable: **snapshot, bump one tag, `up -d`, `doctor`, smoke test, log it, roll back
if anything fails.** A known-good stack beats a new one, and on a Tuesday evening that is the
difference between a ten-minute problem and a weekend.

## How do I know it works?

- [ ] Every image in your `compose.yaml` is pinned to an exact tag, and none reads `latest`.
- [ ] You have run `doctor` after every change you have made to the stack this month.
- [ ] You have visited all four advisory pages at least once, with nothing wrong.
- [ ] You know the newest advisory for each of the four services, and what your answer is on
      reachability.
- [ ] Every model in your stack is GGUF or safetensors, from a publisher you could name, with its
      id and size recorded.
- [ ] Your update routine has an owner, a day of the month, and a date in a calendar.
- [ ] You have taken one backup and know where it is. Restoring it is [42 · Backups and a restore
      drill](../module-12/lesson-02.md), and it is the part you have not done yet.

## Use it when / avoid it

**Update monthly, on a date, with a smoke test.** The cadence matters far less than the date and the
test. A stack that is rebuilt on an arbitrary Tuesday because something looked wrong is a stack you
cannot roll back.

**Update the host as well as the containers.** Docker Engine, the operating system and the router
firmware are where most real risk lives; the images are the part you chose. A container on an
unpatched host is a patched application on an old kernel.

**Update before you add.** The month you add a service is a bad month to also discover a CVE; do
the window first, then add.

**Avoid updating in the middle of a module.** A lesson that stops working halfway through because
an image tag moved is a lesson you will not finish and will not repeat.

## Reflect

1. Take the newest advisory you found today and answer all four questions in writing. Which one
   changed your answer the most?
2. Which of your installed models could you rebuild the provenance of in two minutes, and which
   could you not?
3. Your machine has been up for 200 days and the stack has never been rebuilt. What is the
   argument for leaving it alone, and the argument against?

## Sources

- [Wiz — CVE-2024-37032 "Probllama", path traversal to remote code execution, fixed in 0.1.34](https://www.wiz.io/blog/probllama-ollama-vulnerability-cve-2024-37032)
- [Cyera — CVE-2026-7482 "Bleeding Llama", unauthenticated memory leak, fixed in 0.17.1](https://www.cyera.com/blog/bleeding-llama-a-critical-memory-leak-in-the-worlds-most-popular-local-ai-platform)
- [SentinelOne vulnerability database — CVE-2025-64496, Open WebUI, fixed in 0.6.35](https://www.sentinelone.com/vulnerability-database/cve-2025-64496/)
- [ReversingLabs — malicious machine-learning models on a public hub](https://www.reversinglabs.com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face)
- [CISA known exploited vulnerabilities catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [Update routine](../../templates/update-routine.md)
- [Pinned versions](../../references/versions.md)
- [05.3 · Licences and trusted sources](../module-05/lesson-03.md)
- [42 · Backups and a restore drill](../module-12/lesson-02.md)
