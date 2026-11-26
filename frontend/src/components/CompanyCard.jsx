import { Link } from "react-router-dom";
import { ArrowUpRight, Building2 } from "lucide-react";

export default function CompanyCard({ company, transcriptCount = 0 }) {
  return (
    <Link
      to={`/companies/${company.symbol}`}
      className="group block rounded-xl border border-slate-800 bg-slate-900/60 hover:border-emerald-500/40 hover:bg-slate-900 p-4 transition"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-slate-800 flex items-center justify-center text-emerald-400">
            <Building2 className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white group-hover:text-emerald-300 transition">
              {company.name}
            </h3>
            <p className="text-xs text-slate-400">
              NSE: {company.symbol} · BSE: {company.scrip_code}
            </p>
          </div>
        </div>
        <ArrowUpRight className="h-4 w-4 text-slate-500 group-hover:text-emerald-400 transition" />
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <span className="text-slate-400">Transcripts</span>
        <span className="font-semibold text-slate-200">{transcriptCount}</span>
      </div>
    </Link>
  );
}

