---
id: "07.3"
module: 7
minutes: 11
practice_minutes: 35
prerequisites: ["07.2"]
objectives:
  - Add a custom sentence that matches a phrase Home Assistant does not know.
  - Trigger an automation from a spoken phrase and from a sensor state.
  - Explain the difference between a sentence that matches and an intent that acts.
volatility: implementation
sources:
  - title: "Home Assistant — custom sentences"
    url: https://www.home-assistant.io/voice_control/custom_sentences/
  - title: "Home Assistant — automation triggers"
    url: https://www.home-assistant.io/docs/automation/trigger/
last_verified: "2026-09-30"
---

# 07.3 · Custom sentences and voice automations

Built-in sentences cover a lot. They do not cover "good night", your own phrase for a room, or the
one sentence your household says in a way nobody anticipated. Custom sentences fill that gap, and
automations are what the gap connects to.

## Why it matters

Two reasons, and the second is the one that changes how the system feels.

The first is coverage: a fixed sentence list cannot contain every way a family talks, and a
household that has to speak the software's language stops using it.

The second is **mapping**. A custom sentence can turn any phrase you like into a normal
automation trigger, and an automation can do several things at once. "Good night" that turns off
three lights, checks the door and says something is one phrase, not three commands — and it is
deterministic, which means it never misfires.

That is the pattern this whole course converges on: fixed, deterministic phrases for the things
that matter, and a model for the things that need understanding.

## How it works

### Two files, two jobs

| Concept | What it is | Where it lives |
|---|---|---|
| **Custom sentences** | Turns a phrase into an intent and slots | `custom_sentences/<language>.yaml` |
| **Automations** | Fires on an intent, a sentence, or a state change | `automations.yaml` or the UI |

A sentence matches text and produces an intent. An intent does something. Keeping them separate is
what lets one phrase drive several actions.

### Lists and slots

Sentences use *lists* — named sets of words — and *slots*, which are placeholders filled from those
lists:

```yaml
intent_script: !include custom_sentences/en.yaml
```

```yaml
language: en
intents:
  SetTimerByWord:
    speech:
      - "set a {word} timer for {minutes} minutes"
  lists:
    minutes:
      values: ["one", "two", "three", "five", "ten", "fifteen", "twenty", "thirty"]
```

"set a laundry timer for five minutes" then matches, and `{word}` and `{minutes}` arrive as
`laundry` and `5`.

### Where to put the file

```yaml
# configuration.yaml
intent_script: !include custom_sentences/en.yaml
```

**Language-sensitive block:** every phrase in this lesson is something a person says. A translated
version of the course replaces the phrases and keeps the structure exactly.

The course ships a worked file at
`labs/common/samples/en/homeassistant/custom-sentences-en.yaml` with a timer phrase, a room phrase,
a "good night" scene and a deliberately-unanswerable question that teaches the model its own
limits.

## Show me

The two patterns worth copying, both from the course's sample file:

```yaml
  # A phrase Home Assistant does not know, mapped to an existing entity set.
  - SetBlindsByRoom:
      speech:
        - "drop the {area} blinds halfway"
        - "half close the {area} blinds"
      slots:
        area:
          - name: Living room
          - name: Bedroom
          - name: Study

  # Several actions from one phrase, entirely deterministic.
  GoodNightScene:
    speech:
      - "good night"
      - "good night house"
      - "everything off"
    action:
      - stop: ""
      - turn_off: []
      - set_conversation_response: "Good night. Lights off, doors checked."
  - action:
      - turn_off:
          entity_id:
            - light.kitchen_light
            - light.living_room_lamp
            - light.hall_light
            - switch.hall_heater
```

The second block is the shape to aim for. "Good night" cannot be misheard into doing the wrong
thing, because there is no interpretation step at all — the phrase *is* the action.

## Try it

