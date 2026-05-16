"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Loader2,
  AlertTriangle,
  Github,
  FolderOpen,
  Sparkles,
} from "lucide-react";
import { api } from "@/lib/api";
import type { PreMortemReport as PreMortemReportType } from "@/types";
import PreMortemReport from "@/components/PreMortemReport";
import PDFDownloadButton from "@/components/PDFDownloadButton";
import EmptyState from "@/components/EmptyState";

type LoadingStage = {
  stage: string;
  description: string;
};

const LOADING_STAGES: LoadingStage[] = [
  {
    stage: "Learning repository topology",
    description: "Analyzing service dependencies and architecture patterns...",
  },
  {
    stage: "Correlating incident DNA",
    description: "Matching code patterns with historical failure signatures...",
  },
  {
    stage: "Predicting cascade propagation",
    description: "Computing blast radius and failure propagation paths...",
  },
  {
    stage: "Computing operational impact",
    description: "Estimating business and customer impact metrics...",
  },
  {
    stage: "Generating executive intelligence report",
    description: "Synthesizing pre-mortem analysis and recommendations...",
  },
];

export default function PreMortemPage() {
  const [repoPath, setRepoPath] = useState("demo-repos/payment-system");
  const [failureMode, setFailureMode] = useState("auto");
  const [specificTarget, setSpecificTarget] = useState("");
  const [availableTargets, setAvailableTargets] = useState<any[]>([]);
  const [loadingTargets, setLoadingTargets] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [report, setReport] = useState<PreMortemReportType | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchAvailableTargets = async () => {
    if (!repoPath.trim() || failureMode !== "specific") return;
    
    setLoadingTargets(true);
    try {
      const response = await fetch("http://localhost:8000/api/detect-services", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_path: repoPath }),
      });
      const data = await response.json();
      if (data.success && data.services) {
        setAvailableTargets(data.services);
        if (data.services.length > 0) {
          setSpecificTarget(data.services[0].name);
        }
      }
    } catch (err) {
      console.error("Failed to fetch targets:", err);
    } finally {
      setLoadingTargets(false);
    }
  };

  const handleModeChange = (mode: string) => {
    setFailureMode(mode);
    if (mode === "specific") {
      fetchAvailableTargets();
    }
  };

  const handleGenerate = async () => {
    if (!repoPath.trim()) {
      setError("Please provide repository path");
      return;
    }

    if (failureMode === "specific" && !specificTarget.trim()) {
      setError("Please select a component for specific mode");
      return;
    }

    setIsLoading(true);
    setError(null);
    setReport(null);
    setCurrentStage(0);

    // Animate through loading stages
    const stageInterval = setInterval(() => {
      setCurrentStage((prev) => {
        if (prev < LOADING_STAGES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2000);

    try {
      const response = await api.generatePreMortem({
        repo_path: repoPath,
        failure_mode: failureMode,
        failed_service: failureMode === "specific" ? specificTarget : undefined,
      });

      clearInterval(stageInterval);

      if (response.success && response.report) {
        setReport(response.report);
      } else {
        setError(response.message || "Failed to generate pre-mortem report");
      }
    } catch (err) {
      clearInterval(stageInterval);
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
      setCurrentStage(0);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Brain className="w-8 h-8 text-purple-400" />
          <h1 className="text-3xl font-bold text-white">Pre-Mortem Intelligence</h1>
        </div>
        <p className="text-gray-400">
          AI-powered incident prediction before outages occur
        </p>
      </div>

      {/* Input Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Inputs */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                <div className="flex items-center gap-2">
                  <FolderOpen className="w-4 h-4" />
                  Repository Path
                </div>
              </label>
              <input
                type="text"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                placeholder="demo-repos/payment-system"
                className="w-full px-4 py-3 bg-gray-950 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500 mt-1">
                Local path or GitHub URL (e.g., https://github.com/user/repo)
              </p>
            </div>

            {/* Failure Mode Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Failure Simulation Mode
              </label>
              <div className="space-y-3">
                {/* Auto Mode */}
                <label className="flex items-start gap-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg cursor-pointer hover:border-purple-500/50 transition-colors">
                  <input
                    type="radio"
                    name="failureMode"
                    value="auto"
                    checked={failureMode === "auto"}
                    onChange={(e) => handleModeChange(e.target.value)}
                    className="mt-1 w-4 h-4 text-purple-500 focus:ring-purple-500"
                    disabled={isLoading}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-white font-medium">
                      <span>🤖</span>
                      <span>Auto (Recommended)</span>
                      {failureMode === "auto" && (
                        <span className="ml-auto text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400 mt-1">
                      Automatically detect the most critical failure point
                    </p>
                  </div>
                </label>

                {/* All Mode */}
                <label className="flex items-start gap-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg cursor-pointer hover:border-purple-500/50 transition-colors">
                  <input
                    type="radio"
                    name="failureMode"
                    value="all"
                    checked={failureMode === "all"}
                    onChange={(e) => handleModeChange(e.target.value)}
                    className="mt-1 w-4 h-4 text-purple-500 focus:ring-purple-500"
                    disabled={isLoading}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-white font-medium">
                      <span>🌐</span>
                      <span>Entire System</span>
                      {failureMode === "all" && (
                        <span className="ml-auto text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400 mt-1">
                      Analyze platform-wide failure scenarios
                    </p>
                  </div>
                </label>

                {/* Specific Mode */}
                <label className="flex items-start gap-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg cursor-pointer hover:border-purple-500/50 transition-colors">
                  <input
                    type="radio"
                    name="failureMode"
                    value="specific"
                    checked={failureMode === "specific"}
                    onChange={(e) => handleModeChange(e.target.value)}
                    className="mt-1 w-4 h-4 text-purple-500 focus:ring-purple-500"
                    disabled={isLoading}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-white font-medium">
                      <span>🎯</span>
                      <span>Select Component</span>
                      {failureMode === "specific" && (
                        <span className="ml-auto text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-400 mt-1">
                      Choose a specific component to analyze
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Component Selector (only for specific mode) */}
            {failureMode === "specific" && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Select Component
                </label>
                <select
                  value={specificTarget}
                  onChange={(e) => setSpecificTarget(e.target.value)}
                  disabled={loadingTargets || availableTargets.length === 0 || isLoading}
                  className="w-full px-4 py-2 bg-gray-950 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                >
                  {loadingTargets ? (
                    <option>Loading components...</option>
                  ) : availableTargets.length === 0 ? (
                    <option>No components detected</option>
                  ) : (
                    availableTargets.map((target) => (
                      <option key={target.name} value={target.name}>
                        {target.name} ({target.type})
                      </option>
                    ))
                  )}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {loadingTargets
                    ? "Detecting components..."
                    : availableTargets.length === 0
                    ? "Enter repository path to detect components"
                    : `${availableTargets.length} component(s) detected`}
                </p>
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-700 disabled:to-gray-600 text-white font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-purple-500/50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Generate Pre-Mortem
                </>
              )}
            </button>
          </div>

          {/* Right Column - Info */}
          <div className="bg-gray-950/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              How It Works
            </h3>
            <div className="space-y-3 text-sm text-gray-400">
              <div className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-950 border border-purple-700 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 text-xs font-bold">1</span>
                </div>
                <p>
                  <span className="text-white font-semibold">Repository Scan:</span> Analyzes
                  code for architectural risk patterns
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-950 border border-purple-700 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 text-xs font-bold">2</span>
                </div>
                <p>
                  <span className="text-white font-semibold">Blast Radius:</span> Computes
                  cascading failure propagation paths
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-950 border border-purple-700 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 text-xs font-bold">3</span>
                </div>
                <p>
                  <span className="text-white font-semibold">DNA Correlation:</span> Matches
                  patterns with historical incidents
                </p>
              </div>
              <div className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-950 border border-purple-700 flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-400 text-xs font-bold">4</span>
                </div>
                <p>
                  <span className="text-white font-semibold">Intelligence Report:</span>{" "}
                  Generates actionable pre-mortem analysis
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-red-950/50 border border-red-800 rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <div>
                <h3 className="text-red-400 font-semibold">Error</h3>
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Animation */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-8"
          >
            <div className="flex flex-col items-center justify-center space-y-6">
              <div className="relative">
                <div className="w-20 h-20 border-4 border-purple-900 rounded-full" />
                <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-purple-500 rounded-full animate-spin" />
                <Brain className="absolute inset-0 m-auto w-8 h-8 text-purple-400" />
              </div>

              <div className="text-center space-y-2 max-w-md">
                <motion.h3
                  key={currentStage}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-xl font-bold text-white"
                >
                  {LOADING_STAGES[currentStage].stage}
                </motion.h3>
                <motion.p
                  key={`desc-${currentStage}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-gray-400"
                >
                  {LOADING_STAGES[currentStage].description}
                </motion.p>
              </div>

              {/* Progress Bar */}
              <div className="w-full max-w-md">
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-600 to-pink-600"
                    initial={{ width: "0%" }}
                    animate={{
                      width: `${((currentStage + 1) / LOADING_STAGES.length) * 100}%`,
                    }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  <span>Stage {currentStage + 1} of {LOADING_STAGES.length}</span>
                  <span>{Math.round(((currentStage + 1) / LOADING_STAGES.length) * 100)}%</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Report Display */}
      <AnimatePresence>
        {report && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="space-y-6"
          >
            {/* Report Header with PDF Download */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">Pre-Mortem Report</h2>
                <p className="text-sm text-gray-400 mt-1">
                  AI-powered failure prediction analysis
                </p>
              </div>
              <PDFDownloadButton
                elementId="premortem-report-content"
                filename="Nexus-PreMortem-Report.pdf"
                title="Nexus-IntelliBob Pre-Mortem Report"
                variant="primary"
              />
            </div>

            {/* Wrapped Report Content for PDF Export */}
            <div id="premortem-report-content">
              <PreMortemReport report={report} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!report && !isLoading && !error && (
        <EmptyState
          icon={Brain}
          title="No pre-mortem report generated yet"
          description="Enter a repository path and failed service, then click 'Generate Pre-Mortem' to create an AI-powered incident prediction report."
        />
      )}
    </div>
  );
}

// Made with Bob
