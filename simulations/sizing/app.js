// Sizing calculator for the Private Home AI course.
//
// One idea: during generation, every new token re-reads the whole model, so speed is bounded by
// memory bandwidth divided by model size. Prompt processing is a different limit (cores, compute),
// and the KV cache is a third thing that grows with context and is paid for on every token.
//
// Everything here is an educational estimate. It has no network access, no storage, and no idea
// what machine you are actually sitting at.

const GB = 1024 ** 3;

// Theoretical peak bytes/second per channel for common DDR generations. Real machines reach roughly
// 70-85% of these; the efficiency factor below carries that uncertainty.
const MEMORY_BW = {
  "d4-3200": { theoretical: 25.6, real: 51 },
  "d4-3600": { theoretical: 28.8, real: 57 },
  "d5-5600": { theoretical: 44.8, real: 89 },
  "d5-6000": { theoretical: 48.0, real: 96 },
  "d5-6400": { theoretical: 51.2, real: 102 },
};

// Apple Silicon: unified memory, and the CPU is not the only consumer of it.
const APPLE_BW = { m1: 68, m2: 89, m3: 100, m4: 120 };

// Bytes of weights per parameter, by quantisation.
const QUANT_BYTES = { q4: 0.55, q5: 0.68, q6: 0.85, q8: 1.06, f16: 2.0 };

const QUANT_LABEL = {
  q4: "Q4_K_M",
  q5: "Q5_K_M",
  q6: "Q6_K",
  q8: "Q8_0",
  f16: "F16",
};

// Rough KV cache cost, in GB, for a 1B model at a given context. Scales roughly linearly with
// parameters and context, and the exact constant depends on the architecture (GQA models use far
// less), so this is deliberately generous for the larger models.
const KV_GB_PER_1B_PER_1K_CTX = { small: 0.008, large: 0.004 };

const SERVICES = [
  { id: "svc-chat", label: "Chat interface", gb: 1.2 },
  { id: "svc-ha", label: "Home Assistant", gb: 1.0 },
  { id: "svc-voice", label: "Voice services", gb: 1.6 },
  { id: "svc-rag", label: "Vector store and embedder", gb: 1.2 },
  { id: "svc-browser", label: "Browser, ten tabs", gb: 1.5 },
  { id: "svc-os", label: "Operating system", gb: 2.5 },
];

const el = (id) => document.getElementById(id);

function readState() {
  const cores = Number(el("cores").value);
  return {
    ram: Number(el("ram").value),
    memory: el("memory").value,
    channels: Number(el("channels").value),
    cores: Number.isFinite(cores) && cores > 0 ? Math.min(64, cores) : 1,
    apple: el("apple").checked,
    params: Number(el("model").value),
    quant: el("quant").value,
    context: Number(el("context").value),
    target: Number(el("target").value),
    services: SERVICES.filter((s) => el(s.id).checked).map((s) => s.label),
  };
}

// Presets arrive as ?preset=... so a lesson can link straight to a worked example.
function applyPreset(name) {
  const presets = {
    "tier-a": { ram: 16, memory: "d5-5600", channels: 2, cores: 8, params: 4, quant: "q4", context: 4096 },
    "one-stick": { ram: 32, memory: "d5-6000", channels: 1, cores: 16, params: 8, quant: "q4", context: 4096 },
    "too-big": { ram: 16, memory: "d4-3200", channels: 1, cores: 4, params: 14, quant: "q8", context: 32768 },
    "voice": { ram: 16, memory: "d5-5600", channels: 2, cores: 8, params: 4, quant: "q4", context: 4096, extra: ["svc-voice", "svc-ha"] },
  };
  const p = presets[name];
  if (!p) return false;
  for (const key of ["ram", "memory", "channels", "cores", "params", "quant", "context"]) {
    if (p[key] === undefined) continue;
    const node = el(key === "params" ? "model" : key);
    if (node) node.value = String(p[key]);
  }
  for (const s of SERVICES) el(s.id).checked = p.extra ? p.extra.includes(s.id) : s.id === "svc-chat" || s.id === "svc-browser" || s.id === "svc-os";
  return true;
}

function usableBandwidth(s) {
  if (s.apple) {
    return APPLE_BW.m3 * (s.channels === 1 ? 0.45 : 1);
  }
  const per = MEMORY_BW[s.memory];
  if (!per) return 0;
  // Two sticks in the right slots give roughly the full per-pin rate; one stick gives about half
  // on consumer boards, because only one 64-bit memory channel is populated.
  return s.channels === 1 ? per.theoretical : per.real;
}

function compute(s) {
  const weightsGb = s.params * QUANT_BYTES[s.quant];
  const kvPer1B = s.params >= 7 ? KV_GB_PER_1B_PER_1K_CTX.large : KV_GB_PER_1B_PER_1K_CTX.small;
  const kvGb = kvPer1B * s.params * (s.context / 1024);
  const runtimeOverhead = 0.5; // allocator, compute buffers, the server process itself
  const modelTotal = weightsGb + kvGb + runtimeOverhead;

  const servicesGb = SERVICES.filter((x) => s.services.includes(x.label)).reduce((a, x) => a + x.gb, 0);
  const totalGb = modelTotal + servicesGb;
  const headroomGb = s.ram - totalGb;

  const bwGBs = usableBandwidth(s);
  const bwBytes = bwGBs * GB;
  // Efficiency: the share of theoretical bandwidth a memory-bound generation loop actually gets.
  // This is the number the lesson asks you to argue about, so it is a range, not a constant.
  const efficiency = s.apple ? 0.62 : 0.55;
  const genTps = (bwBytes * efficiency) / (weightsGb * GB);

  // Prompt processing is compute-bound and scales with cores until memory bandwidth bites.
  // A deliberately coarse shape: it rises with cores and falls with model size.
  const promptTps = Math.max(1, (s.cores * 9) / Math.sqrt(s.params * QUANT_BYTES[s.quant]));

  return { weightsGb, kvGb, runtimeOverhead, modelTotal, servicesGb, totalGb, headroomGb, bwGBs, genTps, promptTps };
}

