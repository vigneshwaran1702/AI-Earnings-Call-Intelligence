import { Activity, RefreshCw, Play } from "lucide-react";

export default function Navbar({ apiOnline, wsStatus, onRefresh, onRunPipeline, runningPipeline }) {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-900/70 backdrop-blur px-6 flex items-center justify-between">
      <div>
        <h1 className="text-base font-semibold text-white tracking-tight">
          Finosauras Intelligence
        </h1>
        <p className="text-[11px] font-medium tracking-widest text-emerald-400 uppercase">
          Earnings Call Analytics · India
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs">
          <span
            className={`h-2 w-2 rounded-full ${
              apiOnline ? "bg-emerald-400" : "bg-rose-500"
            }`}
          />
          <span className="text-slate-300">
            API: {apiOnline ? "Connected" : "Offline"}
          </span>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs">
          <Activity
            className={`h-3.5 w-3.5 ${
              wsStatus === "live"
                ? "text-emerald-400 animate-pulse"
                : "text-amber-400"
            }`}
          />
          <span className="text-slate-300 capitalize">
            Pipeline: {wsStatus}
          </span>
        </div>

        {onRunPipeline && (
          <button
            onClick={onRunPipeline}
            disabled={runningPipeline}
            className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 px-3 py-1.5 text-xs font-semibold text-slate-950 transition cursor-pointer"
          >
            <Play className="h-3.5 w-3.5" />
            {runningPipeline ? "Scanning..." : "Scan Filings"}
          </button>
        )}

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/70 hover:bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        )}
      </div>
    </header>
  );
}

