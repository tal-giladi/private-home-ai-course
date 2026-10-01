# Sample household folder

Fictional documents for Module 6. Everything here is invented: no real person, address, account or
device. Names are deliberately repeatable (`Washing Machine`, `Router`) so that entity matching and
aliases are easy to follow.

| File | What it is for |
|---|---|
| `washing-machine-manual.md` | A long document, for testing chunking and retrieval |
| `appliance-warranties.csv` | Structured facts, for testing "when does X end?" |
| `wifi-router-notes.md` | The kind of note people actually write, with the admin password in it |
| `energy-bill-2026-03.csv` | Numbers, for testing arithmetic over retrieved text |
| `recipe-book.md` | Multiple short documents in one file |
| `guest-wifi.txt` | A credential, which is the point of lesson 21 |

Read `questions.txt` in the parent folder for the labelled questions used to check whether answers
are grounded.

> [!CAUTION]
> `wifi-router-notes.md` contains a made-up admin password. It is here so Module 6 has something
> realistic to teach: real notes contain credentials, and a retrieval system that indexes your whole
> home folder will happily surface them. Lesson 21 is about exactly that.
