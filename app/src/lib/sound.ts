import type { SoundDef } from "../types";

export function clampVolume(v: number) { return Math.max(0, Math.min(1, v)); }
export function fadeSteps(from: number, to: number, steps: number) {
  const n = Math.max(1, steps);
  const out: number[] = [];
  for (let i = 1; i <= n; i++) out.push(from + ((to - from) * i) / n);
  return out;
}
export function resolveSound(id: string, defs: SoundDef[]) {
  return defs.find((d) => d.id === id) ?? null;
}

function noiseBuffer(ctx: AudioContext, color: string) {
  const len = ctx.sampleRate * 2;
  const buf = ctx.createBuffer(1, len, ctx.sampleRate);
  const d = buf.getChannelData(0);
  let last = 0;
  let b0 = 0, b1 = 0, b2 = 0;
  for (let i = 0; i < len; i++) {
    const white = Math.random() * 2 - 1;
    if (color === "brown") { last = (last + 0.02 * white) / 1.02; d[i] = last * 3.5; }
    else if (color === "pink") { b0 = 0.99765 * b0 + white * 0.099; b1 = 0.963 * b1 + white * 0.2965; b2 = 0.57 * b2 + white * 1.0526; d[i] = (b0 + b1 + b2 + white * 0.1848) * 0.2; }
    else d[i] = white * 0.4;
  }
  return buf;
}