function render() {
  const s = readState();
  const r = compute(s);

  // ---- verdict -------------------------------------------------------------------------------
  const verdict = el("verdict");
  const fits = r.headroomGb >= 0;
  const meetsSpeed = r.genTps >= s.target;
  const spareSpeed = r.genTps / s.target;

  let cls, text;
  if (!fits) {
    cls = "bad";
    text = `Does not fit. It needs ${r.totalGb.toFixed(1)} GB and you have ${s.ram} GB. Whatever you switch off, something still has to give — and swap on a home machine means roughly a hundred times slower, not slightly slower.`;
  } else if (!meetsSpeed) {
    cls = "warn";
    text = `Fits, with ${r.headroomGb.toFixed(1)} GB to spare — but ${r.genTps.toFixed(1)} tok/s is under your ${s.target} tok/s target. It will work and it will feel slow.`;
  } else if (spareSpeed > 2.5) {
    cls = "good";
    text = `Fits with ${r.headroomGb.toFixed(1)} GB to spare and is well past your target. You could go up a size: try the next model up in the list and check whether it still fits.`;
  } else {
    cls = "good";
    text = `Fits with ${r.headroomGb.toFixed(1)} GB to spare and clears your ${s.target} tok/s target. This is the pick.`;
  }
  verdict.className = `verdict ${cls}`;
  verdict.textContent = text;

  // ---- speed ---------------------------------------------------------------------------------
  el("speed-line").innerHTML = "";
  el("speed-line").append(
    document.createTextNode(`${r.genTps.toFixed(1)} tokens/second `),
    Object.assign(document.createElement("span"), { className: "unit", textContent: ` predicted generation · about ${r.promptTps.toFixed(0)} tokens/second prompt processing` })
  );

  const scaleMax = Math.max(30, Math.ceil(r.genTps * 1.2));
  const fill = el("bar-fill");
  fill.style.width = `${Math.min(100, (r.genTps / scaleMax) * 100)}%`;
  fill.className = r.genTps >= s.target ? "bar-fill" : "bar-fill over";
  el("bar-target").style.left = `${(s.target / scaleMax) * 100}%`;
  el("bar-label").textContent = `The vertical line is your ${s.target} tok/s target. Scale 0 to ${scaleMax} tokens/second.`;

  // ---- bill ---------------------------------------------------------------------------------
  const tbody = el("bill").querySelector("tbody");
  tbody.replaceChildren();

  const rows = [
    ["Model weights on disk", r.weightsGb, `${s.params}B at ${QUANT_LABEL[s.quant]}`],
    ["KV cache", r.kvGb, `grows with context: ${s.context.toLocaleString("en-GB")} tokens`],
    ["Runtime overhead", r.runtimeOverhead, "server process, buffers, allocator"],
  ];
  for (const label of s.services) {
    const svc = SERVICES.find((x) => x.label === label);
    rows.push([label, svc.gb, "sharing the same RAM"]);
  }

  for (const [name, gb, why] of rows) {
    const tr = document.createElement("tr");
    const tdName = document.createElement("td");
    tdName.textContent = name;
    const tdGb = document.createElement("td");
    tdGb.textContent = gb.toFixed(2);
    const tdWhy = document.createElement("td");
    const span = document.createElement("span");
    span.className = "why";
    span.textContent = why;
    tdWhy.append(span);
    tr.append(tdName, tdGb, tdWhy);
    if (!fits && name === "Model weights on disk") tr.className = "hot";
    tbody.append(tr);
  }

  el("bill-total").textContent = `${r.totalGb.toFixed(1)} GB`;
  el("bill-head").textContent =
    r.headroomGb >= 0
      ? `${r.headroomGb.toFixed(1)} GB headroom on ${s.ram} GB`
      : `${Math.abs(r.headroomGb).toFixed(1)} GB over on ${s.ram} GB`;

  // ---- why ----------------------------------------------------------------------------------
  const channelNote = s.channels === 1 ? "One stick, so about half the bandwidth — this is the single most common reason a machine feels slow." : "";
  el("why").textContent =
    `Predicted generation speed = usable memory bandwidth ÷ model size. Here that is ${r.bwGBs.toFixed(0)} GB/s ÷ ${r.weightsGb.toFixed(2)} GB, times an efficiency factor of ${s.apple ? 0.62 : 0.55}. ` +
    `Prompt processing is a different limit — it scales with cores, which is why ${s.cores} cores is what it is. ` +
    `The KV cache is the part people forget: it is paid on every single token, so a ${s.context.toLocaleString("en-GB")}-token context costs you even when you only ask a short question.` +
    (channelNote ? ` ${channelNote}` : "");
}

function init() {
  // ?preset=... is read without any side effects; there is no storage and no navigation.
  let preset = "";
  try {
    preset = new URLSearchParams(window.location.search).get("preset") || "";
  } catch {
    preset = "";
  }
  if (preset) applyPreset(preset);

  const form = el("controls");
  form.addEventListener("input", render);
  form.addEventListener("change", render);
  form.addEventListener("submit", (e) => e.preventDefault());
  render();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
