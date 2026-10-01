---
id: "capstone.rubric"
module: 13
minutes: 20
practice_minutes: 0
prerequisites: ["11.4", "12.4"]
objectives:
  - >-
    Understand the nine criteria your capstone is marked against, and what evidence each one asks
    for before you start building.
volatility: concept
last_verified: "2026-09-30"
---

# Capstone rubric

You build one private home AI stack on your own machine and defend every choice in it with numbers
you measured yourself. This page is the whole marking scheme: nine criteria, what "meets the bar"
looks like for each, and the evidence to hand in.

Two rules apply to every criterion. **Your numbers, not ours.** This course does not publish
community results, and nothing here is passed by matching a figure from a lesson — a slower machine
with an honest explanation scores better than a fast one with an unexplained number. **A criterion
you did not do is marked as not met, however well the rest went.** Leaving a row empty is cheap;
discovering it during marking is not.

## The criteria

| Criterion | What meets the bar | How you show it |
|---|---|---|
| **Sizing** | A prediction for each chosen model made *before* you measured, and the measured tokens/s and RAM afterwards, with the gap between them explained — bandwidth, context, or a mistake | The filled [measure-yours](../templates/measure-yours.md) table, with your prediction column dated earlier than your measurement column |
| **Model choice** | An eval set of at least 20 tasks of your own, run against at least three candidate models, and a chosen model per job justified by those scores *and* their measured speed | The task list, the score table, and one sentence per job naming the winner and the runner-up |
| **Private files** *(only if you took Module 6)* | RAG over a real folder of your own; at least 10 labelled questions; a grounded-answer rate; and a demonstration that deleting a file removes it from the answers | The folder, the questions and labels, the rate, and the before-and-after from the deletion test |
| **Voice pipeline** | Wake word or the typed route → speech-to-text → intents or model → text-to-speech, with a per-stage latency table filled in for your machine, and a misfire rate over the 30-command set | The latency table from Module 8, plus the misfire count and the commands that misfired |
| **Guardrails** | A written list of the entities exposed to the model, each with a reason; a confirmation step for anything with a physical consequence; and tool calls visible in the logs, with some actually read | The entity list with justifications, and a log excerpt showing a confirmation being requested |
| **Security** | Nothing reachable from the internet, checked from outside your own network with the VPN off; remote access only over a VPN; every image pinned to an exact version; a written update routine; and the machine check showing no unexplained warning | The filled [security checklist](../templates/security-checklist.md), including the method and date of the outside check, and the [pinned versions](../references/versions.md) you ran |
| **Operations** | A backup **and a completed restore drill** — a stack started from an archive, with your configuration in it; plus idle memory and idle power measured on your machine | The restore-drill result with its date, and the idle figures from [measure yours](../templates/measure-yours.md) |
| **No cloud** | The outbound-blocked test passes with every feature you rely on still working, run with your feature list in hand, and anything that does reach the internet either disabled or written down with your reason | The control and test output, the feature list, the date, and any accepted exception |
| **Reproducibility** | One `docker compose up` — plus a documented native Ollama step if you used one — rebuilds your stack from the repository and `.env.example`, on a machine that has not seen your `.env` | The commands, in order, as someone else would type them |

## Private files

That criterion applies only if you took Module 6. Skipping Module 6 is a supported path: the capstone
is completable without it, and the other eight criteria are unaffected. Nobody is penalised for a
path they did not choose — the row is simply not part of your submission.

## The write-up

Everything above is defended by **one page of your own writing**, using the
[capstone write-up template](../templates/capstone-write-up.md). It is not a summary of the course
and it is not a list of what you installed. It is a short argument: for each major choice — the
chat model, the speech-to-text model, the keep-alive policy, the segmentation decision, the
publishing decision — state the choice, the number from your own machine that drove it, and the
alternative you rejected.

The test for whether a page is doing its job is simple: someone reading only that page, with no
access to your machine, should be able to tell whether you understood your own stack or copied a
configuration. Numbers with no explanation, and explanations with no numbers, both fail it.

## How this maps to the course

| Criterion | Where you built it |
|---|---|
| Sizing | Modules 2 and 5, [measure yours](../templates/measure-yours.md) |
| Model choice | Module 5, your own eval set |
| Private files | Module 6, and lesson 10.4 for the spoken version |
| Voice pipeline | Modules 8, 9 and 10 |
| Guardrails | Module 10, tools and guardrails |
| Security | Module 11, and the [security checklist](../templates/security-checklist.md) |
| Operations | Module 12, [backups](../templates/update-routine.md) and idle measurements |
| No cloud | [43 · Prove there is no cloud](../lessons/module-12/lesson-03.md) |
| Reproducibility | Module 3, the shared stack, and your own override files |

The two modules that decide how much of this you can complete are 11 and 12, and the two artefacts
they produce — a completed restore drill and a recorded no-cloud test — are the two things people
most often mean to do and do not. Do them before the capstone, not during it.

## Before you submit

- [ ] Every criterion above has evidence attached, and the one-page write-up exists.
- [ ] The prediction column in your sizing table is dated before the measurement column.
- [ ] The outside-the-network check was actually done from outside, with the VPN off, and the date is
      written down.
- [ ] The restore drill finished with a running stack that had your automations in it.
- [ ] Any criterion you deliberately did not do is listed as such, with the reason.
- [ ] Nothing in your submission is a number you did not measure yourself.
