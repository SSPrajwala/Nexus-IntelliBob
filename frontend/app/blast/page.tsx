"use client";

import { useState } from "react";
import { Target, AlertTriangle, DollarSign, Users, Shield, Zap, Loader2, GitBranch } from "lucide-react";
import { api } from "@/lib/api";
import BlastGraph from "@/components/BlastGraph";
import FailureTimeline from "@/components/FailureTimeline";
import MetricCard from "@/components/MetricCard";
import PDFDownloadButton from "@/components/PDFDownloadButton";
import LoadingState from "@/components/LoadingState";

export default function BlastPage() {
  const [repoPath, setRepoPath] = useState("demo-repos/payment-system");
  const [failureMode, setFailureMode] = useState("auto");
  const [specificTarget, setSpecificTarget] = useState("");
  const [availableTargets, setAvailableTargets] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingTargets, setLoadingTargets] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [animating, setAnimating] = useState(false);

  // Fetch available targets when repo path changes and mode is specific
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

  // Fetch targets when switching to specific mode
  const handleModeChange = (mode: string) => {
    setFailureMode(mode);
    if (mode === "specific") {
      fetchAvailableTargets();
    }
  };

  const handleSimulateFailure = async () => {
    if (!repoPath.trim()) {
      setError("Please provide repository path");
      return;
    }

    if (failureMode === "specific" && !specificTarget.trim()) {
      setError("Please select a component for specific mode");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setAnimating(true);

    try {
      // Simulate loading animation
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const response = await api.computeBlastRadius({
        repo_path: repoPath,
        failure_mode: failureMode,
        failed_service: failureMode === "specific" ? specificTarget : undefined,
      });

      if (response.success) {
        setResult(response);
        setAnimating(false);
      } else {
        setError(response.message || "Failed to compute blast radius");
        setAnimating(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setAnimating(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Blast Radius Intelligence</h1>
        <p className="text-gray-400">
          Simulate cascading failures and analyze operational impact
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
        {/* Repository Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Repository Path
          </label>
          <div className="relative">
            <GitBranch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="demo-repos/payment-system or GitHub URL"
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Local path or GitHub URL
          </p>
        </div>

        {/* Failure Mode Selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Failure Simulation Mode
          </label>
          <div className="space-y-3">
            {/* Auto Mode */}
            <label className="flex items-start gap-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg cursor-pointer hover:border-blue-500/50 transition-colors">
              <input
                type="radio"
                name="failureMode"
                value="auto"
                checked={failureMode === "auto"}
                onChange={(e) => handleModeChange(e.target.value)}
                className="mt-1 w-4 h-4 text-blue-500 focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 text-white font-medium">
                  <span>🤖</span>
                  <span>Auto (Recommended)</span>
                  {failureMode === "auto" && (
                    <span className="ml-auto text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mt-1">
                  Automatically select the most critical component
                </p>
              </div>
            </label>

            {/* All Mode */}
            <label className="flex items-start gap-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg cursor-pointer hover:border-blue-500/50 transition-colors">
              <input
                type="radio"
                name="failureMode"
                value="all"
                checked={failureMode === "all"}
                onChange={(e) => handleModeChange(e.target.value)}
                className="mt-1 w-4 h-4 text-blue-500 focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 text-white font-medium">
                  <span>🌐</span>
                  <span>Entire System</span>
                  {failureMode === "all" && (
                    <span className="ml-auto text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mt-1">
                  Simulate platform-wide failure
                </p>
              </div>
            </label>

            {/* Specific Mode */}
            <label className="flex items-start gap-3 p-4 bg-gray-800/50 border border-gray-700 rounded-lg cursor-pointer hover:border-blue-500/50 transition-colors">
              <input
                type="radio"
                name="failureMode"
                value="specific"
                checked={failureMode === "specific"}
                onChange={(e) => handleModeChange(e.target.value)}
                className="mt-1 w-4 h-4 text-blue-500 focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 text-white font-medium">
                  <span>🎯</span>
                  <span>Select Component</span>
                  {failureMode === "specific" && (
                    <span className="ml-auto text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mt-1">
                  Choose a specific component to fail
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Component Selector (only for specific mode) */}
        {failureMode === "specific" && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select Component
            </label>
            <div className="relative">
              <Target className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <select
                value={specificTarget}
                onChange={(e) => setSpecificTarget(e.target.value)}
                disabled={loadingTargets || availableTargets.length === 0}
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {loadingTargets
                ? "Detecting components..."
                : availableTargets.length === 0
                ? "Enter repository path to detect components"
                : `${availableTargets.length} component(s) detected`}
            </p>
          </div>
        )}

        {/* Simulate Button */}
        <button
          onClick={handleSimulateFailure}
          disabled={loading}
          className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Simulating Failure...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5" />
              Simulate Failure
            </>
          )}
        </button>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">Error</p>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}
      </div>

      {/* Loading Animation */}
      {animating && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-12">
          <LoadingState message="Analyzing service dependencies and computing blast radius..." />
        </div>
      )}

      {/* Results */}
      {result && !animating && (
        <>
          {/* Report Header with PDF Download */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">Blast Radius Analysis</h2>
              <p className="text-sm text-gray-400 mt-1">
                Service dependency and failure propagation analysis
              </p>
            </div>
            <PDFDownloadButton
              elementId="blast-radius-report-content"
              filename="Nexus-Blast-Radius-Report.pdf"
              title="Nexus-IntelliBob Blast Radius Analysis"
              variant="primary"
            />
          </div>

          {/* Wrapped Report Content for PDF Export */}
          <div id="blast-radius-report-content" className="space-y-6">
            {/* Impact Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Criticality Score"
              value={result.criticality_score || 0}
              icon={AlertTriangle}
              trend={{
                value: result.criticality_score >= 80 ? "Critical" : "Moderate",
                isPositive: false
              }}
            />
            <MetricCard
              title="Affected Services"
              value={result.affected_services?.length || 0}
              icon={Target}
              trend={{
                value: `${result.affected_services?.length || 0} services`,
                isPositive: false
              }}
            />
            <MetricCard
              title="Revenue Risk"
              value={result.estimated_revenue_risk || "$0"}
              icon={DollarSign}
              trend={{
                value: "Per hour",
                isPositive: false
              }}
            />
            <MetricCard
              title="Customer Impact"
              value={result.affected_services?.length >= 2 ? "High" : "Medium"}
              icon={Users}
              trend={{
                value: result.affected_services?.length >= 2 ? "Platform-wide" : "Partial",
                isPositive: false
              }}
            />
          </div>

          {/* Operational Impact Summary */}
          <div className="bg-gradient-to-br from-red-900/20 to-orange-900/20 border border-red-500/30 rounded-lg p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-red-500/20 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">
                  Operational Impact Assessment
                </h3>
                <p className="text-gray-300 mb-4">
                  {result.estimated_customer_impact}
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm font-medium">
                    {result.failure_type?.replace(/_/g, " ").toUpperCase()}
                  </span>
                  <span className="px-3 py-1 bg-orange-500/20 text-orange-300 rounded-full text-sm font-medium">
                    {result.affected_services?.length || 0} Services Impacted
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Dependency Graph */}
          {result.graph && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-400" />
                Service Dependency Graph
              </h2>
              <BlastGraph
                nodes={result.graph.nodes || []}
                edges={result.graph.edges || []}
                className="h-[600px]"
              />
            </div>
          )}

          {/* Failure Timeline */}
          {result.propagation_chain && result.propagation_chain.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-red-400" />
                Cascading Failure Timeline
              </h2>
              <FailureTimeline events={result.propagation_chain} />
            </div>
          )}

          {/* Containment Recommendations */}
          {result.containment_recommendations && result.containment_recommendations.length > 0 && (
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <Shield className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Containment Recommendations</h3>
                  <p className="text-sm text-gray-400">Immediate actions to mitigate impact</p>
                </div>
              </div>
              <div className="space-y-3">
                {result.containment_recommendations.map((rec: string, index: number) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800/70 transition-colors"
                  >
                    <div className="flex-shrink-0 w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center text-blue-400 text-sm font-semibold mt-0.5">
                      {index + 1}
                    </div>
                    <p className="text-gray-300 text-sm">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          </div>
        </>
      )}
    </div>
  );
}

// Made with Bob
