import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Download, Sparkles, Quote, AlertTriangle, FileText } from "lucide-react";
import { getTranscript, getTranscriptPdfUrl } from "../services/api";

export default function TranscriptDetails() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRaw, setShowRaw] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getTranscript(id)
      .then((res) => {
        if (active) setData(res);
      })
      .catch(() => {
        if (active) setData(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [id]);

  if (loading) {
    return <div className="text-sm text-slate-400">Loading AI summary…</div>;
  }

  if (!data) {
    return (
      <div className="text-sm text-rose-400">
        Transcript not found.{" "}
        <Link to="/" className="underline text-emerald-400">
          Return to Overview
        </Link>
      </div>
    );
  }

  const summary = data.summary;

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-emerald-400"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Overview
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowRaw((v) => !v)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 cursor-pointer"
          >
            <FileText className="h-3.5 w-3.5" />
            {showRaw ? "Hide Raw Transcript" : "View Raw Transcript"}
          </button>

          <a
            href={getTranscriptPdfUrl(data.id)}
            download
            className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-3.5 py-1.5 text-xs font-semibold transition"
          >
            <Download className="h-3.5 w-3.5" />
            Download PDF
          </a>
        </div>
      </div>

      {/* Header */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex items-center gap-2 flex-wrap">
          <h2 className="text-xl font-bold text-white">{data.company}</h2>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
            {data.exchange} · {data.symbol}
          </span>
          {data.quarter && (
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300">
              {data.quarter}
            </span>
          )}
          {summary?.sentiment && (
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300">
              Sentiment: {summary.sentiment}
            </span>
          )}
        </div>
        <p className="text-sm text-slate-400 mt-1">{data.title}</p>
        <p className="text-xs text-slate-500 mt-2">Call Date: {data.call_date || "—"}</p>
      </div>

      {/* Financial Highlights */}
      {summary?.financial_highlights?.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {summary.financial_highlights.map((h, i) => (
            <div
              key={i}
              className="rounded-xl border border-slate-800 bg-slate-900/60 p-4"
            >
              <div className="text-xs text-slate-400">{h.metric}</div>
              <div className="text-lg font-bold text-white mt-1">{h.value}</div>
              {h.change && (
                <div className="text-xs text-emerald-400 mt-0.5">{h.change}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 7-Section AI Summary */}
      {summary?.sections?.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <Sparkles className="h-4 w-4 text-violet-400" />
            AI Earnings Summary (with Transcript Evidence)
          </div>

          {summary.sections.map((sec, idx) => (
            <div
              key={idx}
              className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-2.5"
            >
              <h3 className="text-sm font-semibold text-emerald-300">
                {sec.title}
              </h3>
              <p className="text-sm text-slate-200 leading-relaxed">
                {sec.content}
              </p>
              {sec.evidence?.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 space-y-1">
                  {sec.evidence.map((q, qi) => (
                    <div
                      key={qi}
                      className="flex items-start gap-2 text-xs text-slate-400 italic"
                    >
                      <Quote className="h-3.5 w-3.5 text-slate-500 shrink-0 mt-0.5" />
                      <span>“{q}”</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Key Risks */}
      {summary?.key_risks?.length > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-5 space-y-2">
          <div className="flex items-center gap-2 text-sm font-semibold text-amber-300">
            <AlertTriangle className="h-4 w-4" />
            Key Risks & Watchlist
          </div>
          <ul className="list-disc list-inside text-sm text-slate-300 space-y-1">
            {summary.key_risks.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Raw Transcript */}
      {showRaw && data.raw_text && (
        <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <h3 className="text-sm font-semibold text-white mb-3">
            Original Extracted Transcript Text
          </h3>
          <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed">
            {data.raw_text}
          </pre>
        </div>
      )}
    </div>
  );
}

