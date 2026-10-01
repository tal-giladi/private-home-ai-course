---
id: "06.2"
module: 6
minutes: 12
practice_minutes: 35
prerequisites: ["06.1"]
objectives:
  - >-
    Decide which folders to index and which never to, using the credential problem as the worked
    example.
  - Keep an index in sync with a folder that changes, and make deletion remove content from answers.
  - >-
    Reduce prompt length by narrowing the indexed folder rather than by improving the model.
volatility: concept
sources:
  - title: "Home Assistant — remote access and why a port is not it"
    url: https://www.home-assistant.io/docs/configuration/remote/
last_verified: "2026-09-30"
---

# 06.2 · Which folders to index

A retrieval system indexes whatever you point it at and answers from whatever it finds, including
the line in your router notes that contains the admin password. This lesson is the one where the
course stops being about technology and starts being about judgement, and it is the one most worth
reading twice.

## Why it matters

Look at the sample folder the course ships. Two of its ten labelled questions ask for a credential
— the router admin password and the guest Wi-Fi password — and a retrieval system will answer both,
correctly, with a citation, because they are written down in documents you gave it.

That is not a retrieval bug. That is a retrieval system doing exactly what you asked.

The lesson is that "index my documents" is a disclosure decision, and it should be made the way any
disclosure decision is made: deliberately, folder by folder, with a reason you can write down. The
capstone asks for exactly this list.

> [!CAUTION]
> Never index a folder that contains credentials, key material, tax returns, medical records or
> anything you would not paste into a public website — *even though the stack is local*. The model
> is local, but the index is a searchable copy of your files sitting in a database, and the chat
> interface will cheerfully display any of it to anyone who reaches that port.

## How it works

### A test that works on any folder

Ask three questions about a candidate folder:

1. **Would I be comfortable if this text appeared in an answer to a stranger's question?**
2. **Does it contain anything whose value lies in nobody reading it?**
3. **How long will it be true, and will I remember to delete it when it stops being?**

A folder that fails any one of them does not get indexed whole. It gets filtered first: copy the
documents you want into a dedicated folder, and leave everything else where it is.

### The pattern that makes this manageable

```text
<home>/homelab-index/
  manuals/          copies of appliance manuals
  warranties/       one row per appliance, no credentials
  notes/            your own notes, scrubbed
  NOT-indexed/      everything else, deliberately
```

The copy is the point. If the index reads from the source, you have to remember every time you edit
a source. If it reads from a copy you curate, the difference between "in the index" and "on my
disk" is a directory listing you can read in two seconds, and it is the answer to the capstone
question.

### Keeping it in sync

Three options, in increasing order of effort and decreasing order of forgetting:

| Approach | Effort | Forgetting risk |
|---|---|---|
| Re-ingest by hand when you remember | none | high |
| A weekly scheduled re-ingest | a cron line | low |
| Watch the folder and re-ingest on change | a small script | lowest, and slowest to build |

For a home folder that changes monthly, **a weekly re-ingest is the right answer**. The thing people
get wrong is not forgetting to re-ingest; it is forgetting to *remove*, so a document you deleted
from disk six months ago is still in the index and still answers questions.

Deletion therefore has to be a re-ingest, not an edit. If your system has a "delete document"
action, use it; if it has a "rebuild the index" action, use that. Test it deliberately — delete a
document, re-ingest, and ask a question only it could answer. The answer should now be "I don't
know".

## Show me

The decision for the course's sample folder, written out so you can copy the format:

| Folder | Indexed? | Reason |
|---|---|---|
| Appliance manuals | Yes | Public documents, no credentials, stable |
| Warranty records (CSV) | Yes | Exactly the kind of thing a model cannot guess |
| Energy bills | Yes | Your own data, useful, low sensitivity |
| Recipe book | Yes | Nothing to lose |
| **Router notes** | **No — copy and scrub** | Contains the router admin password, and the house Wi-Fi password |
| **Guest Wi-Fi note** | **No** | A credential handed to guests should not be retrievable by the model |
| Anything under `~/.ssh`, browser profiles, password stores | Never | These are credentials by definition |

Two of the sample questions therefore cannot be answered by a correctly configured index, and
that is the correct behaviour. Your eval set should include them precisely so you notice.

## Try it

1. Make the decision for one real folder of yours, in writing. Use the table above. Ten minutes,
   and it is the capstone's first answer.

