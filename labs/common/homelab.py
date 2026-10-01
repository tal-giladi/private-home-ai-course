#!/usr/bin/env python3
"""homelab - doctor and bench for the Private Home AI course.

Two commands, standard library only, no install step:

    python homelab.py doctor     what machine is this, which tier, which model to start with
    python homelab.py bench      prompt and generation speed, peak RAM, voice stage timings

`doctor` never changes anything. `bench` only reads, sends a few prompts to a model server you
already run, and plays nothing. Run `python homelab.py --help` for the full list.

Language: every user-facing string lives in STRINGS so a later translation is a data change, not a
rewrite. See the Hebrew-ready note in the course plan.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------------------------
# Strings: one place, so a second language is a data change and not a rewrite.
# ---------------------------------------------------------------------------------------------

STRINGS = {
    "en": {
        "header": "homelab {cmd} - {machine}",
        "section.system": "System",
        "section.memory": "Memory",
        "section.tools": "Tools",
        "section.services": "Services and ports",
        "section.tier": "Tier and recommendation",
        "ok": "ok",
        "warn": "warn",
        "fail": "fail",
        "missing": "not found",
        "yes": "yes",
        "no": "no",
        "unknown": "unknown",
        "exposed": "listening on {addr} - reachable by other devices on your network",
        "loopback": "loopback only - not reachable by other devices",
        "routable": "reachable from your router; this is the one to fix",
        "foot": "Numbers here come from this machine, not from the course. See references/benchmarks.md.",
    },
}


def t(key: str, lang: str = "en", **kw) -> str:
    table = STRINGS.get(lang, STRINGS["en"])
    return table.get(key, key).format(**kw)


# ---------------------------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------------------------

IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
GB = 1024 ** 3


def run(cmd: list[str], timeout: int = 10) -> tuple[int, str]:
    """Run a command, return (exit code, combined output). Never raises."""
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            shell=IS_WINDOWS and not cmd[0].endswith(".exe"),
        )
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return 127, str(e)


@dataclass
class Check:
    name: str
    status: str  # ok | warn | fail | missing
    detail: str = ""


@dataclass
class Report:
    checks: list[Check] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.checks.append(Check(name, status, detail))

    def render(self, cmd: str) -> str:
        out: list[str] = []
        out.append("=" * 74)
        out.append(t("header", cmd=cmd, machine=platform.node() or "this machine"))
        out.append("=" * 74)
        width = max((len(c.name) for c in self.checks), default=10)
        section = ""
        for c in self.checks:
            if c.name.startswith("section."):
                section = t(c.name)
                out.append("")
                out.append(section)
                out.append("-" * len(section))
                continue
            mark = {"ok": "ok  ", "warn": "WARN", "fail": "FAIL", "missing": "--  "}[c.status]
            name = c.name
            pad = " " * max(0, width - len(name))
            line = f"  {mark}  {name}{pad}"
            if c.detail:
                line += f"  {c.detail}"
            out.append(line)
        out.append("")
        return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------------------------


def total_ram_bytes() -> int:
    if IS_WINDOWS:
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            st = MEMORYSTATUSEX()
            st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
            return int(st.ullTotalPhys)
        except Exception:
            pass
    try:
        if sys.platform.startswith("linux"):
            pages = os.sysconf("SC_PHYS_PAGES")
            size = os.sysconf("SC_PAGE_SIZE")
            return int(pages * size)
        if IS_MAC:
            rc, out = run(["sysctl", "-n", "hw.memsize"])
            if rc == 0 and out.strip().isdigit():
                return int(out.strip())
    except (ValueError, OSError):
        pass
    return 0


def available_ram_bytes() -> int:
    try:
        if sys.platform.startswith("linux"):
            info = {}
            with open("/proc/meminfo", encoding="utf-8") as fh:
                for line in fh:
                    key, _, rest = line.partition(":")
                    info[key] = int(rest.strip().split()[0]) * 1024
            return int(info.get("MemAvailable", info.get("MemFree", 0)))
    except OSError:
        pass
    try:
        if IS_MAC:
            rc, out = run(["vm_stat"])
            if rc == 0:
                page = 4096
                free = 0
                for line in out.splitlines():
                    if line.startswith(("Pages free", "Pages inactive", "Pages speculative")):
                        m = re.search(r"(\d+)", line)
                        if m:
                            free += int(m.group(1))
                return free * page
    except OSError:
        pass
    if IS_WINDOWS:
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            st = MEMORYSTATUSEX()
            st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
            return int(st.ullAvailPhys)
        except Exception:
            pass
    return 0


def ram_module_info() -> str:
    """Best effort: how many physical RAM sticks, and whether that means dual channel.

    There is no portable way to ask. Linux can often see it; macOS cannot from the shell at all.
    Say "unknown" rather than guess - a wrong channel count wrecks the bandwidth estimate.
    """
    if IS_MAC or IS_WINDOWS:
        return t("unknown")
    try:
        out = Path("/sys/devices/virtual/dmi/id").read_text(encoding="utf-8", errors="ignore")
        del out
    except OSError:
        pass
    try:
        rc, so = run(["lshw", "-class", "memory", "-short"])
        if rc == 0:
            banks = len(re.findall(r"^\s*bank\s+\d+", so, re.M))
            if banks:
                return f"{banks} bank(s) reported by lshw - confirm against your motherboard"
    except OSError:
        pass
    try:
        rc, so = run(["dmidecode", "-t", "memory"])
        if rc == 0:
            devices = len(re.findall(r"Size:\s+\d+\s+[MG]B", so))
            if devices:
                return f"{devices} populated DIMM slot(s) (dmidecode)"
    except OSError:
        pass
    return t("unknown")


def disk_free_bytes(path: str) -> int:
    try:
        return shutil.disk_usage(path).free
    except OSError:
        return 0


def docker_info() -> tuple[str, str]:
    if not shutil.which("docker"):
        return ("missing", "docker not on PATH")
    rc, out = run(["docker", "version", "--format", "{{.Server.Version}}"], timeout=15)
    if rc != 0:
        return ("warn", "docker CLI present but the daemon is not answering")
    rc2, out2 = run(["docker", "compose", "version", "--short"], timeout=15)
    compose = out2.strip() if rc2 == 0 else "compose v2 plugin missing"
    return ("ok", f"server {out.strip()}, {compose}")


def http_get_json(url: str, timeout: float = 3.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310 - fixed local URLs
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def tcp_open(host: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# The default Wyoming ports. They are only published by the satellite running on the host; the
# services themselves live on the internal Docker network and expose no host port at all.
STACK_PORTS = {
    11434: "Ollama",
    8080: "Open WebUI",
    8123: "Home Assistant",
    6333: "Qdrant",
    10200: "Wyoming wake word",
    10300: "Wyoming speech-to-text",
    10301: "Wyoming text-to-speech",
    10302: "Wyoming satellite",
    10303: "Wyoming speech-to-phrase",
}


def check_bind(port: int, label: str, rep: Report) -> None:
    """The rule that matters most: is this port reachable from off this machine?"""
    loop = tcp_open("127.0.0.1", port)
    if not loop:
        rep.add(f"port {port} ({label})", "missing", "not listening")
        return
    routable = False
    addrs: list[str] = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127."):
                continue
            if tcp_open(ip, port):
                routable = True
                addrs.append(ip)
    except OSError:
        pass
    if routable:
        rep.add(
            f"port {port} ({label})",
            "fail",
            t("routable") + (f" on {', '.join(addrs)}" if addrs else ""),
        )
    else:
        rep.add(f"port {port} ({label})", "ok", t("loopback"))


def microphone_present() -> tuple[str, str]:
    if IS_MAC:
        return ("ok", "system audio present (macOS asks per app; not verified by us)")
    if sys.platform.startswith("linux"):
        if not shutil.which("pactl") and not shutil.which("wpctl"):
            return ("warn", "no pactl/wpctl found; is PipeWire or PulseAudio running?")
        tool = "pactl" if shutil.which("pactl") else "wpctl"
        args = ["pactl", "list", "short", "sources"] if tool == "pactl" else ["wpctl", "list", "Devices"]
        rc, out = run(args)
        if rc == 0 and out.strip():
            return ("ok", f"{tool} reports at least one input device")
        return ("warn", f"{tool} ran but reported no input devices")
    if IS_WINDOWS:
        try:
            import ctypes

            # waveInGetNumDevs: number of recording devices the driver exposes.
            n = ctypes.windll.winmm.waveInGetNumDevs()
            if n > 0:
                return ("ok", f"{n} recording device(s) reported by the audio driver")
            return ("warn", "the audio driver reports no recording devices")
        except Exception:
            return ("warn", "could not query recording devices")
    return ("warn", t("unknown"))


def tier_for(ram_gb: float, cores: int) -> tuple[str, str, str]:
    """(tier, recommended chat model, why). Deliberately conservative about tier B."""
    if ram_gb >= 24 and cores >= 8:
        return (
            "B",
            "qwen3:4b",
            "32 GB class: you can try a 7-8B if your bandwidth supports it. Start at 4B and "
            "measure before you go bigger.",
        )
    if ram_gb >= 12:
        return (
            "A",
            "qwen3:4b",
            "16 GB class: 3-4B chat plus an embedder and the voice services, with headroom. "
            "An 8B will run and will be slow.",
        )
    if ram_gb >= 6:
        return (
            "C",
            "llama3.2:1b",
            "8 GB class: stay small. Use Speech-to-Phrase or Whisper tiny for voice, and do not "
            "run a vector store and a chat model at the same time.",
        )
    return (
        "C-",
        "gemma3:1b",
        "under 8 GB: this course will be tight. Lessons still work, but expect a 1B model and "
        "nothing else loaded at once.",
    )


def cmd_doctor(args: argparse.Namespace) -> int:
    rep = Report()

    rep.add("section.system", "ok")
    osname = platform.system() + " " + platform.release()
    rep.add("operating system", "ok", osname)
    machine = platform.machine()
    rep.add("architecture", "ok", machine)
    note = "macOS steps are not verified by us in this course" if IS_MAC else ""
    rep.add("python", "ok", f"{platform.python_version()} (needs 3.10+)" + (f"; {note}" if note else ""))
    if IS_WINDOWS:
        try:
            ctypes.windll.shell32.SetProcessDpiAwareness(1)
        except Exception:
            pass

    cpu = ""
    try:
        if sys.platform.startswith("linux"):
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
                if line.lower().startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
        elif IS_MAC:
            rc, out = run(["sysctl", "-n", "machdep.cpu.brand_string"])
            cpu = out.strip() if rc == 0 else ""
        elif IS_WINDOWS:
            env = {k: v for k, v in os.environ.items()}
            del env
    except OSError:
        pass
    if not cpu and IS_WINDOWS:
        for probe in (
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Processor | Select-Object -First 1).Name"],
            ["powershell", "-NoProfile", "-Command", "$env:PROCESSOR_IDENTIFIER"],
        ):
            rc, out = run(probe)
            # PowerShell writes progress and error text to the same streams; keep the last
            # line that looks like a model name and ignore the rest.
            for line in reversed(out.splitlines()):
                line = line.strip()
                if line and " " in line and not line.startswith((
                    "At line", "+ ", "CategoryInfo", "FullyQualifiedErrorId", "Get-CimInstance"
                )):
                    cpu = line
                    break
            if cpu:
                break
        if not cpu and "PROCESSOR_IDENTIFIER" in os.environ:
            cpu = os.environ["PROCESSOR_IDENTIFIER"]
    rep.add("cpu", "ok" if cpu else "missing", cpu or "could not read the CPU model")

    cores = os.cpu_count() or 0
    phys = cores
    try:
        if sys.platform.startswith("linux"):
            rc, out = run(["nproc"])
            if rc == 0 and out.strip().isdigit():
                phys = int(out.strip())
    except OSError:
        pass
    rep.add("logical cores", "ok", f"{phys} logical")

    rep.add("section.memory", "ok")
    total = total_ram_bytes()
    avail = available_ram_bytes()
    if total:
        rep.add("total ram", "ok", f"{total / GB:.1f} GB")
        rep.add("available ram", "ok", f"{avail / GB:.1f} GB free right now")
    else:
        rep.add("total ram", "warn", t("unknown"))
    rep.add("memory channels", "warn" if ram_module_info() == t("unknown") else "ok", ram_module_info())
    free_disk = disk_free_bytes(str(Path.home()))
    if free_disk:
        status = "ok" if free_disk > 10 * GB else "warn"
        rep.add("free disk (home)", status, f"{free_disk / GB:.1f} GB")

    rep.add("section.tools", "ok")
    d_status, d_detail = docker_info()
    rep.add("docker + compose", d_status, d_detail)

    if shutil.which("ollama"):
        rc, out = run(["ollama", "--version"])
        rep.add("ollama cli", "ok", out.strip() or "present")
    else:
        rep.add("ollama cli", "missing", "not on PATH (Module 1 installs it)")

    if shutil.which("llama-bench"):
        rep.add("llama-bench", "ok", "present - Module 2 can cross-check against it")
    else:
        rep.add("llama-bench", "missing", "not on PATH - optional, doctor still works")

    m_status, m_detail = microphone_present()
    rep.add("microphone", m_status, m_detail)

    rep.add("section.services", "ok")
    if http_get_json("http://127.0.0.1:11434/api/version"):
        rep.add("ollama api", "ok", "answering on 127.0.0.1:11434")
    elif tcp_open("127.0.0.1", 11434):
        rep.add("ollama api", "warn", "port is open but /api/version did not answer")
    else:
        rep.add("ollama api", "missing", "not running (fine before Module 1)")

    for port, label in STACK_PORTS.items():
        check_bind(port, label, rep)

    rep.add("section.tier", "ok")
    ram_gb = (total or 0) / GB
    tier, model, why = tier_for(ram_gb, phys)
    rep.add("tier", "ok", f"{tier}")
    rep.add("recommended first model", "ok", model)
    rep.add("why", "ok", why)
    if tier in ("C", "C-") and not args.force:
        rep.add("next step", "warn", "reduced path: read the tier C notes in each lesson first")

    print(rep.render("doctor"))
    if args.verbose:
        print("  detail: " + json.dumps(rep.extra, indent=2, sort_keys=True))
    print("  " + t("foot"))
    print()
    return 0


# ---------------------------------------------------------------------------------------------
# bench
# ---------------------------------------------------------------------------------------------


def ollama_chat(base: str, model: str, prompt: str, num_predict: int = 64, stream: bool = True):
    """Stream a chat completion, returning (ttft_seconds, total_seconds, reply_text)."""
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
            "options": {"num_predict": num_predict, "temperature": 0},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/chat", data=body, headers={"Content-Type": "application/json"}
    )
    start = time.perf_counter()
    first = None
    text: list[str] = []
    with urllib.request.urlopen(req, timeout=600) as r:  # noqa: S310 - fixed local URL
        if not stream:
            data = json.loads(r.read().decode("utf-8"))
            return time.perf_counter() - start, time.perf_counter() - start, data.get("message", {}).get("content", "")
        for raw in r:
            if not raw.strip():
                continue
            chunk = json.loads(raw.decode("utf-8"))
            piece = chunk.get("message", {}).get("content", "")
            if piece:
                if first is None:
                    first = time.perf_counter()
                text.append(piece)
            if chunk.get("done"):
                break
    end = time.perf_counter()
    ttft = (first or end) - start
    return ttft, end - start, "".join(text)


def prompt_tokens(reply_text: str) -> int:
    """Rough token count. Good enough for a ratio; not a substitute for the model's own count."""
    return max(1, len(reply_text) // 4)


def peak_rss_of(children: list[str]) -> float:
    """Peak resident memory of the named processes, in GB. Best effort by platform."""
    pids: list[str] = []
    for name in children:
        if not shutil.which(name):
            continue
        if IS_WINDOWS:
            rc, out = run(["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/FO", "CSV", "/NH"])
            for line in out.splitlines():
                parts = [p.strip('" ') for p in line.split('","')]
                if len(parts) > 4 and parts[0].lower() == name.lower() and parts[4].isdigit():
                    pids.append(parts[4])
        else:
            rc, out = run(["pgrep", "-x", name])
            pids.extend(p for p in out.split() if p.strip().isdigit())
    if not pids:
        return 0.0
    total_kb = 0.0
    for pid in pids:
        try:
            if sys.platform.startswith("linux"):
                for line in Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines():
                    if line.startswith("VmHWM:"):
                        total_kb += float(line.split()[1])
                        break
            elif IS_MAC:
                rc, out = run(["ps", "-o", "rss=", "-p", pid])
                if rc == 0 and out.strip().isdigit():
                    total_kb += float(out.strip())
        except (OSError, ValueError):
            continue
    if not total_kb and IS_WINDOWS:
        return 0.0
    return total_kb / (1024 * 1024)


def wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as w:
            return w.getnframes() / float(w.getframerate() or 1)
    except (OSError, wave.Error):
        return 0.0


def load_env(path: Path) -> dict:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def find_env(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    here = Path.cwd() / ".env"
    if here.exists():
        return here
    return Path(__file__).resolve().parent / ".env"


def cmd_bench(args: argparse.Namespace) -> int:
    env_path = find_env(args.env)
    env = load_env(env_path)
    base = args.base or os.environ.get("OLLAMA_HOST_URL") or "http://127.0.0.1:11434"
    model = args.model or env.get("CHAT_MODEL", "qwen3:4b")
    verbose = args.verbose

    print("=" * 74)
    print(f"homelab bench - {platform.node() or 'this machine'}")
    print("=" * 74)
    print(f"  .env            {env_path}{'' if env_path.exists() else '   (not found; using defaults)'}")
    print(f"  model server    {base}")
    print(f"  model           {model}")
    print(f"  python          {platform.python_version()}")
    print()

    version = http_get_json(f"{base}/api/version")
    if not version:
        print("  FAIL  the model server is not answering on " + base)
        print("        Start it, or point --base at the right host, then run this again.")
        print("        Lessons: 03 for a native Ollama, 12 for the Compose stack.")
        return 2
    print(f"  ok    server {version.get('version', 'unknown version')}")
    print()

    # ---- chat: one short prompt, one long prompt ----------------------------------------------------------------
    short_prompt = "In one sentence, what does a CPU do?"
    long_prompt = ("Summarise this in one sentence: " + ("A home AI stack runs a model server, "
                    "a chat interface and a vector store on one machine. " * 120))

    results = []
    for label, prompt, n in (("short prompt", short_prompt, 64), ("long prompt", long_prompt, 64)):
        print(f"  running: {label} ({len(prompt)} chars, {len(prompt) // 4} approx tokens) ...")
        try:
            ttft, total, reply = ollama_chat(base, model, prompt, num_predict=n)
        except (urllib.error.URLError, OSError, ValueError, TimeoutError) as e:
            print(f"  FAIL  {e}")
            return 2
        gen = prompt_tokens(reply)
        gen_rate = gen / total if total > 0 and gen else 0.0
        prompt_tok = len(prompt) // 4
        prompt_rate = prompt_tok / ttft if ttft > 0 else 0.0
        results.append((label, prompt_tok, ttft, gen, total, gen_rate, prompt_rate))
        print(f"          first token {ttft:.2f}s | {gen} tokens in {total:.2f}s "
              f"= {gen_rate:.2f} tok/s generation")
        print(f"          prompt throughput ~{prompt_rate:.0f} tok/s (approximate)")
        if verbose:
            print("          reply: " + reply[:160].replace("\n", " "))
        print()

    # ---- memory ----------------------------------------------------------------------------------
    rss = peak_rss_of(["ollama", "llama-server", "ollama_llama_server"])
    print("  memory")
    if rss:
        print(f"    peak resident set of the model process: {rss:.2f} GB")
    else:
        print("    peak resident set: not measurable on this platform from a script")
        print("    watch it yourself: 'ps -o rss= -C ollama' (Linux/macOS) or Task Manager (Windows)")
    total_ram = total_ram_bytes()
    if total_ram:
        print(f"    of {total_ram / GB:.1f} GB total, {total_ram / GB - rss:.1f} GB is not the model"
              if rss else f"    total {total_ram / GB:.1f} GB")
    print()

    # ---- comparison table ------------------------------------------------------------------------
    print("  your numbers (copy these into templates/measure-yours.md)")
    print(f"    {'run':<14}{'prompt tok':>11}{'gen tok/s':>12}{'prompt tok/s':>15}{'TTFT s':>9}")
    for label, ptok, ttft, gen, _total, grate, prate in results:
        print(f"    {label:<14}{ptok:>11}{grate:>12.2f}{prate:>15.0f}{ttft:>9.2f}")
    print()
    print("    Prediction to check next lesson: bandwidth / model size, times an efficiency factor.")
    print("    If your measurement is far from that, the gap is the lesson, not a defect.")
    print()

    # ---- voice -----------------------------------------------------------------------------------
    if not args.models_only:
        cmd_bench_voice(args, env)

    return 0


def cmd_bench_voice(args: argparse.Namespace, env: dict) -> None:
    samples = Path(__file__).resolve().parent / "samples" / "en" / "commands"
    print("  voice")
    if not samples.exists():
        print("    no sample audio found. The WAV files are generated, not shipped:")
        print("      python homelab.py make-samples")
        print("    Every voice lab also works from a WAV you record yourself.")
        print()
        return
    wavs = sorted(samples.glob("*.wav"))
    if not wavs:
        print("    the sample folder is empty - run: python homelab.py make-samples")
        print()
        return
    print(f"    {len(wavs)} sample command(s) in {samples.name}/")
    for w in wavs:
        dur = wav_duration(w)
        sidecar = w.with_suffix(".txt")
        transcript = sidecar.read_text(encoding="utf-8").strip() if sidecar.exists() else "(no transcript)"
        print(f"    {w.name:<28} {dur:5.2f}s   {transcript}")
    stt = env.get("STT_MODEL", "base")
    print(f"    speech-to-text model: {stt} (see Module 8 for the timings on your machine)")
    print("    Measure the real pipeline with the Assist timing helper:")
    print("      docker compose --profile voice logs -f homeassistant | grep -i latency")
    print()


# ---------------------------------------------------------------------------------------------
# make-samples
# ---------------------------------------------------------------------------------------------


def cmd_make_samples(args: argparse.Namespace) -> int:
    """Generate short placeholder WAVs so every voice lab can run before you record anything.

    These are tones, not speech: they prove the plumbing (file found, length read, service fed)
    without pretending to be a voice dataset. Record your own with any phone or voice recorder,
    16 kHz mono WAV, and put it in the same folder.
    """
    import math
    import struct

    out = Path(__file__).resolve().parent / "samples" / "en" / "commands"
    out.mkdir(parents=True, exist_ok=True)
    phrases = [
        ("turn-on-kitchen-light", "turn on the kitchen light"),
        ("what-is-the-temperature", "what is the temperature in the living room"),
        ("set-a-timer", "set a timer for five minutes"),
        ("good-night", "good night"),
    ]
    rate = 16000
    made = 0
    for slug, phrase in phrases:
        wav = out / f"{slug}.wav"
        if wav.exists() and not args.force:
            print(f"  keep   {wav.name}")
            continue
        seconds = 1.2 + 0.08 * len(phrase)
        n = int(rate * seconds)
        frames = bytearray()
        for i in range(n):
            # A placeholder "speech-like" sweep, not speech.
            env = math.sin(math.pi * i / n) ** 2
            f = 140 + 90 * math.sin(2 * math.pi * 3 * i / rate)
            frames += struct.pack("<h", int(12000 * env * math.sin(2 * math.pi * f * i / rate)))
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(bytes(frames))
        (out / f"{slug}.txt").write_text(phrase + "\n", encoding="utf-8")
        made += 1
        print(f"  write  {wav.name}  ({seconds:.1f}s placeholder tone)")
    print()
    print(f"{made} file(s) written to {out}")
    print("These are tones, not words. They prove the plumbing only.")
    print("Record your own 16 kHz mono WAVs and drop them in the same folder to test accuracy.")
    return 0


# ---------------------------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="homelab.py",
        description="doctor and bench for the Private Home AI course. Reads only; changes nothing.",
    )
    p.add_argument("--version", action="version", version="homelab.py 1.0 (course build 2026-09-30)")
    sub = p.add_subparsers(dest="cmd")

    d = sub.add_parser("doctor", help="classify this machine, check the stack, recommend a model")
    d.add_argument("--verbose", action="store_true", help="also print collected values as JSON")
    d.add_argument("--force", action="store_true", help="do not warn about a small machine")
    d.set_defaults(func=cmd_doctor)

    b = sub.add_parser("bench", help="measure prompt and generation speed, peak RAM, voice samples")
    b.add_argument("--model", help="override the chat model (default: CHAT_MODEL from .env)")
    b.add_argument("--base", help="model server base URL (default: http://127.0.0.1:11434)")
    b.add_argument("--env", help="path to .env (default: ./.env, else next to this script)")
    b.add_argument("--models-only", action="store_true", help="skip the voice section")
    b.add_argument("--verbose", action="store_true", help="print the replies too")
    b.set_defaults(func=cmd_bench)

    m = sub.add_parser("make-samples", help="generate placeholder WAVs so voice labs can run")
    m.add_argument("--force", action="store_true", help="overwrite existing files")
    m.set_defaults(func=cmd_make_samples)

    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        print()
        print("Start with:  python homelab.py doctor")
        return 0
    try:
        return int(args.func(args) or 0)
    except KeyboardInterrupt:
        print("\ninterrupted")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
