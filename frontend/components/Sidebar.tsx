"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  AlertTriangle,
  Search,
  Target,
  FileText,
  Sparkles,
  Clock
} from "lucide-react";
import NexusLogo from "./NexusLogo";
import ThemeToggle from "./ThemeToggle";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Incidents", href: "/incidents", icon: AlertTriangle },
  { name: "Scan", href: "/scan", icon: Search },
  { name: "Blast Radius", href: "/blast", icon: Target },
  { name: "Pre-Mortem", href: "/premortem", icon: FileText },
];

const demoLink = { name: "🎬 Cinematic Demo", href: "/demo", icon: Sparkles };

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 glass-panel border-r border-[var(--border)] flex flex-col backdrop-blur-xl">
      {/* Logo & Branding */}
      <div className="p-6 border-b border-[var(--border)]">
        <div className="flex items-center gap-3 mb-2">
          <NexusLogo size={36} />
          <div>
            <h1 className="text-lg font-bold text-[var(--text)] tracking-tight">
              Nexus-IntelliBob
            </h1>
            <p className="text-[10px] text-[var(--text-secondary)] font-medium">
              AI Incident Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                transition-all duration-200 group
                ${
                  isActive
                    ? "bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/30 shadow-lg shadow-[var(--accent)]/10"
                    : "text-[var(--text-secondary)] hover:text-[var(--text)] hover:bg-[var(--card)] border border-transparent"
                }
              `}
            >
              <Icon className={`w-5 h-5 transition-transform duration-200 ${isActive ? '' : 'group-hover:scale-110'}`} />
              {item.name}
            </Link>
          );
        })}
        
        {/* Demo Link - Special Highlight */}
        <div className="pt-4 mt-4 border-t border-[var(--border)]">
          <Link
            href={demoLink.href}
            className={`
              flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
              transition-all duration-200 group
              ${
                pathname === demoLink.href
                  ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-purple-400 border border-purple-500/30 shadow-lg shadow-purple-500/20"
                  : "bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-purple-400 border border-purple-500/20 hover:border-purple-500/40 hover:shadow-lg hover:shadow-purple-500/20"
              }
            `}
          >
            <demoLink.icon className="w-5 h-5 animate-pulse" />
            {demoLink.name}
          </Link>
        </div>
      </nav>

      {/* Theme Toggle & Footer */}
      <div className="p-4 border-t border-[var(--border)] space-y-4">
        {/* Theme Toggle */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-[var(--text-secondary)]">Theme</span>
          <ThemeToggle />
        </div>
        
        {/* Footer Info */}
        <div className="text-xs text-[var(--text-secondary)]">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-3 h-3" />
            <p>Version 1.0.0</p>
          </div>
          <p className="text-[10px]">© 2026 Nexus-IntelliBob</p>
          <p className="text-[10px] mt-1 text-[var(--accent)]">Made with Bob</p>
        </div>
      </div>
    </aside>
  );
}

// Made with Bob
