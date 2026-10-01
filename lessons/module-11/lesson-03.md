---
id: "11.3"
module: 11
minutes: 15
practice_minutes: 30
prerequisites: ["11.2", "07.1"]
objectives:
  - >-
    Explain why reaching a home stack over a VPN removes the need for any port forward, and what each
    option costs you in setup, money and trust.
  - Choose between a managed mesh and WireGuard, and reach a loopback-bound service from a phone
    without publishing it on the LAN.
  - Put IoT devices on a network they cannot use to reach your files, and verify the isolation.
volatility: implementation
sources:
  - title: "Home Assistant — remote access, and why opening a port is not secure"
    url: https://www.home-assistant.io/docs/configuration/remote/
  - title: "Tailscale documentation"
    url: https://tailscale.com/kb/
  - title: "WireGuard quickstart"
    url: https://www.wireguard.com/quickstart/
  - title: "Ollama FAQ — the API has no authentication"
    url: https://docs.ollama.com/faq
last_verified: "2026-09-30"
---

# 11.3 · Remote access the safe way

The question this lesson answers is narrow and practical: how do you open your chat interface from a
phone in another city without opening anything to the world? The answer has a shape, it has two
implementations, and one of them has a surprising cost that is worth saying out loud in a course
about privacy.

> [!WARNING]
> This lesson touches your router, and everything in it is a change to how your house is reachable
> from elsewhere.
>
> - **Nothing here forwards a port.** Remote access is over Tailscale or WireGuard, and that is the
>   only method this course teaches. Home Assistant's own documentation says plainly that simply
>   opening a port is not secure.
> - Read your router's page before you change anything on it, and write down what the setting was
>   before you change it. Firmware updates change menu names and occasionally change defaults.
> - The changes here are reversible: a VPN client can be uninstalled, a guest password reissued, and
>   a DHCP reservation deleted. None of them touches the router's own admin page.

## Why it matters

Everything so far has assumed you are at home. The moment you want your assistant from a phone
outside, three options exist, and only one of them keeps the property this whole course is built on:

| Option | What it means | Verdict |
|---|---|---|
| **Publish a port** | Forward a router port to the stack, usually with a domain and TLS in front | Rejected. Unauthenticated APIs, documented remote-code-execution bugs, and a public address |
| **A cloud relay or tunnel** | A vendor brokers a connection into your home | Rejected here. It is a cloud dependency and, in the providers' case, a subscription |
| **A VPN you operate** | Your phone joins a private network; the stack never sees a public address | This lesson |

The reason the VPN option is different is structural, not cosmetic. **With a VPN there is no port to
forward, because there is nothing listening on your router's public address.** Your phone and your
stack both join a private network with addresses that mean nothing on the internet. Reachability is
then a question about which devices are on that private network, which is a list you control — not
a question about what the internet can find.

## How it works

### Tailscale and WireGuard, honestly

Tailscale is managed coordination plus a WireGuard data plane. You install a client on the stack host
and on your phone, sign in with the same account, and both get addresses on a private tailnet. The
payload is encrypted end to end; the coordination service exists to tell devices about each other
and to hand out addresses.

The honest part, which a course called *Private Home AI* should not hide: **Tailscale's
coordination service is somebody else's computer, and you do create an account.** It can see
metadata — device names, addresses, public keys, when you were online, which nodes talk to which. It
cannot see your chat traffic, your documents or your voice, because it never holds the keys that
decrypt them. If that trade is unacceptable to you, the alternative is below, and the trade-off
list tells you which one it is.

WireGuard is the same cryptography with none of the coordination, run by you. Keys you generate and
hold, a configuration file you wrote, no vendor, no account, no subscription. The cost is that an
endpoint has to be reachable from wherever you are connecting *from*, and a home endpoint that is
reachable from outside normally means a UDP port on your router or a relay machine somewhere else.
That is a real cost and a real decision, and **it is exactly the trade this course refuses to
make.** We do not teach opening ports, and we point you at the managed mesh instead. The exception
worth checking first: if your router runs a WireGuard server natively, no forward is needed at all.

