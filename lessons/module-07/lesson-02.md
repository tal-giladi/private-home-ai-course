---
id: "07.2"
module: 7
minutes: 12
practice_minutes: 35
prerequisites: ["07.1"]
objectives:
  - Send Assist a typed command and get the right entity changed.
  - Explain what exposing an entity actually does, and why it is opt-in per assistant.
  - Fix the three common reasons a sentence is understood but nothing happens.
volatility: concept
sources:
  - title: "Home Assistant — exposing entities to Assist"
    url: https://www.home-assistant.io/voice_control/voice_remote_expose_devices/
  - title: "Home Assistant — Assist pipelines"
    url: https://www.home-assistant.io/voice_control/pipelines/
  - title: "Home Assistant — aliases for entities, areas and floors"
    url: https://www.home-assistant.io/voice_control/aliases/
last_verified: "2026-09-30"
---

# 07.2 · Assist with typed commands

Typing "turn on the kitchen light" into Assist and watching it happen is the fastest way to
understand what the voice path will do later, with no microphone and no speech model in the way.
This lesson is about that loop, and about the one setting — exposure — that decides what the
assistant is allowed to touch.

## Why it matters

Two things become clear from typing rather than speaking:

1. **Assist already works without any AI.** Built-in intents cover control. What a language model
   adds is *open-ended* understanding: "it's cold in here", "what did I leave on last night". The
   split matters enormously in Module 10, where you will decide what each does.
2. **Exposure is a security decision wearing a usability costume.** An entity is not controllable
   by Assist until you expose it, per assistant, and the list you expose becomes the list a model
   can choose from. People are surprised by this at exactly the moment they realise the assistant
   knows about the front door lock.

Typing is also the accessibility route. Every voice lab in this course can be completed without a
microphone, and the capstone rubric accepts it.

## How it works

### The pipeline, in one sentence

A sentence arrives, becomes an **intent** plus optional **slots**, and the intent runs against the
exposed entities. `turn on` is an intent; `kitchen light` is a slot value resolved against your
entity names, aliases and areas.

### Entities, areas, aliases

| Concept | What it is | Why it exists |
|---|---|---|
| Entity | One controllable thing, e.g. the kitchen light | The thing an intent acts on |
| Area | A named place, e.g. "Kitchen" | So "turn on the kitchen light" can be said as "turn on the lights in the kitchen" |
| Floor | A named floor, e.g. "Ground floor" | The same, one level up |
| Alias | An extra name for one of the above | The word you actually say |

Assist matches the words you type against the names, aliases, areas and floors of the entities you
have **exposed**. Miss one and nothing happens.

### Exposure is per assistant

This is the detail that catches people. Exposing an entity to one assistant does not expose it to
another. That is what lets you have a "guest assistant" with five lights and a "house assistant"
with twenty, and it is the mechanism Module 10 uses to keep the risky entities out of the model's
reach.

### What built-in intents can and cannot do

| Can | Cannot |
|---|---|
| Turn things on and off, set brightness and colour | Answer a question |
| Read sensor values | Explain anything |
| Set and cancel a timer | Do anything not in its sentence list |
| Add to a list, if one exists | Understand "it's cold in here" |

The right-hand column is where a language model earns its place — and where it earns your caution.
Module 10 measures both halves.

## Show me

The three settings that decide whether a typed sentence works, and nothing else:

```text
1. The entity exists          → Demo entities from lesson 07.1
2. The entity is exposed      → Settings → Voice assistants → your assistant → Expose
3. The words match a name     → entity name, an alias, or an area the entity belongs to
```

Everything else is downstream of those three. When a command does nothing, check them in that order,
because it is nearly always one of them.

A useful test sequence, with the failure each step reveals:

| Try | If it fails, you learn |
|---|---|
| `turn on the kitchen light` | Exposure and naming are fine |
| `turn on kitchen light` (no "the") | The "the" was doing work in your naming |
| `turn on the lights in the kitchen` | Area assignment is missing |
| `turn on the kettle` | Not exposed, or not a light |
| `what is the temperature in the bedroom` | Sensor exposure, or the sensor does not exist |

## Try it

1. Open Assist in the Home Assistant UI and type a command. The developer tools page is the
   fastest route:

   ```bash
   # The UI path: Developer Tools -> Assist -> the text box
   ```

   Try: `turn on the kitchen light`

2. Check the light actually changed — both in the dashboard and in the entity's own page, where its
   state and brightness are visible. "It said it did it" and "it did it" are different claims, and
   the second one is the one that matters.

3. Expose the rest of the demo entities and retry. **Settings → Voice assistants → (your
   assistant) → Expose**. Expose the lights, the temperature sensors and the heater. Leave the front
   door lock alone for now and notice in Module 10 that the model cannot see it either.

