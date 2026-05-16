"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Github, Sparkles, Zap, Shield, TrendingUp, ArrowRight } from "lucide-react";
import LiveAnalysisStages from "@/components/LiveAnalysisStages";
import RepositoryIntelligenceOverview from "@/components/RepositoryIntelligenceOverview";
import PreMortemReport from "@/components/PreMortemReport";
import BlastGraph from "@/components/BlastGraph";
import EngineeringTimeline from "@/components/EngineeringTimeline";
import ExecutiveIntelCard from "@/components/ExecutiveIntelCard";
import { api } from "@/lib/api";
import { EngineeringTimelineData } from "@/types";

interface AnalysisStage {
  id: string;
  label: string;
  status: "pending" | "active" | "completed" | "error";
  progress?: number;
}

export default function HomePage() {
  const router = useRouter();
  const [repoUrl, setRepoUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [analysisStages, setAnalysisStages] = useState<AnalysisStage[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [timelineData, setTimelineData] = useState<EngineeringTimelineData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const exampleRepos = [
    {
      url: "https://github.com/tiangolo/fastapi",
      name: "FastAPI",
      description: "Modern Python web framework",
    },
    {
      url: "https://github.com/vercel/next.js",
      name: "Next.js",
      description: "React framework for production",
    },
    {
      url: "https://github.com/calcom/cal.com",
      name: "Cal.com",
      description: "Open source scheduling platform",
    },
  ];

  const initializeStages = (): AnalysisStage[] => [
    {
      id: "clone",
      label: "Cloning repository from GitHub",
      status: "pending",
      progress: 0,
    },
    {
      id: "architecture",
      label: "Mapping system architecture and dependencies",
      status: "pending",
      progress: 0,
    },
    {
      id: "graph",
      label: "Learning service dependency graph",
      status: "pending",
      progress: 0,
    },
    {
      id: "patterns",
      label: "Detecting operational anti-patterns",
      status: "pending",
      progress: 0,
    },
    {
      id: "incidents",
      label: "Correlating with historical incident DNA",
      status: "pending",
      progress: 0,
    },
    {
      id: "cascade",
      label: "Simulating cascading failure scenarios",
      status: "pending",
      progress: 0,
    },
    {
      id: "predict",
      label: "Predicting future outage probabilities",
      status: "pending",
      progress: 0,
    },
    {
      id: "report",
      label: "Generating executive intelligence report",
      status: "pending",
      progress: 0,
    },
  ];

  const updateStage = (index: number, status: "active" | "completed", progress?: number) => {
    setAnalysisStages((prev) =>
      prev.map((stage, i) => {
        if (i === index) {
          return { ...stage, status, progress };
        }
        return stage;
      })
    );
  };

  const simulateProgress = async (stageIndex: number, duration: number) => {
    const steps = 20;
    const interval = duration / steps;

    for (let i = 0; i <= steps; i++) {
      await new Promise((resolve) => setTimeout(resolve, interval));
      updateStage(stageIndex, "active", (i / steps) * 100);
    }
  };

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) {
      setError("Please enter a GitHub repository URL");
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setCurrentStage(0);

    const stages = initializeStages();
    setAnalysisStages(stages);

    try {
      // Stage 1: Cloning
      updateStage(0, "active", 0);
      await simulateProgress(0, 1500);
      updateStage(0, "completed", 100);
      setCurrentStage(1);

      // Stage 2: Architecture mapping
      updateStage(1, "active", 0);
      await simulateProgress(1, 2000);
      updateStage(1, "completed", 100);
      setCurrentStage(2);

      // Stage 3: Dependency graph
      updateStage(2, "active", 0);
      await simulateProgress(2, 1800);
      updateStage(2, "completed", 100);
      setCurrentStage(3);

      // Stage 4: Anti-patterns
      updateStage(3, "active", 0);
      await simulateProgress(3, 2200);
      updateStage(3, "completed", 100);
      setCurrentStage(4);

      // Stage 5: Incident correlation
      updateStage(4, "active", 0);
      await simulateProgress(4, 1500);
      updateStage(4, "completed", 100);
      setCurrentStage(5);

      // Stage 6: Cascade simulation
      updateStage(5, "active", 0);
      await simulateProgress(5, 2000);
      updateStage(5, "completed", 100);
      setCurrentStage(6);

      // Stage 7: Prediction
      updateStage(6, "active", 0);
      await simulateProgress(6, 1800);
      updateStage(6, "completed", 100);
      setCurrentStage(7);

      // Stage 8: Report generation (actual API call)
      updateStage(7, "active", 0);

      const result = await api.analyzeGithubRepository({
        repo_url: repoUrl,
      });

      updateStage(7, "completed", 100);
      setAnalysisResult(result);

      // Generate engineering timeline if we have the necessary data
      if (result.success && result.blast_radius?.root_failure_service) {
        try {
          const timelineResult = await api.generateEngineeringTimeline({
            repo_path: repoUrl,
            failed_service: result.blast_radius.root_failure_service,
          });

          if (timelineResult.success && timelineResult.timeline && timelineResult.executive_summary) {
            setTimelineData({
              timeline: timelineResult.timeline,
              executive_summary: timelineResult.executive_summary,
              metadata: timelineResult.metadata || {
                generated_at: new Date().toISOString(),
                repository: repoUrl,
                failed_service: result.blast_radius.root_failure_service,
                total_events: timelineResult.timeline.length,
                analysis_confidence: 0.85,
              },
            });
          }
        } catch (timelineError) {
          console.error("Failed to generate timeline:", timelineError);
          // Don't fail the entire analysis if timeline generation fails
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to analyze repository");
      console.error("Analysis error:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleExampleClick = (url: string) => {
    setRepoUrl(url);
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      {!isAnalyzing && !analysisResult && (
        <div className="relative">
          {/* Animated Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-orange-500/5 rounded-lg" />
          <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />

          <div className="relative bg-gradient-to-br from-[#18181b] to-[#0a0a0f] border border-[#27272a] rounded-lg p-12 text-center">
            {/* Pulsing AI Indicator */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-red-500 rounded-full blur-xl opacity-30 animate-pulse" />
                <div className="relative w-16 h-16 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>

            {/* Heading */}
            <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-white via-red-200 to-orange-200 bg-clip-text text-transparent">
              NEXUS AI Incident Intelligence
            </h1>
            <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
              Analyze any GitHub repository and predict failures before they happen.
              AI-powered architecture analysis, risk detection, and pre-mortem intelligence.
            </p>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8 max-w-4xl mx-auto">
              <div className="bg-[#18181b]/50 border border-[#27272a] rounded-lg p-4">
                <Github className="w-6 h-6 text-red-500 mx-auto mb-2" />
                <div className="text-sm text-gray-300">Repository Analysis</div>
              </div>
              <div className="bg-[#18181b]/50 border border-[#27272a] rounded-lg p-4">
                <Shield className="w-6 h-6 text-orange-500 mx-auto mb-2" />
                <div className="text-sm text-gray-300">Risk Detection</div>
              </div>
              <div className="bg-[#18181b]/50 border border-[#27272a] rounded-lg p-4">
                <Zap className="w-6 h-6 text-yellow-500 mx-auto mb-2" />
                <div className="text-sm text-gray-300">Blast Radius</div>
              </div>
              <div className="bg-[#18181b]/50 border border-[#27272a] rounded-lg p-4">
                <TrendingUp className="w-6 h-6 text-purple-500 mx-auto mb-2" />
                <div className="text-sm text-gray-300">Pre-Mortem Report</div>
              </div>
            </div>

            {/* Input Section */}
            <div className="max-w-3xl mx-auto">
              <div className="flex gap-3 mb-4">
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleAnalyze()}
                  placeholder="https://github.com/username/repository"
                  className="flex-1 px-6 py-4 bg-[#18181b] border border-[#27272a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition-colors"
                />
                <button
                  onClick={handleAnalyze}
                  disabled={!repoUrl.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 text-white font-semibold rounded-lg hover:from-red-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  Start Intelligence Analysis
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>

              {error && (
                <div className="text-red-400 text-sm mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                  {error}
                </div>
              )}

              {/* Example Repositories */}
              <div className="text-left">
                <div className="text-sm text-gray-500 mb-3">Try these examples:</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {exampleRepos.map((repo) => (
                    <button
                      key={repo.url}
                      onClick={() => handleExampleClick(repo.url)}
                      className="text-left p-4 bg-[#18181b]/50 border border-[#27272a] rounded-lg hover:border-red-500/30 transition-colors group"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Github className="w-4 h-4 text-gray-500 group-hover:text-red-500 transition-colors" />
                        <span className="text-sm font-medium text-white">
                          {repo.name}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        {repo.description}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis in Progress */}
      {isAnalyzing && (
        <LiveAnalysisStages stages={analysisStages} currentStage={currentStage} />
      )}

      {/* Analysis Results */}
      {analysisResult && !isAnalyzing && (
        <div className="space-y-8">
          {/* Success Banner */}
          <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              <h2 className="text-2xl font-bold text-white">
                Intelligence Analysis Complete
              </h2>
            </div>
            <p className="text-gray-400">
              Repository analyzed successfully. Review the findings below.
            </p>
          </div>

          {/* Repository Intelligence Overview */}
          <RepositoryIntelligenceOverview data={analysisResult} />

          {/* Blast Radius Visualization */}
          {analysisResult.blast_radius?.graph && (
            <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                Blast Radius Visualization
              </h3>
              <BlastGraph
                nodes={analysisResult.blast_radius.graph.nodes}
                edges={analysisResult.blast_radius.graph.edges}
              />
            </div>
          )}

          {/* Pre-Mortem Report */}
          {analysisResult.premortem_report && (
            <PreMortemReport report={analysisResult.premortem_report} />
          )}

          {/* Engineering Timeline */}
          {timelineData?.timeline && (
            <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
              <EngineeringTimeline events={timelineData.timeline} />
            </div>
          )}

          {/* Executive Intelligence Summary */}
          {timelineData?.executive_summary && (
            <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
              <ExecutiveIntelCard summary={timelineData.executive_summary} />
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => {
                setAnalysisResult(null);
                setTimelineData(null);
                setRepoUrl("");
              }}
              className="px-6 py-3 bg-[#27272a] text-white rounded-lg hover:bg-[#3f3f46] transition-colors"
            >
              Analyze Another Repository
            </button>
            <button
              onClick={() => router.push("/scan")}
              className="px-6 py-3 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg hover:from-red-600 hover:to-orange-600 transition-all"
            >
              View Detailed Risk Scan
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
