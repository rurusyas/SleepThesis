import { useEffect, type ReactNode } from "react";
import { HashRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useStore } from "./store/useStore";
import TabBar from "./components/TabBar";
import Home from "./screens/Home";
import Onboarding from "./screens/Onboarding";
import Apnea from "./screens/Apnea";
import Diary from "./screens/Diary";
import Sounds from "./screens/Sounds";
import Alarm from "./screens/Alarm";
import Education from "./screens/Education";
import Chat from "./screens/Chat";
import Focus from "./screens/Focus";
import Leaderboard from "./screens/Leaderboard";
import Profile from "./screens/Profile";
import Routine from "./screens/Routine";

function OnboardingGate({ children }: { children: ReactNode }) {
  const ready = useStore((s) => s.ready);
  const indices = useStore((s) => s.indices);
  const { pathname } = useLocation();
  if (!ready) return null;
  if (indices === null && pathname !== "/onboarding") {
    return <Navigate to="/onboarding" replace />;
  }
  return <>{children}</>;
}

function TabBarMaybe() {
  const indices = useStore((s) => s.indices);
  if (indices === null) return null;
  return <TabBar />;
}

export default function App({ demo = false }: { demo?: boolean }) {
  const init = useStore((s) => s.init);
  useEffect(() => { init(); }, [init]);

  const inner = (
    <div className="app web-app">
      {demo && <div className="island" />}
      <div className="stars" />
      <div className="scroll">
        <OnboardingGate>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/apnea" element={<Apnea />} />
            <Route path="/diary" element={<Diary />} />
            <Route path="/sounds" element={<Sounds />} />
            <Route path="/alarm" element={<Alarm />} />
            <Route path="/education" element={<Education />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/focus" element={<Focus />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/routine" element={<Routine />} />
          </Routes>
        </OnboardingGate>
      </div>
      <TabBarMaybe />
    </div>
  );

  return <HashRouter>{demo ? <div className="stage"><div className="device">{inner}</div></div> : inner}</HashRouter>;
}