4. Give one entity an area, and one an alias, and watch the difference:

   ```yaml
   # in your own configuration, not the read-only demo file
   homeassistant:
     customize:
       - entity_id: light.hall_light
         area: Hallway
         alias: The Passage
   ```

   Now `turn on the hall light`, `turn on the light in the hallway`, and `turn on the passage` all
   work. One entity, three phrasings.

5. Find out what Assist thinks you said. In **Developer Tools → Assist**, switch on the "show
   intent" or debug output. You will see the intent name and the slot values it extracted. Reading
   these is the fastest way to learn what the built-in sentence grammar accepts.

6. Run the thirty commands from the sample set, typed rather than spoken. Module 10 uses the same
   list for the misfire measurement, and the text route removes the speech model from the
   comparison entirely — which is exactly what you want when you are measuring the brain rather
   than the ear.

   ```text
   01 turn on the kitchen light          16 what is the washing machine warranty end date
   05 what is the temperature in the bedroom   24 summarize the washing machine manual in three sentences
   26 unlock the front door              30 tell me the wifi admin password
   ```

   Note which of the thirty built-in intents handle and which need a model. That split is the next
   three modules.

## Break it

**Break it by not exposing.** Turn on everything in the dashboard, then say "turn on the kitchen
light". Nothing happens and Assist says it could not understand. This is by design, and it is the
single most common early confusion.

**Break it with a name Assist cannot hear.** Rename an entity to something with no consonants — "A
C D lights" — and watch the sentence fail on the letter, not the light.

**Break it by expecting a question to be answered.** Try "is it cold in here?" Built-in intents
control; they do not answer. This is exactly the gap Module 10 fills.

**Break it with too much exposure.** Expose every entity you own, including the lock and the alarm,
"just to see". Assist can now act on all of them — and in Module 10 a model will be choosing among
them. This is a habit worth breaking before it forms.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| "I could not understand" | Not exposed, or no matching name | Expose it, or add an alias |
| Right entity, wrong action | You said a question, not a command | That needs a model — Module 10 |
| Works with "the", fails without | The article is part of the matched phrase | Rename, or add the shorter form as an alias |
| "The lights in the kitchen" does nothing | No area, or the entity has no area | Assign the entity to an area |
| Works for one assistant, not another | Exposure is per assistant | Expose it for the assistant you are using |
| Understands the words, does nothing | A slot did not resolve | Read the intent output in developer tools |

The general fix: **read the intent output.** Home Assistant tells you which intent it matched and
what it put in each slot, which turns a guessing game into a two-minute check.

## How do I know it works?

- [ ] Ten typed commands from the sample set change the right entities.
- [ ] You can name the three settings that decide whether a command works, and check them in order.
- [ ] One entity responds to its name, its area and its alias.
- [ ] You know which of the thirty sample commands built-in intents handle.
- [ ] You have deliberately left the lock and the alarm unexposed, and can say why.

## Use it when / avoid it

**Use the typed route to debug and to build.** Every voice problem is easier to find when the
sentence is already in front of you as text.

**Expose narrowly.** The smallest list that makes the assistant useful is the right list. Every
exposed entity is one more thing a model can choose, and a mistake is proportionally cheaper with
five entities than with fifty.

**Use areas and aliases rather than fighting the grammar.** They are what the system is designed
around, and they take ten minutes instead of an evening of custom sentences.

**Do not expose locks, alarms, garage doors or covers to start with.** Module 10 has a specific
lesson about why, and a specific mechanism for adding them back safely.

> [!NOTE]
> Developer tools and the Assist debug output are the same interface the course's later labs use
> to read tool calls. Getting comfortable with it here is the reason Module 10's misfire
> measurement is quick.

## Reflect

1. Which of your entities could Assist not reach before you exposed them, and which would you still
   rather it did not?
2. "It's cold in here" is a question and not a command. What would a language model have to know to
   answer it correctly — and what could it get wrong?
3. If you had a guest assistant for visitors, which three entities would you expose and which
   reasoning would you use?

## Sources

- [Home Assistant — exposing entities to Assist](https://www.home-assistant.io/voice_control/voice_remote_expose_devices/)
- [Home Assistant — Assist pipelines](https://www.home-assistant.io/voice_control/pipelines/)
- [Home Assistant — aliases for entities, areas and floors](https://www.home-assistant.io/voice_control/aliases/)
- [Home Assistant — built-in sentences](https://www.home-assistant.io/voice_control/builtin_sentences/)
- [Sample command set](../../labs/common/)
- [35 · Tools and guardrails](../module-10/lesson-03.md)