| | Tailscale | WireGuard on your own router | Cloud relay or tunnel |
|---|---|---|---|
| Account needed | One sign-up; there is a free personal plan | None | One sign-up |
| Who runs coordination | The vendor | You | The vendor |
| Data path | End to end encrypted | End to end encrypted | Often through the vendor; read the terms |
| Cost | Free for a household's worth of devices; paid tiers exist for business | Free, if your router supports it | Usually a subscription |
| Setup | Install on two devices, sign in, done | Keys, routing, firewall rules, DNS | Install on two devices, sign in, done |
| Ongoing work | Occasional key expiry, access-list changes | Key rotation, plus firmware upgrades that undo it | Nothing |
| What the vendor can see | Device metadata, not your traffic | Nothing | Whatever the terms allow |
| If the vendor disappears | Existing sessions continue; new devices cannot join | Unaffected | Stopped |

The free-plan device limit is the one number you should check yourself before relying on it, on
Tailscale's own pricing page. We are not going to print a figure that changes.

### Getting to a service that is bound to loopback

This is the part people get wrong, because a VPN connects you to the *host*, and the chat interface
is on `127.0.0.1` of that host. There are two honest ways across it, and the first is usually the
better one.

**Option 1 — keep `WEBUI_BIND=127.0.0.1` and tunnel the last hop over SSH.** The VPN gets you to the
host; the SSH tunnel carries the port the last few metres:

```bash
# Linux / macOS
ssh -N -L 8080:127.0.0.1:8080 homelab
```

```powershell
# Windows PowerShell, same flags
ssh -N -L 8080:127.0.0.1:8080 homelab
```

Then open <http://127.0.0.1:8080> — on the laptop, or on the phone via any SSH client that supports
local forwarding. Nothing on the host changed, and `doctor` still reports loopback only.

**Option 2 — bind the chat interface to the tailnet address only.** In `.env`:

```dotenv
WEBUI_BIND=100.x.y.z
```

That binds the socket to one interface, so LAN traffic to your LAN address gets nothing, and tailnet
traffic works. Two things to know: the address is not stable until you have a reservation for the
host (below), and if the VPN client is not running, the address does not exist and the container
fails to start. That second one is the cost of this option.

> [!NOTE]
> `homelab.py doctor` tests ports against your machine's routable addresses and cannot tell a
> tailnet address from an internet-reachable one, so it will probably flag this port. That is the
> tool being deliberately conservative, and it is why the check that actually matters is the one in
> the checklist below: turn the VPN off, on a network that is not your home, and confirm the address
> does not answer.

### A reverse proxy, and what it does not do

A reverse proxy in front of the web interfaces is worth having when more than one person uses them,
because it gives you one hostname, one place to authenticate, one place to read logs, and TLS if
one day a UI genuinely has to be reachable from a browser that will not sit on your tailnet. Over a
VPN the tunnel is already encrypted, so the proxy's job there is identity and bookkeeping, not
confidentiality in transit.

What a reverse proxy is **not** is a fix for an exposed model server. If the proxy forwards a
request to the model server, the proxy is the only thing in the path — and the model server still
has no authentication of its own. Publish the model server to a proxy you control, on an address
only that proxy can reach, and understand that you have moved the boundary rather than removed it.

The pattern, as a sketch rather than a file you paste in — we have not run a proxy in this course:

```caddyfile
# Illustrative only: a placeholder tailnet hostname and a made-up credential hash.
chat.example-tailscale-host.internal {
    basicauth {                     # identity, in front of every UI
        $argon2id$TWO$...$HASH
    }
    reverse_proxy homelab-open-webui:8080
}
```

### Keeping the cheap bulb away from your documents

The second half of the threat model is the device you did not choose. A bulb from a bargain box, a
camera with a vendor app, a television: unpatched, probably listening, and on the same flat network
as everything you care about. The fix is segmentation, and there are two levels of it.

