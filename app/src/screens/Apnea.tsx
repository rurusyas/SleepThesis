import { useEffect, useRef, useState } from "react";
import { Page, ScreenHeader } from "../components/Shell";
import { Icon } from "../components/icons";
import { api } from "../services/api";
import { useStore } from "../store/useStore";

const REC_SECONDS = 30;
type Mode = "idle" | "recording" | "analyzing" | "result" | "error";

function fmt(ts: number) {
  const d = new Date(ts);
  const today = new Date();
  const yesterday = new Date(); yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return "Сегодня";
  if (d.toDateString() === yesterday.toDateString()) return "Вчера";
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
}

function statusFor(conf: number, has: boolean) {
  if (!has) return { tone: "good", label: "Норма", desc: "пауз дыхания не выявлено" };
  if (conf < 0.4) return { tone: "warn", label: "Лёгкие признаки", desc: "редкие паузы дыхания" };
  return { tone: "bad", label: "Признаки апноэ", desc: "выявлены значимые паузы" };
}

export default function Apnea() {
  const apnea = useStore((s) => s.apnea);
  const addApnea = useStore((s) => s.addApnea);
  const backendUid = useStore((s) => s.backendUid);

  const [mode, setMode] = useState<Mode>("idle");
  const [counter, setCounter] = useState(REC_SECONDS);
  const [result, setResult] = useState<{ has_apnea: boolean; confidence: number; used_model: boolean } | null>(null);
  const [err, setErr] = useState("");

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);

  const supported = typeof navigator !== "undefined" && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== "undefined";

  useEffect(() => () => cleanup(), []);

  function cleanup() {
    if (timerRef.current) { window.clearInterval(timerRef.current); timerRef.current = null; }
    try { recorderRef.current?.stop(); } catch {}
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    recorderRef.current = null;
    chunksRef.current = [];
  }

  async function start() {
    setErr("");
    setResult(null);
    if (!supported) { setErr("Запись недоступна в этом браузере. Открой в Chrome/Safari/Firefox."); setMode("error"); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const rec = new MediaRecorder(stream);
      recorderRef.current = rec;
      chunksRef.current = [];
      rec.ondataavailable = (e) => { if (e.data && e.data.size > 0) chunksRef.current.push(e.data); };
      rec.onstop = onStop;
      rec.start();
      setMode("recording");
      setCounter(REC_SECONDS);
      timerRef.current = window.setInterval(() => {
        setCounter((c) => {
          if (c <= 1) { stop(); return 0; }
          return c - 1;
        });
      }, 1000);
    } catch (e: any) {
      setErr("Не получилось получить доступ к микрофону. Разреши в настройках браузера.");
      setMode("error");
    }
  }

  function stop() {
    if (timerRef.current) { window.clearInterval(timerRef.current); timerRef.current = null; }
    try { recorderRef.current?.stop(); } catch {}
    streamRef.current?.getTracks().forEach((t) => t.stop());
  }

  async function onStop() {
    setMode("analyzing");
    const blob = new Blob(chunksRef.current, { type: chunksRef.current[0]?.type || "audio/webm" });
    chunksRef.current = [];
    try {
      const res = await api.analyzeApnea(blob, backendUid ?? undefined);
      if (!res) {
        setErr("Сервер недоступен. Проверь, что бэкенд запущен.");
        setMode("error");
        return;
      }
      const r = { has_apnea: !!res.has_apnea, confidence: Number(res.confidence) || 0, used_model: !!res.used_model };
      setResult(r);
      await addApnea({ has_apnea: r.has_apnea, confidence: r.confidence, mode: "browser" });
      setMode("result");
    } catch {
      setErr("Не удалось проанализировать. Попробуй ещё раз.");
      setMode("error");
    }
  }

  return (
    <Page>
      <ScreenHeader title="Анализ апноэ" />

      <div className="card" style={{ padding: 20, textAlign: "center", position: "relative", overflow: "hidden" }}>
        {mode === "idle" && (
          <>
            <div className="muted" style={{ fontSize: 11, letterSpacing: ".16em", textTransform: "uppercase" }}>Готов к записи</div>
            <p style={{ fontSize: 13, lineHeight: 1.5, margin: "14px 16px 18px", color: "var(--ice)" }}>
              Поднеси телефон или микрофон ближе ко рту, дыши спокойно {REC_SECONDS} секунд
            </p>
            <button className="btn" onClick={start}><Icon name="mic" size={16} style={{ stroke: "#04122a" }} /> Начать запись</button>
          </>
        )}

        {mode === "recording" && (
          <>
            <div className="breath" style={{ margin: "10px auto" }}>
              <div className="ring glow" />
              <div className="ring a" />
              <div className="ring b" />
              <div className="big" style={{ position: "relative", zIndex: 3 }}>
                <b className="mono">{counter}</b>
                <span>осталось сек</span>
              </div>
            </div>
            <button className="btn ghost" onClick={stop}>Остановить</button>
          </>
        )}

        {mode === "analyzing" && (
          <>
            <div className="breath" style={{ margin: "10px auto" }}>
              <div className="ring glow" />
              <div className="ring a" />
              <div className="ring b" />
              <div className="big" style={{ position: "relative", zIndex: 3 }}>
                <b style={{ fontSize: 17 }}>Анализирую</b>
                <span>аудио</span>
              </div>
            </div>
          </>
        )}

        {mode === "result" && result && (() => {
          const s = statusFor(result.confidence, result.has_apnea);
          const colorMap = { good: "var(--good)", warn: "var(--warn)", bad: "var(--bad)" } as const;
          return (
            <>
              <div className="breath" style={{ margin: "10px auto" }}>
                <div className="ring glow" />
                <div className="ring a" />
                <div className="ring b" />
                <div className="big" style={{ position: "relative", zIndex: 3 }}>
                  <b style={{ color: colorMap[s.tone as keyof typeof colorMap], fontSize: 16, fontWeight: 700 }}>{s.label}</b>
                  <span style={{ fontSize: 12, opacity: 0.85, display: "block", marginTop: 4 }}>{s.desc}</span>
                </div>
              </div>
              <div className="row" style={{ marginTop: 8 }}>
                <div className="stat"><div className="n mono">{Math.round(result.confidence * 100)}%</div><div className="l">уверенность</div></div>
                <div className="stat"><div className="n mono">{result.has_apnea ? "да" : "нет"}</div><div className="l">паузы дыхания</div></div>
              </div>
              {!result.used_model && (
                <div className="muted" style={{ fontSize: 10.5, marginTop: 12, fontStyle: "italic" }}>
                  Демо-режим: эвристика по аудио. Полная модель — в iOS-сборке с Apple HealthKit (SpO2).
                </div>
              )}
              <button className="btn" style={{ marginTop: 12 }} onClick={() => { setMode("idle"); setResult(null); }}>Записать ещё раз</button>
            </>
          );
        })()}

        {mode === "error" && (
          <>
            <div className="muted" style={{ fontSize: 11, letterSpacing: ".16em", textTransform: "uppercase", color: "var(--bad)" }}>Ошибка</div>
            <p style={{ fontSize: 13, lineHeight: 1.5, margin: "14px 16px 18px" }}>{err}</p>
            <button className="btn" onClick={() => { setMode("idle"); setErr(""); }}>Попробовать ещё раз</button>
          </>
        )}
      </div>

      {apnea.length > 0 && (
        <>
          <div className="eyebrow" style={{ margin: "20px 0 10px" }}>История</div>
          <div className="col" style={{ gap: 9 }}>
            {apnea.slice(0, 5).map((r) => {
              const s = statusFor(r.confidence, r.has_apnea);
              const colorMap = { good: "var(--good)", warn: "var(--warn)", bad: "var(--bad)" } as const;
              return (
                <div key={r.id} className="li">
                  <div className="dot" style={{ background: colorMap[s.tone as keyof typeof colorMap], flex: "none" }} />
                  <div style={{ flex: 1 }}>
                    <div className="t">{fmt(r.created_at)} · {s.label.toLowerCase()}</div>
                    <div className="d">{s.desc}</div>
                  </div>
                  <div className="mono muted" style={{ fontSize: 12 }}>{Math.round(r.confidence * 100)}%</div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </Page>
  );
}
