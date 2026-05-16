"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Home, 
  AlertTriangle, 
  Search, 
  Target, 
  FileText 
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Incidents", href: "/incidents", icon: AlertTriangle },
  { name: "Scan", href: "/scan", icon: Search },
  { name: "Blast Radius", href: "/blast", icon: Target },
  { name: "Pre-Mortem", href: "/premortem", icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 bg-[#18181b] border-r border-[#27272a] flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-[#27272a]">
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse-red" />
          </div>
          <h1 className="text-xl font-bold text-white">NEXUS</h1>
        </div>
        <p className="text-xs text-gray-400 mt-1">IntelliBob AI</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium
                transition-all duration-200
                ${
                  isActive
                    ? "bg-red-500/10 text-red-500 border border-red-500/20"
                    : "text-gray-400 hover:text-white hover:bg-[#27272a]"
                }
              `}
            >
              <Icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[#27272a]">
        <div className="text-xs text-gray-500">
          <p>Version 1.0.0</p>
          <p className="mt-1">© 2026 Nexus</p>
        </div>
      </div>
    </aside>
  );
}

// Made with Bob
