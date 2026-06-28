import { useEffect } from "react";
import { HashRouter, Route, Routes, useNavigate } from "react-router-dom";
import { useStore } from "../../store/useStore";
import TgTabBar from "./TgTabBar";
import TgHome from "./TgHome";
import TgOnboarding from "./TgOnboarding";
import Diary from "../Diary";
import Sounds from "../Sounds";
import Education from "../Education";
import Chat from "../Chat";
import Leaderboard from "../Leaderboard";

function HomeOnMount() {
  const nav = useNavigate();
  useEffect(() => { nav("/", { replace: true }); }, []);
  return null;
}

export default function TelegramApp() {
  const init = useStore((s) => s.init);
  useEffect(() => { init(); }, [init]);

  return (
    <HashRouter>
      <HomeOnMount />
      <div className="app">
        <div className="stars" />
        <div className="scroll">
          <Routes>
            <Route path="/" element={<TgHome />} />
            <Route path="/onboarding" element={<TgOnboarding />} />
            <Route path="/diary" element={<Diary />} />
            <Route path="/sounds" element={<Sounds />} />
            <Route path="/education" element={<Education />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
          </Routes>
        </div>
        <TgTabBar />
      </div>
    </HashRouter>
  );
}
