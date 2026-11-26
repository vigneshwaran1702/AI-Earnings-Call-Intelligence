import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { getTranscripts } from "../services/api";
import SummaryCard from "../components/SummaryCard";

export default function CompanyDetails({ companies }) {
  const { symbol } = useParams();
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(true);

  const company = companies.find(
    (c) => c.symbol.toUpperCase() === (symbol || "").toUpperCase()
  );

  useEffect(() => {
    let active = true;
    setLoading(true);
    getTranscripts(symbol)
      .then((data) => {
        if (active) setTranscripts(data);
      })
      .catch(() => {
        if (active) setTranscripts([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [symbol]);

  return (
    <div className="space-y-6">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-emerald-400"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to Overview
      </Link>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-xl font-bold text-white">
          {company?.name || symbol}
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          NSE Symbol: {symbol} · BSE Scrip Code: {company?.scrip_code || "—"}
        </p>
      </div>

      {loading ? (
        <div className="text-sm text-slate-400">Loading transcripts…</div>
      ) : transcripts.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-8 text-center text-sm text-slate-400">
          No transcripts recorded for {company?.name || symbol} yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {transcripts.map((t) => (
            <SummaryCard key={t.id} transcript={t} />
          ))}
        </div>
      )}
    </div>
  );
}