| | Guest network (SSID) | VLAN |
|---|---|---|
| Cost | Free, on almost every router | A router that supports it; sometimes a managed switch |
| Setup | A new SSID and a password | Per-device or per-port VLAN assignment |
| Isolation | **Often** client-to-client, and usually client-to-main — but verify | Typically enforced by the switch, reliably |
| Right for | Almost everyone starting out | Anyone whose guest network turns out not to isolate |

Then verify, because "guest" on a cheap router frequently means "different SSID, same subnet". From
a phone joined to the guest network, try the stack:

```powershell
# Windows PowerShell
Test-NetConnection 192.168.1.50 -Port 8080
```

```bash
# macOS / Linux
nc -z 192.168.1.50 8080
```

Replace that address with your stack host's LAN address. If it says the port is open, the guest
network is not isolated and the segmentation you thought you had does not exist. Also make sure the
router's own admin page is not reachable from the guest network — an attacker with a cheap bulb and
the router's credentials owns your whole network.

Finally, pin the stack host's address. In your router's admin page, look for **DHCP reservation**,
**address reservation** or **static lease**, and pin the host's MAC to a fixed address. Everything
downstream — VPN names, the Home Assistant integration in 12.4, a reverse proxy — depends on that
address not changing after a reboot.

## Show me

What the finished remote-access story looks like, with no numbers invented and every claim
traceable:

| Path | Who can take it | What it exposes | Notes |
|---|---|---|---|
| Tailnet from your phone, SSH tunnel to loopback | Devices on your tailnet only | The chat interface, through an encrypted tunnel | Nothing on the host changes; `doctor` stays quiet |
| Tailnet, chat interface bound to the tailnet address | Devices on your tailnet only | The chat interface | Needs a DHCP reservation; fails to bind if the VPN is down |
| Tailscale subnet router sharing your LAN | Every device on your tailnet | The whole trusted LAN | Powerful and broad; only if you need it, and then with an access list |
| Anything on the internet | Anyone | Everything | Not an option. The counts of exposed model servers are not theoretical |

Home Assistant's documentation on remote access lists exactly this shape: a cloud relay, a VPN, or a
correctly configured reverse proxy. This course takes the VPN, for the reason in the first table —
the other two make your home reachable by a stranger's infrastructure.

## Try it

1. Install a VPN client on the stack host and on your phone, from the same account. Nothing else in
   the stack changes; the containers do not know the VPN exists.

2. On the host, confirm the new interface and its address:

   ```bash
   # Linux / macOS
   ip -brief addr | grep -E 'tailscale|utun'

   # Windows PowerShell
   Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like '*Tailscale*' }
   ```

   Write the address down. This is the value you will use for `WEBUI_BIND` if you take option 2, and
   the value you will pass to a `ssh -L` target if you take option 1.

3. Set a DHCP reservation in your router for the stack host's current LAN address, before you rely on
   either address being stable. Note the setting's old value first.

4. Connect from the phone, outside your home, and check the tailnet is up. Then use option 1:

   ```bash
   ssh -N -L 8080:127.0.0.1:8080 homelab
   ```

   Open <http://127.0.0.1:8080> on the phone. If the phone has no SSH client with local forwarding,
   take option 2 instead, and set the reservation from step 3 first.

5. **The check that answers the real question.** Turn the VPN off. Stay on the network you are
   currently on — which is not your home — and try the stack's LAN address and its tailnet address.
   Neither should answer. Write the method and the date into
   [the security checklist](../../templates/security-checklist.md), because "it is behind the VPN" is
   only a measurement if somebody did it.

6. Put your IoT devices on the guest network, then run the isolation test from step "verifying"
   above. If the port answers, the guest network is not isolated — write that down, and either fix
   the router's isolation setting or move to a VLAN-capable router.

7. Confirm the router's admin page is not reachable from the guest network. On most routers this is
   a separate toggle; on some it is not there at all, which is itself an answer.

8. Re-run `python homelab.py doctor` from home. Whatever it says about tailnet-bound ports, it must
   not show the model server's port at all.

## Break it

**Break it by forwarding the port "just to test".** It works, which is the problem. The test ends and
the forward stays, and now an unauthenticated API and a home automation server both have public
addresses. If you have done this before, this is your cleanup list: forward 11434 and forward 8123
first.