1. Copy the sample custom sentences into your running instance:

   ```bash
   # Windows PowerShell
   Copy-Item .\samples\en\homeassistant\custom-sentences-en.yaml `
     .\config\custom_sentences\en.yaml -Force

   # macOS / Linux
   mkdir -p config/custom_sentences
   cp samples/en/homeassistant/custom-sentences-en.yaml config/custom_sentences/en.yaml
   ```

   Then add the include to your `configuration.yaml`:

   ```yaml
   intent_script: !include custom_sentences/en.yaml
   ```

2. Validate before restarting. This saves the restart-restart-restart loop:

   ```bash
   docker compose exec homeassistant \
     python3 -m homeassistant --script check_config -c /config
   ```

3. Restart Home Assistant, then in **Developer Tools → Assist** try each phrase: "good night",
   "everything off", "drop the bedroom blinds halfway", "is it warm in the kitchen". The last one
   should respond that it does not know — deliberately, and it is the most useful line in the file.

4. Add an automation that a phrase triggers. In **Settings → Automations & scenes → Automations →
   Create**, choose **Trigger → Sentence**, pick your sentence, and add an action:

   ```yaml
   alias: Kitchen lights off after ten minutes
   trigger:
     - platform: state
       entity_id: light.kitchen_light
       to: "on"
       for:
         minutes: 10
   action:
     - service: light.turn_off
       target:
         entity_id: light.kitchen_light
   ```

   That is not a voice automation, and it is the more valuable half of this lesson: a house that
   turns the lights off by itself does not need to be asked. Put it somewhere sensible, then check
   whether your family actually turns the kitchen light on for ten minutes.

5. Connect a sentence to that behaviour. Add a "movie time" phrase that dims the lamp and turns the
   kitchen light off, and check that it does both.

6. Read the automations list in the UI and ask which of them you would still want if the voice
   assistant stopped working tomorrow. The answer to that is your actual automation, and it is
   usually shorter than the list.

## Break it

**Break it with a YAML error in the sentences file.** One malformed block makes Assist refuse *all*
custom sentences, including the ones that worked. Check the log; the message names the file and
roughly where.

**Break it with an unmatched list.** A sentence refers to `{minutes}` but the list defining it is
missing or misspelled. The phrase never matches, and the failure looks like a recognition problem
rather than a configuration one.

**Break it by mixing quotation styles.** Apostrophes in phrases inside YAML cause silent breakage,
and the course's own file uses double quotes throughout for exactly that reason.

**Break it with a phrase that sounds like another.** Add "set the kettle on" and "set the kettle
off" with similar wording; at a noisy microphone they will collide. This is the failure mode that
motivates a wake word in Module 9.

**Break it with an automation you cannot explain.** Build a scene while exploring, and six months
later nobody knows why the hallway light turns on at 22:00. Name every automation after what it
does for the household, not after the technique.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| No custom sentence matches at all | YAML error in the sentences file | `check_config`, then read the log |
| One phrase matches, others do not | A missing or misspelled list | Check every `{placeholder}` has a list |
| The file is not loaded | Missing `intent_script` include, or the wrong path | `!include custom_sentences/en.yaml` |
| Sentences work but no action follows | The intent matched with no script bound to it | Add an action, or map it to a script |
| Two phrases collide on the microphone | Too similar | Reword one; this is a wake-word argument |
| Automations fire at the wrong time | A `for:` duration that is too long or too short | Change it and watch it for a day |

## How do I know it works?

- [ ] `check_config` passes with your sentences file in place.
- [ ] Four phrases from the sample file work in Developer Tools → Assist.
- [ ] "good night" turns off all three lights and the heater in one step.
- [ ] You have at least one automation that runs without any voice involvement at all.
- [ ] Every automation you have is named after what it does for the household.

## Use it when / avoid it

**Use custom sentences for phrases a household says often and expects to work every time.** They
are deterministic, instant, and impossible to misfire into the wrong action.

**Use a sentence to trigger an automation rather than a long chain of intents.** One phrase, one
action, one place to look when it misbehaves.

**Prefer automation to speech for anything predictable.** If a thing happens at a time or a state,
Home Assistant should do it on its own. Speech is for what you want *when* you want it.

**Avoid adding sentences nobody says.** Every phrase is something to maintain, and every similar
pair is something that can collide.

> [!NOTE]
> This is also the least language-dependent part of the course. The structure — lists, slots,
> intents, actions — is the same in every language, and the sample file is structured so a
> translated version replaces phrases and nothing else.

## Reflect

1. Which of your automations would a guest get wrong by saying the wrong thing, and how would you
   make that safe?
2. If a family member says "good night" meaning "I am going to bed", what should happen, and should
   any of it be a model decision rather than a fixed phrase?
3. How many custom sentences do you actually need for your household, and what would the last three
   be?

## Sources

- [Home Assistant — custom sentences](https://www.home-assistant.io/voice_control/custom_sentences/)
- [Home Assistant — automation triggers](https://www.home-assistant.io/docs/automation/trigger/)
- [Home Assistant — best practices with Assist](https://www.home-assistant.io/voice_control/best_practices/)
- [Sample custom sentences](../../labs/common/)
- [Using Piper in automations](https://www.home-assistant.io/voice_control/using_tts_in_automation/)
- [31 · Your laptop as a voice satellite](../module-09/lesson-02.md)