import {
  Building2,
  FileText,
  Sparkles,
  Activity,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import CompanyCard from "../components/CompanyCard";
import SummaryCard from "../components/SummaryCard";
import LiveFeed from "../components/LiveFeed";

export default function Dashboard({
  stats,
  companies,
  transcripts,
  events,
  wsStatus,
  section = "overview",
}) {
  const countBySymbol = transcripts.reduce((acc, t) => {
    const sym = (t.symbol || "").toUpperCase();
    acc[sym] = (acc[sym] || 0) + 1;
    return acc;
  }, {});

  const chartData = companies.map((c) => ({
    symbol: c.symbol,
    transcripts: countBySymbol[c.symbol] || 0,
  }));

  const kpis = [
    {
      label: "Tracked Companies",
      value: String(stats?.tracked_companies ?? companies.length ?? 0).padStart(2, "0"),
      sub: "NSE & BSE universe",
      icon: Building2,
      color: "text-emerald-400",
    },
    {
      label: "Transcripts",
      value: stats?.total_transcripts ?? 0,
      sub: "Verified documents",
      icon: FileText,
      color: "text-cyan-400",
    },
    {
      label: "AI Summaries",
      value: stats?.processed_summaries ?? 0,
      sub: "Successfully generated",
      icon: Sparkles,
      color: "text-violet-400",
    },
    {
      label: "Live Pipeline",
      value: stats?.pipeline_status ? stats.pipeline_status.toUpperCase() : "READY",
      sub: `WebSocket: ${wsStatus}`,
      icon: Activity,
      color: "text-amber-400",
    },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map(({ label, value, sub, icon: Icon, color }) => (
          <div
            key={label}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-4"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">{label}</span>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
            <div className="mt-2 text-2xl font-bold text-white">{value}</div>
            <div className="mt-1 text-xs text-slate-500">{sub}</div>
          </div>
        ))}
      </div>

      {/* Analytics + Live Feed */}
      {(section === "overview" || section === "monitor") && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <h3 className="text-sm font-semibold text-white mb-4">
              Transcript Coverage by Company
            </h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="symbol" stroke="#94a3b8" fontSize={12} />
                  <YAxis stroke="#94a3b8" fontSize={12} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#1e293b",
                      borderRadius: "8px",
                      color: "#f1f5f9",
                    }}
                  />
                  <Bar dataKey="transcripts" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <LiveFeed events={events} wsStatus={wsStatus} />
        </div>
      )}

      {/* Companies Grid */}
      {(section === "overview" || section === "companies") && (
        <div>
          <h2 className="text-sm font-semibold text-white mb-3">
            Tracked Companies ({companies.length})
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {companies.map((c) => (
              <CompanyCard
                key={c.symbol}
                company={c}
                transcriptCount={countBySymbol[c.symbol] || 0}
              />
            ))}
          </div>
        </div>
      )}

      {/* Transcripts / Summaries */}
      {(section === "overview" || section === "calls" || section === "insights") && (
        <div>
          <h2 className="text-sm font-semibold text-white mb-3">
            Recent Earnings Calls ({transcripts.length})
          </h2>
          {transcripts.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-8 text-center text-sm text-slate-400">
              No transcripts ingested yet. Run the NSE/BSE ingestion pipeline to populate real filings.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {transcripts.map((t) => (
                <SummaryCard key={t.id} transcript={t} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Settings view */}
      {section === "settings" && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-3 text-sm">
          <h2 className="text-base font-semibold text-white">
            Platform Configuration
          </h2>
          <p className="text-slate-400">
            Frontend is proxying <code className="text-emerald-400">/api</code> and{" "}
            <code className="text-emerald-400">/ws</code> directly to the FastAPI backend at{" "}
            <code className="text-slate-200">http://127.0.0.1:8000</code>.
          </p>
        </div>
      )}
    </div>
  );
}

