"use client";

import { useState } from "react";
import { Search, Github, AlertTriangle, CheckCircle, Filter, ArrowUpDown, ExternalLink } from "lucide-react";
import LoadingState from "@/components/LoadingState";
import RiskMatchCard from "@/components/RiskMatchCard";
import PDFDownloadButton from "@/components/PDFDownloadButton";
import { api } from "@/lib/api";
import { RiskMatch, ScanRepoResponse } from "@/types";

type ScanStage = "idle" | "indexing" | "mapping" | "detecting" | "correlating" | "computing" | "complete";
type SeverityFilter = "all" | "critical" | "high" | "medium" | "low";
type SortOption = "severity" | "confidence" | "blast_radius";

const scanStages = [
  { id: "indexing", label: "Indexing services", duration: 800 },
  { id: "mapping", label: "Mapping dependencies", duration: 1000 },
  { id: "detecting", label: "Detecting anti-patterns", duration: 1500 },
  { id: "correlating", label: "Correlating incident DNA", duration: 1200 },
  { id: "computing", label: "Computing risk graph", duration: 900 },
];

const exampleRepos = [
  { url: "https://github.com/vercel/next.js", label: "vercel/next.js" },
  { url: "https://github.com/facebook/react", label: "facebook/react" },
  { url: "https://github.com/nodejs/node", label: "nodejs/node" },
];

