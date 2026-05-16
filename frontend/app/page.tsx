"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, Search, TrendingUp } from "lucide-react";
import MetricCard from "@/components/MetricCard";
import LoadingState from "@/components/LoadingState";
import { DashboardStats } from "@/types";
import { api, safeApiCall } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    const data = await safeApiCall(
      () => api.getDashboardStats(),
      {
        total_incidents: 0,
        total_scans: 0,
        total_risk_matches: 0,
        critical_risks: 0,
        high_risks: 0,
        medium_risks: 0,
        low_risks: 0,
        avg_confidence_score: 0,
        repositories_monitored: 0,
      }
    );
    setStats(data);
    setLoading(false);
  };

  if (loading) {
    return <LoadingState message="Loading dashboard..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">
          AI-powered incident intelligence for your codebase
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Incidents"
          value={stats?.total_incidents || 0}
          icon={AlertTriangle}
        />
        <MetricCard
          title="Total Scans"
          value={stats?.total_scans || 0}
          icon={Search}
        />
        <MetricCard
          title="Risk Matches"
          value={stats?.total_risk_matches || 0}
          icon={Activity}
        />
        <MetricCard
          title="Repositories"
          value={stats?.repositories_monitored || 0}
          icon={TrendingUp}
        />
      </div>

      {/* Risk Breakdown */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">
          Risk Breakdown
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-500 mb-1">
              {stats?.critical_risks || 0}
            </div>
            <div className="text-sm text-gray-400">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-500 mb-1">
              {stats?.high_risks || 0}
            </div>
            <div className="text-sm text-gray-400">High</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-500 mb-1">
              {stats?.medium_risks || 0}
            </div>
            <div className="text-sm text-gray-400">Medium</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-500 mb-1">
              {stats?.low_risks || 0}
            </div>
            <div className="text-sm text-gray-400">Low</div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-2">
            Average Confidence Score
          </h3>
          <div className="text-3xl font-bold text-white">
            {((stats?.avg_confidence_score || 0) * 100).toFixed(1)}%
          </div>
          <p className="text-sm text-gray-400 mt-2">
            Pattern matching accuracy
          </p>
        </div>

        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-2">
            Last Scan
          </h3>
          <div className="text-lg text-white">
            {stats?.last_scan_time
              ? new Date(stats.last_scan_time).toLocaleString()
              : "No scans yet"}
          </div>
          <p className="text-sm text-gray-400 mt-2">
            Most recent repository scan
          </p>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-2">
          🚀 Getting Started
        </h3>
        <p className="text-gray-300 mb-4">
          Start by ingesting incident data or scanning your repositories for
          potential risks.
        </p>
        <div className="flex gap-3">
          <a
            href="/incidents"
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
          >
            Add Incident
          </a>
          <a
            href="/scan"
            className="px-4 py-2 bg-[#27272a] text-white rounded-md hover:bg-[#3f3f46] transition-colors"
          >
            Scan Repository
          </a>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
