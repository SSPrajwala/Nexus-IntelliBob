"use client";

import { useState } from "react";
import { Search, FolderOpen } from "lucide-react";
import LoadingState from "@/components/LoadingState";

export default function ScanPage() {
  const [loading, setLoading] = useState(false);
  const [repoPath, setRepoPath] = useState("");

  const handleScan = async () => {
    if (!repoPath.trim()) return;
    setLoading(true);
    // Scan logic will be implemented
    setTimeout(() => setLoading(false), 2000);
  };

  if (loading) {
    return <LoadingState message="Scanning repository..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Scan Repository</h1>
        <p className="text-gray-400">
          Scan your codebase for patterns matching known incident DNA
        </p>
      </div>

      {/* Scan Form */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">
          Repository Details
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Repository Path
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                placeholder="/path/to/your/repository"
                className="flex-1 bg-[#27272a] border border-[#3f3f46] rounded-md px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              <button className="px-4 py-2 bg-[#27272a] text-white rounded-md hover:bg-[#3f3f46] transition-colors flex items-center gap-2">
                <FolderOpen className="w-4 h-4" />
                Browse
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Enter the absolute path to your repository
            </p>
          </div>

          <button
            onClick={handleScan}
            disabled={!repoPath.trim()}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Search className="w-5 h-5" />
            Start Scan
          </button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <h3 className="text-sm font-semibold text-white mb-2">
            Pattern Matching
          </h3>
          <p className="text-xs text-gray-400">
            Scans code for patterns extracted from historical incidents
          </p>
        </div>
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <h3 className="text-sm font-semibold text-white mb-2">
            Risk Detection
          </h3>
          <p className="text-xs text-gray-400">
            Identifies potential failure points before they become incidents
          </p>
        </div>
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <h3 className="text-sm font-semibold text-white mb-2">
            Confidence Scoring
          </h3>
          <p className="text-xs text-gray-400">
            Each match includes a confidence score for prioritization
          </p>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