export default function ScanPage() {
  const [repoPath, setRepoPath] = useState("");
  const [scanning, setScanning] = useState(false);
  const [currentStage, setCurrentStage] = useState<ScanStage>("idle");
  const [scanResults, setScanResults] = useState<ScanRepoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>("all");
  const [sortBy, setSortBy] = useState<SortOption>("severity");

  const isValidGitHubUrl = (url: string): boolean => {
    const githubPattern = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    return githubPattern.test(url.trim());
  };

  const handleScan = async () => {
    const trimmedPath = repoPath.trim();
    if (!trimmedPath) return;
    
    // Validate GitHub URL
    if (!isValidGitHubUrl(trimmedPath)) {
      setError("Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)");
      return;
    }
    
    setScanning(true);
    setError(null);
    setScanResults(null);
    setCurrentStage("indexing");

    try {
      // Animate through scan stages
      for (const stage of scanStages) {
        setCurrentStage(stage.id as ScanStage);
        await new Promise(resolve => setTimeout(resolve, stage.duration));
      }

      // Perform actual scan
      const results = await api.scanRepository(repoPath);
      setScanResults(results);
      setCurrentStage("complete");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to scan repository");
      setCurrentStage("idle");
    } finally {
      setScanning(false);
    }
  };

  const getFilteredAndSortedRisks = (): RiskMatch[] => {
    if (!scanResults?.matches) return [];

    let risks = [...scanResults.matches];

    // Apply severity filter
    if (severityFilter !== "all") {
      risks = risks.filter(r => 
        (r.severity || r.risk_level) === severityFilter
      );
    }

    // Apply sorting
    risks.sort((a, b) => {
      if (sortBy === "severity") {
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        const aSev = severityOrder[(a.severity || a.risk_level) as keyof typeof severityOrder] || 0;
        const bSev = severityOrder[(b.severity || b.risk_level) as keyof typeof severityOrder] || 0;
        return bSev - aSev;
      } else if (sortBy === "confidence") {
        return (b.confidence || b.confidence_score || 0) - (a.confidence || a.confidence_score || 0);
      } else if (sortBy === "blast_radius") {
        return (b.blast_radius_score || 0) - (a.blast_radius_score || 0);
      }
      return 0;
    });

    return risks;
  };

  const filteredRisks = getFilteredAndSortedRisks();

  // Scanning animation
  if (scanning || currentStage !== "idle" && currentStage !== "complete") {
    const currentStageIndex = scanStages.findIndex(s => s.id === currentStage);
    const progress = currentStageIndex >= 0 ? ((currentStageIndex + 1) / scanStages.length) * 100 : 0;

    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-2xl w-full space-y-6">
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-500/10 rounded-full mb-4">
              <Search className="w-10 h-10 text-red-400 animate-pulse" />
            </div>
            <h2 className="text-2xl font-bold text-white">Scanning Repository</h2>
            <p className="text-gray-400">
              {scanStages[currentStageIndex]?.label || "Initializing..."}
            </p>
          </div>

          {/* Progress Bar */}
          <div className="relative">
            <div className="h-2 bg-[#27272a] rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="absolute -top-1 left-0 right-0 flex justify-between">
              {scanStages.map((stage, idx) => (
                <div
                  key={stage.id}
                  className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${
                    idx <= currentStageIndex
                      ? "bg-red-500 border-red-500"
                      : "bg-[#27272a] border-[#3f3f46]"
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Stage List */}
          <div className="space-y-2">
            {scanStages.map((stage, idx) => (
              <div
                key={stage.id}
                className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                  idx === currentStageIndex
                    ? "bg-red-500/10 border border-red-500/30"
                    : idx < currentStageIndex
                    ? "bg-green-500/5 border border-green-500/20"
                    : "bg-[#18181b] border border-[#27272a]"
                }`}
              >
                {idx < currentStageIndex ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : idx === currentStageIndex ? (
                  <div className="w-5 h-5 border-2 border-red-400 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <div className="w-5 h-5 border-2 border-[#3f3f46] rounded-full" />
                )}
                <span className={`text-sm ${
                  idx <= currentStageIndex ? "text-white" : "text-gray-500"
                }`}>
                  {stage.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Scan Repository</h1>
        <p className="text-gray-400">
          Detect architectural risks and anti-patterns before they become incidents
        </p>
      </div>

      {/* Scan Form */}
      <div className="glass-card rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
            <Github className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">
              GitHub Repository Analysis
            </h2>
            <p className="text-sm text-gray-400">
              Analyze any public GitHub repository
            </p>
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              GitHub Repository URL
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Github className="w-5 h-5 text-gray-500" />
              </div>
              <input
                type="text"
                value={repoPath}
                onChange={(e) => {
                  setRepoPath(e.target.value);
                  setError(null); // Clear error on input change
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && repoPath.trim()) {
                    handleScan();
                  }
                }}
                placeholder="Enter GitHub repository URL"
                className="w-full bg-[#27272a] border border-[#3f3f46] rounded-md pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all"
              />
            </div>
            <p className="text-sm text-gray-400 mt-2">
              Analyze any GitHub repository to detect risks, map architecture, and generate AI-powered failure predictions.
            </p>
          </div>

          {/* Example Links */}
          <div className="space-y-2">
            <p className="text-xs font-medium text-gray-400">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {exampleRepos.map((repo) => (
                <button
                  key={repo.url}
                  onClick={() => setRepoPath(repo.url)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#27272a] hover:bg-[#3f3f46] border border-[#3f3f46] rounded-md text-xs text-gray-300 transition-colors group"
                >
                  <ExternalLink className="w-3 h-3 text-gray-500 group-hover:text-red-400 transition-colors" />
                  {repo.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleScan}
            disabled={!repoPath.trim() || scanning}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-md hover:from-red-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg shadow-red-500/20"
          >
            <Search className="w-5 h-5" />
            Analyze Repository
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-red-400 mb-1">Scan Failed</h3>
              <p className="text-sm text-gray-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {scanResults && currentStage === "complete" && (
        <>
          {/* Report Header with PDF Download */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">Scan Results</h2>
              <p className="text-sm text-gray-400 mt-1">
                Repository analysis complete
              </p>
            </div>
            <PDFDownloadButton
              elementId="scan-report-content"
              filename="Nexus-Scan-Report.pdf"
              title="Nexus-IntelliBob Risk Scan Report"
              variant="primary"
            />
          </div>

          {/* Wrapped Report Content for PDF Export */}
          <div id="scan-report-content" className="space-y-6">
            {/* Stats Summary */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
              <div className="text-2xl font-bold text-white">{scanResults.total_files_scanned || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Files Scanned</div>
            </div>
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <div className="text-2xl font-bold text-red-400">{scanResults.critical_risks || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Critical</div>
            </div>
            <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-4">
              <div className="text-2xl font-bold text-orange-400">{scanResults.high_risks || 0}</div>
              <div className="text-xs text-gray-400 mt-1">High</div>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
              <div className="text-2xl font-bold text-yellow-400">{scanResults.medium_risks || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Medium</div>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-400">{scanResults.low_risks || 0}</div>
              <div className="text-xs text-gray-400 mt-1">Low</div>
            </div>
          </div>

          {/* Filters and Sort */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-400">Filter:</span>
              {(["all", "critical", "high", "medium", "low"] as SeverityFilter[]).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSeverityFilter(filter)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    severityFilter === filter
                      ? "bg-red-500 text-white"
                      : "bg-[#27272a] text-gray-400 hover:bg-[#3f3f46]"
                  }`}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2 ml-auto">
              <ArrowUpDown className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-400">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="bg-[#27272a] border border-[#3f3f46] rounded-md px-3 py-1 text-sm text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <option value="severity">Severity</option>
                <option value="confidence">Confidence</option>
                <option value="blast_radius">Blast Radius</option>
              </select>
            </div>
          </div>

          {/* Risk Cards */}
          <div className="space-y-4">
            {filteredRisks.length > 0 ? (
              filteredRisks.map((risk, index) => (
                <RiskMatchCard key={risk.id || index} risk={risk} index={index} />
              ))
            ) : (
              <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-12 text-center">
                <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">
                  {severityFilter === "all" ? "No Risks Found" : `No ${severityFilter} risks found`}
                </h3>
                <p className="text-sm text-gray-400">
                  {severityFilter === "all" 
                    ? "This repository appears to be following best practices!"
                    : "Try adjusting the filter to see other risk levels."}
                </p>
              </div>
            )}
          </div>
          </div>
        </>
      )}

      {/* Info Cards (shown when no results) */}
      {!scanResults && currentStage === "idle" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
            <h3 className="text-sm font-semibold text-white mb-2">
              Pattern Matching
            </h3>
            <p className="text-xs text-gray-400">
              Scans code for architectural anti-patterns and risk indicators
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
              DNA Correlation
            </h3>
            <p className="text-xs text-gray-400">
              Correlates findings with known incident DNA patterns
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
