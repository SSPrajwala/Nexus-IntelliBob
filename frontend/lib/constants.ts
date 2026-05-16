export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const SEVERITY_COLORS = {
  critical: "text-red-500 bg-red-500/10 border-red-500/20",
  high: "text-orange-500 bg-orange-500/10 border-orange-500/20",
  medium: "text-yellow-500 bg-yellow-500/10 border-yellow-500/20",
  low: "text-blue-500 bg-blue-500/10 border-blue-500/20",
} as const;

export const SEVERITY_LABELS = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
} as const;

export const STATUS_COLORS = {
  open: "text-red-400 bg-red-400/10",
  investigating: "text-yellow-400 bg-yellow-400/10",
  resolved: "text-green-400 bg-green-400/10",
  closed: "text-gray-400 bg-gray-400/10",
} as const;

export const STATUS_LABELS = {
  open: "Open",
  investigating: "Investigating",
  resolved: "Resolved",
  closed: "Closed",
} as const;

export const ROUTES = {
  HOME: "/",
  INCIDENTS: "/incidents",
  SCAN: "/scan",
  BLAST: "/blast",
  PREMORTEM: "/premortem",
} as const;

// Made with Bob
