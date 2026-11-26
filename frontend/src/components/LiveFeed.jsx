import { Radio } from "lucide-react";

export default function LiveFeed({ events, wsStatus }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Radio className="h-4 w-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Live Pipeline Feed</h3>
        </div>
        <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 capitalize">
          {wsStatus}
        </span>
      </div>

      {events.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center py-8 text-xs text-slate-500">
          <p>WebSocket connected to <code className="text-slate-300">/ws/pipeline</code></p>
          <p className="mt-1">Waiting for new NSE/BSE filings and AI summary events…</p>
        </div>
      ) : (
        <div className="space-y-2 overflow-y-auto max-h-64 pr-1">
          {events.map((ev, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-800 bg-slate-950/70 p-2.5 text-xs"
            >
              <div className="flex items-center justify-between text-emerald-400 font-medium">
                <span>{ev.type || "event"}</span>
                <span className="text-slate-500 text-[10px]">{ev.time}</span>
              </div>
              <p className="text-slate-300 mt-1">
                {ev.message || JSON.stringify(ev)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

