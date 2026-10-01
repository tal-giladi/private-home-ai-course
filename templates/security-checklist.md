# Security checklist

Work through this once after Module 11 and again before the capstone. Every line is either true for
your stack or it is a hole. `homelab.py doctor` checks the machine-checkable half automatically.

## Exposure

- [ ] No service is reachable from the internet. No port forwards, at all, for any of these services.
- [ ] `homelab.py doctor` prints **no** `0.0.0.0` warnings.
- [ ] Checked from *outside* your network, not just from the LAN. Method used: ____________
- [ ] The router has UPnP turned off, so nothing can open a port on its own.
- [ ] Nothing in the stack uses a cloud relay or a hosted control panel as its only way in.

## Bind addresses and networks

- [ ] Ollama binds `127.0.0.1` unless a lab explicitly says otherwise.
- [ ] Every service with an unauthenticated API is on an internal Docker network, not published.
- [ ] Published ports are the chat UI only, and only after you understood the consequence in 11.2.
- [ ] Web UIs reachable from other devices on the LAN have authentication turned on with a real password.
- [ ] Containers run as a non-root user where the image allows it.

## Remote access

- [ ] Remote access is over Tailscale or WireGuard only. Provider used: ____________
- [ ] Nothing else is used instead (no `ngrok`, no public tunnel, no dynamic DNS to the stack).
- [ ] The VPN is the only route in; the same services are not also exposed another way.

## Secrets and accounts

- [ ] Every account that can reach the stack has a unique password from a password manager.
- [ ] Secrets live in `.env` files that are gitignored, never in `compose.yaml` or in a lesson.
- [ ] Home Assistant's default account is not "admin"/"admin".
- [ ] Open WebUI has at least one local account, and the first-created admin password was changed.
- [ ] Telemetry and crash-report settings are off where the setting exists.

## Segmentation

- [ ] IoT devices are on a guest network or a VLAN, not on the same network as the AI box.
- [ ] The AI host can reach the internet only to pull updates and models, and this is deliberate.
- [ ] The router's admin interface is not reachable from the IoT network.

## Supply chain and updates

- [ ] Every image in `compose.yaml` is pinned to an exact version tag. No `latest`.
- [ ] Every model came from a named publisher, in GGUF or safetensors form, never a pickle file.
- [ ] A monthly update routine exists and has a date in the calendar. Next update: ____________
- [ ] You know how to check whether an advisory affects your pinned versions, and you have checked once.
- [ ] The last backup was taken and **restored successfully** at least once. Date: ____________

## Home Assistant safety (Module 10)

- [ ] Few entities are exposed to the LLM; the list is written down and has a reason for each entry.
- [ ] Locks, alarms, garage doors, covers and anything with a physical consequence are **not** exposed
      without a confirmation step.
- [ ] Tool calls are visible in the logs, and you have actually read some of them.
- [ ] The misfire rate on your 30-command set is written down. Current value: ______ %

## Privacy

- [ ] The "no cloud" test passes: with outbound traffic blocked, every feature you use still works.
- [ ] You know which of your folders is indexed and which deliberately is not.

---

**Notes, things that surprised you, and anything you deliberately accepted as a risk:**

______________________________________________________________________
