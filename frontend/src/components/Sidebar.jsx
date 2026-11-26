import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  FileText,
  Sparkles,
  Radio,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/calls", label: "Earnings Calls", icon: FileText },
  { to: "/insights", label: "AI Insights", icon: Sparkles },
  { to: "/monitor", label: "Live Monitor", icon: Radio },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-slate-800/80 bg-slate-950 flex flex-col">
      <div className="h-16 px-5 flex items-center gap-2.5 border-b border-slate-800/80">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-slate-950 font-bold text-sm">
          FI
        </div>
        <div>
          <div className="text-sm font-semibold text-white">Finosauras</div>
          <div className="text-[11px] text-slate-400">NSE · BSE AI</div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-900"
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800/80 text-xs text-slate-500">
        FastAPI + React · v1.0.0
      </div>
    </aside>
  );
}

