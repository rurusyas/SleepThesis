import { useEffect, useState } from "react";
import { Page, StatusBar } from "../components/Shell";
import { Icon } from "../components/icons";
import { useStore } from "../store/useStore";
import { api } from "../services/api";

type Row = { user_id: number | string; name: string | null; score: number; me?: boolean };

export default function Leaderboard() {
  const backendUid = useStore((s) => s.backendUid);
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLeaderboard().then((data) => {
      setLoading(false);
      if (Array.isArray(data) && data.length) {
        setRows(data.map((r: any) => ({ ...r, me: backendUid != null && r.user_id === backendUid })));
      }
    }).catch(() => setLoading(false));
  }, [backendUid]);

  const initials = (n: string | null) => (n || "??").split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  const posColor = (i: number) => (i === 0 ? "#FBBF24" : i === 1 ? "#cbd5e1" : "var(--muted)");

  return (
    <Page>
      <StatusBar />
      <div className="scr-h">
        <Icon name="trophy" size={26} style={{ stroke: "var(--teal1)" }} />
        <h2>Лидерборд</h2>
      </div>
      <p className="muted" style={{ fontSize: 11, marginBottom: 14 }}>Очки = среднее качество сна за 7 дней · только в Telegram</p>
      <div className="col" style={{ gap: 9 }}>
        {loading ? (
          [0, 1, 2].map((i) => (
            <div key={i} className="rank" style={{ opacity: 0.5 }}>
              <div className="pos">{i + 1}</div>
              <div className="av">··</div>
              <div style={{ flex: 1 }}><div className="t" style={{ fontSize: 13, fontWeight: 600 }}>—</div></div>
              <div className="mono" style={{ fontWeight: 700 }}>—</div>
            </div>
          ))
        ) : rows.length === 0 ? (
          <div className="card" style={{ padding: 18, textAlign: "center" }}>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 6 }}>Будь первым в лидерборде</div>
            <div className="muted" style={{ fontSize: 12 }}>Заполни дневник сна несколько дней подряд — и попадёшь в топ.</div>
          </div>
        ) : (
          rows.slice(0, 20).map((r, i) => (
            <div key={r.user_id} className={"rank" + (r.me ? " me" : "")}>
              <div className="pos" style={{ color: posColor(i) }}>{i + 1}</div>
              <div className="av">{initials(r.name)}</div>
              <div style={{ flex: 1 }}><div className="t" style={{ fontSize: 13, fontWeight: 600 }}>{r.name || "Без имени"}{r.me ? " · ты" : ""}</div></div>
              <div className="mono" style={{ fontWeight: 700, color: r.me ? "var(--teal1)" : "var(--text)" }}>{r.score}</div>
            </div>
          ))
        )}
      </div>
    </Page>
  );
}
