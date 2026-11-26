import { Link } from "react-router-dom";
import { FileText, CheckCircle2, Clock, Download, Eye } from "lucide-react";
import { getTranscriptPdfUrl } from "../services/api";

export default function SummaryCard({ transcript }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 p-4 flex flex-col gap-3 transition">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="h-9 w-9 rounded-lg bg-slate-800 flex items-center justify-center text-cyan-400 shrink-0">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-white">
                {transcript.company}
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {transcript.exchange}
              </span>
              {transcript.quarter && (
                <span className="text-[11px] px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300">
                  {transcript.quarter}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-1 line-clamp-2">
              {transcript.title || "Earnings Call Transcript"}
            </p>
          </div>
        </div>

        <span
          className={`inline-flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-full shrink-0 ${
            transcript.processed
              ? "bg-emerald-500/15 text-emerald-300"
              : "bg-amber-500/15 text-amber-300"
          }`}
        >
          {transcript.processed ? (
            <>
              <CheckCircle2 className="h-3 w-3" /> Summarized
            </>
          ) : (
            <>
              <Clock className="h-3 w-3" /> Pending
            </>
          )}
        </span>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-800/80">
        <span>Date: {transcript.call_date || "—"}</span>
        <div className="flex items-center gap-3">
          <Link
            to={`/transcripts/${transcript.id}`}
            className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-medium"
          >
            <Eye className="h-3.5 w-3.5" /> View Summary
          </Link>
          <a
            href={getTranscriptPdfUrl(transcript.id)}
            download
            className="inline-flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-medium"
          >
            <Download className="h-3.5 w-3.5" /> Download PDF
          </a>
        </div>
      </div>
    </div>
  );
}
