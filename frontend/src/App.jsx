import { useCallback, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import CompanyDetails from "./pages/CompanyDetails";
import TranscriptDetails from "./pages/TranscriptDetails";
import { getCompanies, getHealth, getStats, getTranscripts, triggerPipeline } from "./services/api";
import { connectPipelineSocket } from "./services/websocket";

export default function App() {
  const [apiOnline, setApiOnline] = useState(false);
  const [wsStatus, setWsStatus] = useState("connecting");
  const [stats, setStats] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [transcripts, setTranscripts] = useState([]);
  const [events, setEvents] = useState([]);
  const [runningPipeline, setRunningPipeline] = useState(false);

  const handleRunPipeline = async () => {
    setRunningPipeline(true);
    try {
      await triggerPipeline(5);
      await loadData();
    } finally {
      setRunningPipeline(false);
    }
  };

  const loadData = useCallback(async () => {
    try {
      const [healthRes, statsRes, compRes, transRes] = await Promise.all([
        getHealth(),
        getStats(),
        getCompanies(),
        getTranscripts(),
      ]);
      setApiOnline(healthRes?.status === "healthy");
      setStats(statsRes);
      setCompanies(compRes?.companies || []);
      setTranscripts(transRes || []);
    } catch {
      setApiOnline(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const disconnect = connectPipelineSocket({
      onStatusChange: setWsStatus,
      onEvent: (event) => {
        setEvents((prev) => [
          { ...event, time: new Date().toLocaleTimeString() },
          ...prev.slice(0, 49),
        ]);
        loadData();
      },
    });
    return disconnect;
  }, [loadData]);

  const sharedProps = { stats, companies, transcripts, events, wsStatus };

  return (
    <BrowserRouter>
      <div className="min-h-screen flex bg-slate-950 text-slate-100">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar
            apiOnline={apiOnline}
            wsStatus={wsStatus}
            onRefresh={loadData}
            onRunPipeline={handleRunPipeline}
            runningPipeline={runningPipeline}
          />
          <main className="flex-1 p-6 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard {...sharedProps} section="overview" />} />
              <Route path="/companies" element={<Dashboard {...sharedProps} section="companies" />} />
              <Route path="/companies/:symbol" element={<CompanyDetails companies={companies} />} />
              <Route path="/transcripts/:id" element={<TranscriptDetails />} />
              <Route path="/calls" element={<Dashboard {...sharedProps} section="calls" />} />
              <Route path="/insights" element={<Dashboard {...sharedProps} section="insights" />} />
              <Route path="/monitor" element={<Dashboard {...sharedProps} section="monitor" />} />
              <Route path="/settings" element={<Dashboard {...sharedProps} section="settings" />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