**Break it with UPnP left on.** UPnP exists so that a game console can ask the router to open a port
for itself. It also means anything on your LAN can ask. Turning it off costs one game that wants to
find its own server, and it removes a mechanism nobody in your house chose to use.

**Break it by trusting the guest network.** A guest SSID on a router that does not implement client
isolation is a second name for the same network. Test it rather than believing it, because the
failure is invisible until something is compromised.

**Break it with a DNS name instead of a tailnet address.** It is convenient, and every convenience
here has a price: dynamic DNS means something outside has to know where you are, and a certificate
for that name means a certificate authority is involved in reaching a private stack.

## Fix it

| Symptom | Cause | Fix |
|---|---|---|
| The chat interface works at home and not from the phone | Bound to `127.0.0.1`; loopback is the host's, not the tailnet's | SSH local forward, or bind to the tailnet address |
| The container will not start after binding to a tailnet address | The address does not exist while the VPN is down | Use option 1, or start the VPN before the stack |
| The LAN can reach a port you bound to the tailnet | You bound `0.0.0.0`, not the tailnet address | Bind the specific address; a bound socket does not appear on other interfaces |
| A guest-network device reaches the stack | No isolation on that SSID | Enable client isolation, or use a VLAN, or change router |
| Remote access stops working after a router firmware update | Reservation lost, or a default changed | Re-check the reservation; keep a note of every setting you changed |
| Voice commands fail from a satellite on another network | The satellite publishes on the host's LAN address only | Publish the satellite's ports on the tailnet address, and only that |

## How do I know it works?

- [ ] You can reach the chat interface from a phone on a network that is not your home.
- [ ] With the VPN off, on that same outside network, the stack answers on nothing.
- [ ] No port forward exists in your router for 11434, 8080, 8123 or any other stack port.
- [ ] UPnP is off, or you have written down why it is on.
- [ ] A device on the guest network cannot reach your stack, and you tested rather than assumed.
- [ ] The router's admin page is not reachable from the guest network.
- [ ] The stack host has a DHCP reservation, and you know its fixed LAN address.
- [ ] The model server still has no `ports:` line, and `doctor` still does not see its port.

## Use it when / avoid it

**Use a VPN for everything remote, including the things that feel too small to matter.** Voice
satellites, a chat interface on your watch, checking from a hotel: the same rule, and the cost of
getting it wrong does not scale down with how important the feature seemed.

**Use a reverse proxy when more than one person uses the stack**, and not before. One hostname and
one authentication point beats four remembered addresses, and it is the only place to read who
connected when something looks wrong.

**Avoid a mesh when you need it once a year.** The setup is ten minutes and the ongoing work is
minimal, but if you never connect remotely, the honest answer is that the stack is safer with
everything on loopback and no client installed at all.

**Avoid WireGuard on a router you do not also administer well.** A VPN is a new surface: keys, routes
and a firewall rule that did not exist last week. If your router's VPN page is unfamiliar, the
managed mesh is the lower-risk way to get the same property.

## Reflect

1. You now have a tailnet. What exactly did you give up to get it, and would a reader of your
   network traffic be able to tell that you use one?
2. Your guest network turned out not to isolate. What is the cheapest change that gives you real
   segmentation, and what does it cost in time and in hardware?
3. Somebody offers to "just put a free dynamic DNS on it so you can reach it anywhere". List
   everything that changes about your exposure when you accept.

## Sources

- [Home Assistant — remote access, and why opening a port is not secure](https://www.home-assistant.io/docs/configuration/remote/)
- [Tailscale documentation](https://tailscale.com/kb/)
- [WireGuard quickstart](https://www.wireguard.com/quickstart/)
- [Ollama FAQ — the API has no authentication](https://docs.ollama.com/faq)
- [Security checklist](../../templates/security-checklist.md)
- [38 · Bind addresses and ports](../module-11/lesson-02.md)
- [40 · Updates, CVEs and model supply chain](../module-11/lesson-04.md)
