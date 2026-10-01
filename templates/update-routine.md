# Update routine

Half an hour a month. The point is not that you patch everything — it is that when a local model
server has a remote-code-execution bug, you find out from the advisory list and not from an
intrusion.

**Owner:** ____________________
**Day of the month:** ____________________

## Before the window

1. `docker compose pull` — read the release notes for anything whose version jumped by more than a
   patch number. Model servers in particular: a minor bump can change default flags.
2. Check the advisories for the four services that matter most to you. The ones in this course are:
   - Ollama — <https://github.com/ollama/ollama/security/advisories>
   - Home Assistant — <https://github.com/home-assistant/core/security/advisories>
   - Open WebUI — <https://github.com/open-webui/open-webui/security/advisories>
   - Wyoming services — <https://github.com/rhasspy/wyoming>
3. Note whether any advisory mentions an **unauthenticated** endpoint, a path traversal or a parser
   bug in model files. Those are the ones that matter for a box on your home network.

## During the window

- [ ] Pull the new images.
- [ ] Re-read `compose.yaml` and bump the pinned tags; never leave `latest` in place.
- [ ] `docker compose up -d` and watch the logs for a minute.
- [ ] Run `python homelab.py doctor` — it should still print no `0.0.0.0` warnings.
- [ ] Run the smoke test: one chat message, one typed Assist command, one spoken command.
- [ ] If any of the three fails, `git checkout compose.yaml` and go back to the pinned versions
      before you debug further. A known-good stack beats a new one.

## After the window

- [ ] `docker image prune -f` to reclaim the old images once the new ones are proven.
- [ ] `python homelab.py bench --quick` to see whether the update changed your speeds. Software
      updates routinely change them by 10–20%, and that is worth knowing.
- [ ] Note the change in the log below.

## Backups

Monthly, after the update, and always before anything large changes:

- [ ] Home Assistant configuration and `.storage`
- [ ] The vector index, if you built one (it can be rebuilt, so a nightly copy is often enough)
- [ ] Chat history, if you care about keeping it
- [ ] `compose.yaml` and `.env` (`.env` into a password manager, not into git)
- [ ] **Models are not backed up.** They are re-downloadable, and they are the largest thing you have.

## Log

| Date | Versions changed | Advisories that applied | Smoke test | Bench delta | Notes |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