export function createSoundEngine() {
  let ctx: AudioContext | null = null;
  let master: GainNode | null = null;
  let nodes: AudioScheduledSourceNode[] = [];
  let timer: number | null = null;

  function ensure() {
    if (!ctx) {
      ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      master = ctx.createGain();
      master.gain.value = 0;
      master.connect(ctx.destination);
    }
    return ctx!;
  }

  function stopNodes() {
    nodes.forEach((n) => { try { n.stop(); } catch {} });
    nodes = [];
  }

  function rainBuffer(ctx: AudioContext) {
    const len = ctx.sampleRate * 4;
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = buf.getChannelData(0);
    const dropsPerSec = 120;
    const total = Math.floor((dropsPerSec * len) / ctx.sampleRate);
    for (let k = 0; k < total; k++) {
      const pos = Math.floor(Math.random() * len);
      const dur = Math.floor(ctx.sampleRate * (0.008 + Math.random() * 0.022));
      const freq = 2000 + Math.random() * 4000;
      const amp = 0.3 + Math.random() * 0.7;
      for (let i = 0; i < dur && pos + i < len; i++) {
        const t = i / ctx.sampleRate;
        const env = Math.exp(-t / 0.02);
        d[pos + i] += amp * env * Math.sin(2 * Math.PI * freq * t);
      }
    }
    for (let i = 0; i < len; i++) if (d[i] > 1) d[i] = 1; else if (d[i] < -1) d[i] = -1;
    return buf;
  }

  function crackleBuffer(ctx: AudioContext) {
    const len = ctx.sampleRate * 6;
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = buf.getChannelData(0);
    const eventsPerSec = 9;
    const total = Math.floor((eventsPerSec * len) / ctx.sampleRate);
    for (let k = 0; k < total; k++) {
      const pos = Math.floor(Math.random() * len);
      const dur = Math.floor(ctx.sampleRate * (0.04 + Math.random() * 0.11));
      const freq = 300 + Math.random() * 600;
      const amp = 0.3 + Math.random() * 0.7;
      const decay = 0.04 + Math.random() * 0.08;
      for (let i = 0; i < dur && pos + i < len; i++) {
        const t = i / ctx.sampleRate;
        const env = Math.exp(-t / decay);
        d[pos + i] += amp * env * (Math.sin(2 * Math.PI * freq * t) + (Math.random() * 2 - 1) * 0.5);
      }
    }
    const bigPerSec = 1.5;
    const bigTotal = Math.floor((bigPerSec * len) / ctx.sampleRate);
    for (let k = 0; k < bigTotal; k++) {
      const pos = Math.floor(Math.random() * len);
      const dur = Math.floor(ctx.sampleRate * (0.2 + Math.random() * 0.2));
      const freq = 150 + Math.random() * 250;
      for (let i = 0; i < dur && pos + i < len; i++) {
        const t = i / ctx.sampleRate;
        const env = Math.exp(-t / 0.12);
        d[pos + i] += 0.9 * env * (Math.random() * 2 - 1) * Math.sin(2 * Math.PI * freq * t);
      }
    }
    for (let i = 0; i < len; i++) if (d[i] > 1) d[i] = 1; else if (d[i] < -1) d[i] = -1;
    return buf;
  }

  function play(def: SoundDef, volume = 0.6) {
    const c = ensure();
    if (c.state === "suspended") c.resume();
    stopNodes();
    const p = def.params as any;

    if (def.type === "rain") {
      const bg = c.createBufferSource();
      bg.buffer = noiseBuffer(c, (p.color as string) || "pink");
      bg.loop = true;
      const bgGain = c.createGain(); bgGain.gain.value = 0.3;
      const bgFilter = c.createBiquadFilter(); bgFilter.type = "lowpass"; bgFilter.frequency.value = 1200;
      bg.connect(bgFilter); bgFilter.connect(bgGain); bgGain.connect(master!);

      const drops = c.createBufferSource();
      drops.buffer = rainBuffer(c);
      drops.loop = true;
      const hp = c.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 1800;
      const dropsGain = c.createGain(); dropsGain.gain.value = 0.7;
      drops.connect(hp); hp.connect(dropsGain); dropsGain.connect(master!);

      const lfo = c.createOscillator();
      const lfoDepth = c.createGain();
      lfo.frequency.value = 0.05;
      lfoDepth.gain.value = 0.4;
      lfo.connect(lfoDepth); lfoDepth.connect(dropsGain.gain);
      lfo.start();

      bg.start(); drops.start();
      nodes.push(bg, drops, lfo);
      fade(volume, 600);
      return;
    }

    if (def.type === "crackle") {
      const crk = c.createBufferSource();
      crk.buffer = crackleBuffer(c);
      crk.loop = true;
      const bp = c.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 500; bp.Q.value = 0.7;
      const crkGain = c.createGain(); crkGain.gain.value = 0.8;
      crk.connect(bp); bp.connect(crkGain); crkGain.connect(master!);

      const hum = c.createOscillator();
      hum.frequency.value = 90;
      const humGain = c.createGain(); humGain.gain.value = 0.08;
      hum.connect(humGain); humGain.connect(master!);
      hum.start();

      crk.start();
      nodes.push(crk, hum);
      fade(volume, 600);
      return;
    }

    const color = (p.color as string) || "white";
    const src = c.createBufferSource();
    src.buffer = noiseBuffer(c, color);
    src.loop = true;
    let out: AudioNode = src;
    if (p.filterHz && p.filterHz > 0) {
      const f = c.createBiquadFilter();
      f.type = "lowpass";
      f.frequency.value = p.filterHz;
      out.connect(f); out = f;
    }
    if (def.type === "wave" || def.type === "fan") {
      const lfoGain = c.createGain();
      out.connect(lfoGain);
      const lfo = c.createOscillator();
      const depth = c.createGain();
      lfo.frequency.value = (p.lfoRateHz as number) || 0.2;
      depth.gain.value = (p.lfoDepth as number) || 0.3;
      lfoGain.gain.value = 1 - ((p.lfoDepth as number) || 0.3);
      lfo.connect(depth); depth.connect(lfoGain.gain); lfo.start();
      nodes.push(lfo);
      out = lfoGain;
    }
    if (def.type === "drone") {
      const osc = c.createOscillator();
      osc.frequency.value = (p.baseHz as number) || 110;
      const og = c.createGain(); og.gain.value = 0.2;
      osc.connect(og); og.connect(master!); osc.start(); nodes.push(osc);
    }
    out.connect(master!);
    src.start(); nodes.push(src);
    fade(volume, 600);
  }

  function fade(to: number, ms: number) {
    if (!ctx || !master) return;
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(master.gain.value, ctx.currentTime);
    master.gain.linearRampToValueAtTime(clampVolume(to), ctx.currentTime + ms / 1000);
  }

  function stop(fadeMs = 800) {
    if (!ctx || !master) return;
    fade(0, fadeMs);
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => stopNodes(), fadeMs + 50);
  }

  function timerStop(seconds: number) {
    if (timer) window.clearTimeout(timer);
    timer = window.setTimeout(() => stop(4000), seconds * 1000);
  }

  return { play, stop, fade, timerStop, setVolume: (v: number) => fade(v, 300) };
}