2. Build the curated folder and point the knowledge base at **that**, not at your documents
   directory. If the copy step is too much to start with, at least exclude the one folder you know
   contains credentials.

3. Test the exclusion. Ask the two credential questions from the sample set. A correctly scoped
   index refuses or answers without the secret; a badly scoped one hands it over with a citation.

   ```bash
   # Windows PowerShell
   Select-String -Path .\samples\en\household\*.md,.\samples\en\household\*.txt `
     -Pattern "password" -SimpleMatch
   ```

   That is a deliberately crude check, and it is exactly the right first pass: grep for the word
   "password" in anything you are about to index. Extend the list — "secret", "token", "key",
   "api", "credential" — and it catches most of what people forget.

4. Test deletion properly:

   ```bash
   # Windows PowerShell
   Remove-Item .\indexed\warranties.csv
   ```

   Re-ingest, then ask a question only that file could answer. The answer must now be that the
   system does not know. If it still answers, your system has no delete path, and that is a fact
   you need before you add anything private to it.

5. Reduce the prompt by narrowing the folder, not by improving the model. Index only `manuals/`
   rather than everything, ask the same question, and time the first word. Compare with the wider
   index. Fewer chunks is the cheapest speed-up in this course.

## Break it

**Break it with the obvious mistake.** Point the index at your whole documents folder. Now the
question "what is my wifi password" is answered perfectly, with a citation, in under two seconds.
Technically the system is working exactly as designed, and it has just turned a chat interface into
a search box for every secret in your house.

**Break it with a stale deletion.** Add a document, ask about it, delete it from disk, ask again
without re-ingesting. The answer persists, confidently, from a file that no longer exists. Anyone
who later changes that password has a stale copy in your index.

**Break it with a shared folder.** Index a folder on a network share that other people write to.
Now the content of the index changes when someone else's document syncs, and you did not choose
what entered it.

**Break it with an index you cannot audit.** Ten folders, no record of what is in them, no delete
path, no re-ingest. This is the state most people's RAG setup reaches after a year, and it is
unrecoverable without starting over.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| The model answers with a credential | The folder was indexed whole | Rebuild the index from a curated copy |
| A deleted file still answers | No delete path, or no re-ingest | Rebuild the index; verify by asking again |
| A new file is invisible | Index is a snapshot | Re-ingest; automate it weekly |
| Answers are slow | Too many chunks | Narrow the folder or lower `RAG_TOP_K` |
| You cannot tell what is indexed | No list | Keep a text file of exactly what you copied in |

The fix in the last row is the one to do first and the one people skip. A plain text file listing
the contents of your curated folder is worth more than any configuration option.

## How do I know it works?

- [ ] You have a written list of what is indexed and one line of reason per folder.
- [ ] Your index reads from a curated copy, not from your working documents folder.
- [ ] The credential questions are refused, or answered without the secret.
- [ ] You have deleted a document, re-ingested, and confirmed the answer disappeared.
- [ ] You know how to make the index match the folder again, without re-reading a lesson.

## Use it when / avoid it

**Use a curated copy** whenever a folder contains anything you would think twice about. The copy
costs disk you already have and ten minutes you would otherwise spend remembering.

**Re-ingest on a schedule.** A weekly job is the right frequency for a home folder, and the habit
matters more than the mechanism.

**Avoid indexing anything whose value lies in nobody reading it.** Passwords, keys, tokens,
recovery codes, and anything with a person's name and a medical detail attached.

**Do not treat "it is on my own machine" as the answer.** The index is a searchable copy, the chat
interface will display it to anyone who reaches that port, and in Module 11 you may well widen that
port for your phone.

> [!NOTE]
> The capstone requires a folder list with a reason per entry. Writing it takes ten minutes now and
> saves the two hours of reconstructing what you decided six months ago.

## Reflect

1. Which folder would you most want to index, and what would you have to remove from it first?
2. If someone asked "what does your AI know about me?", could you answer completely and honestly
   from what you have written down?
3. What happens to the guarantee in "deleting a file removes it from answers" if your system has no
   rebuild action at all?

## Sources

- [Qdrant documentation — collections and deleting points](https://qdrant.tech/documentation/)
- [Open WebUI documentation — knowledge bases](https://docs.openwebui.com)
- [Home Assistant — remote access](https://www.home-assistant.io/docs/configuration/remote/)
- [Security checklist](../../templates/security-checklist.md)
- [22 · Is the answer right?](lesson-03.md)
- [The capstone rubric](../../assessments/capstone-rubric.md)