"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import {
  Zap,
  Shield,
  AlertTriangle,
  TrendingUp,
  CheckCircle2,
  Sparkles,
  Target,
  Clock,
  DollarSign,
  Server,
  Activity,
} from "lucide-react";
import RepositoryIntelligenceOverview from "./RepositoryIntelligenceOverview";
import RiskMatchCard from "./RiskMatchCard";
import BlastGraph from "./BlastGraph";
import PreMortemReport from "./PreMortemReport";
import EngineeringTimeline from "./EngineeringTimeline";
import ExecutiveIntelCard from "./ExecutiveIntelCard";

type DemoStage =
  | "intro"
  | "loading"
  | "ingestion"
  | "architecture"
  | "scanning"
  | "risks"
  | "blast"
  | "premortem"
  | "timeline"
  | "executive"
  | "finale";

interface DemoData {
  repoAnalysis?: any;
  risks?: any[];
  blastRadius?: any;
  premortem?: any;
  timeline?: any;
}

// Cinematic stage durations (in ms) - moved outside component to avoid recreation
const STAGE_DURATIONS = {
  intro: 3000,
  loading: 2000,
  ingestion: 4000,
  architecture: 6000,
  scanning: 5000,
  risks: 7000,
  blast: 8000,
  premortem: 10000,
  timeline: 8000,
  executive: 10000,
  finale: 0, // Manual control
};

export default function DemoModePlayer() {
  const [stage, setStage] = useState<DemoStage>("intro");
  const [progress, setProgress] = useState(0);
  const [demoData, setDemoData] = useState<DemoData>({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const stageTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const DEMO_REPO_URL = "https://github.com/tiangolo/fastapi";
  const DEMO_SERVICE = "main";

  const startDemo = async () => {
    setIsPlaying(true);
    setStage("intro");
    setProgress(0);
    setError(null);
    setDemoData({});
  };

  const stopDemo = () => {
    setIsPlaying(false);
    const timeout = stageTimeoutRef.current;
    if (timeout) {
      clearTimeout(timeout);
    }
  };

  const resetDemo = () => {
    stopDemo();
    setStage("intro");
    setProgress(0);
    setDemoData({});
    setError(null);
  };

  // Auto-progress through stages
  useEffect(() => {
    if (!isPlaying) return;

    const executeStage = async () => {
      try {
        switch (stage) {
          case "intro":
            // Cinematic intro
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.intro));
            setStage("loading");
            break;

          case "loading":
            // Loading animation
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.loading));
            setStage("ingestion");
            break;

          case "ingestion":
            // Start repository analysis
            setProgress(10);
            const analysisResult = await api.analyzeGithubRepository({
              repo_url: DEMO_REPO_URL,
              failed_service: DEMO_SERVICE,
            });
            setDemoData((prev) => ({ ...prev, repoAnalysis: analysisResult }));
            setProgress(100);
            await new Promise((resolve) => setTimeout(resolve, 2000));
            setStage("architecture");
            break;

          case "architecture":
            // Show architecture intelligence
            setProgress(0);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.architecture));
            setStage("scanning");
            break;

          case "scanning":
            // Scanning animation
            setProgress(0);
            const scanInterval = setInterval(() => {
              setProgress((p) => Math.min(p + 10, 100));
            }, 500);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.scanning));
            clearInterval(scanInterval);
            setStage("risks");
            break;

          case "risks":
            // Show risk matches
            setProgress(0);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.risks));
            setStage("blast");
            break;

          case "blast":
            // Show blast radius
            setProgress(0);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.blast));
            setStage("premortem");
            break;

          case "premortem":
            // Show pre-mortem report
            setProgress(0);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.premortem));
            setStage("timeline");
            break;

          case "timeline":
            // Show engineering timeline
            setProgress(0);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.timeline));
            setStage("executive");
            break;

          case "executive":
            // Show executive summary
            setProgress(0);
            await new Promise((resolve) => setTimeout(resolve, STAGE_DURATIONS.executive));
            setStage("finale");
            break;

          case "finale":
            // Final screen - stay here
            setIsPlaying(false);
            break;
        }
      } catch (err) {
        console.error("Demo stage error:", err);
        setError(err instanceof Error ? err.message : "An error occurred");
        setIsPlaying(false);
      }
    };

    executeStage();

    // Cleanup function with safe ref handling
    return () => {
      const timeout = stageTimeoutRef.current;
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, [stage, isPlaying]);

  // Render stage content
  const renderStageContent = () => {
    switch (stage) {
      case "intro":
        return <IntroStage />;
      case "loading":
        return <LoadingStage />;
      case "ingestion":
        return <IngestionStage progress={progress} />;
      case "architecture":
        return demoData.repoAnalysis ? (
          <ArchitectureStage data={demoData.repoAnalysis} />
        ) : (
          <LoadingStage />
        );
      case "scanning":
        return <ScanningStage progress={progress} />;
      case "risks":
        return demoData.repoAnalysis ? (
          <RisksStage data={demoData.repoAnalysis} />
        ) : (
          <LoadingStage />
        );
      case "blast":
        return demoData.repoAnalysis?.blast_radius ? (
          <BlastStage data={demoData.repoAnalysis.blast_radius} />
        ) : (
          <LoadingStage />
        );
      case "premortem":
        return demoData.repoAnalysis?.premortem_report ? (
          <PreMortemStage data={demoData.repoAnalysis.premortem_report} />
        ) : (
          <LoadingStage />
        );
      case "timeline":
        return demoData.repoAnalysis ? (
          <TimelineStage repoPath={DEMO_REPO_URL} service={DEMO_SERVICE} />
        ) : (
          <LoadingStage />
        );
      case "executive":
        return demoData.repoAnalysis ? (
          <ExecutiveStage data={demoData.repoAnalysis} />
        ) : (
          <LoadingStage />
        );
      case "finale":
        return <FinaleStage onReplay={resetDemo} />;
      default:
        return <LoadingStage />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Control Bar */}
      {!isPlaying && stage === "intro" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0a0a0f]">
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h1 className="text-6xl font-bold bg-gradient-to-r from-red-500 via-orange-500 to-red-500 bg-clip-text text-transparent">
                NEXUS
              </h1>
              <p className="text-2xl text-gray-400">Intelligence Demo</p>
            </div>
            <button
              onClick={startDemo}
              className="px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-red-500/50 transition-all"
            >
              Start Cinematic Demo
            </button>
          </div>
        </div>
      )}

      {/* Demo Content */}
      {isPlaying || stage !== "intro" ? (
        <div className="relative">
          {/* Progress Indicator */}
          {stage !== "finale" && (
            <div className="fixed top-0 left-0 right-0 z-40 h-1 bg-[#18181b]">
              <div
                className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-300"
                style={{
                  width: `${
                    (Object.keys(STAGE_DURATIONS).indexOf(stage) /
                      (Object.keys(STAGE_DURATIONS).length - 1)) *
                    100
                  }%`,
                }}
              />
            </div>
          )}

          {/* Stage Content */}
          <div className="pt-8">{renderStageContent()}</div>

          {/* Control Buttons */}
          {stage !== "intro" && (
            <div className="fixed bottom-8 right-8 z-40 flex gap-4">
              {isPlaying && (
                <button
                  onClick={stopDemo}
                  className="px-6 py-3 bg-[#18181b] border border-[#27272a] rounded-lg hover:bg-[#27272a] transition-colors"
                >
                  Pause
                </button>
              )}
              <button
                onClick={resetDemo}
                className="px-6 py-3 bg-[#18181b] border border-[#27272a] rounded-lg hover:bg-[#27272a] transition-colors"
              >
                Restart
              </button>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="fixed bottom-8 left-8 z-40 max-w-md p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

// Stage Components
function IntroStage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-6 animate-fade-in">
        <Sparkles className="w-20 h-20 mx-auto text-red-500 animate-pulse" />
        <h1 className="text-5xl font-bold">Initializing Intelligence System</h1>
        <p className="text-xl text-gray-400">Nexus AI Platform</p>
      </div>
    </div>
  );
}

function LoadingStage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-6">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-red-500/20 border-t-red-500 rounded-full animate-spin mx-auto" />
          <Zap className="w-8 h-8 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-red-500" />
        </div>
        <p className="text-xl text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

function IngestionStage({ progress }: { progress: number }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center space-y-4">
          <Activity className="w-16 h-16 mx-auto text-red-500 animate-pulse" />
          <h2 className="text-4xl font-bold">Repository Ingestion</h2>
          <p className="text-xl text-gray-400">
            Analyzing: github.com/tiangolo/fastapi
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between text-sm text-gray-400">
            <span>Cloning repository...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-3 bg-[#18181b] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-8">
          {["Scanning files", "Detecting patterns", "Building graph"].map(
            (label, i) => (
              <div
                key={i}
                className="p-4 bg-[#18181b] border border-[#27272a] rounded-lg text-center"
              >
                <div className="w-2 h-2 bg-red-500 rounded-full mx-auto mb-2 animate-pulse" />
                <p className="text-sm text-gray-400">{label}</p>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

function ArchitectureStage({ data }: { data: any }) {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4 mb-12">
          <Server className="w-16 h-16 mx-auto text-purple-500" />
          <h2 className="text-4xl font-bold">Architecture Intelligence</h2>
          <p className="text-xl text-gray-400">
            Discovered system topology and dependencies
          </p>
        </div>

        <RepositoryIntelligenceOverview data={data} />
      </div>
    </div>
  );
}

function ScanningStage({ progress }: { progress: number }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center space-y-4">
          <Shield className="w-16 h-16 mx-auto text-orange-500 animate-pulse" />
          <h2 className="text-4xl font-bold">Risk Intelligence Scanning</h2>
          <p className="text-xl text-gray-400">
            Correlating incident DNA with codebase patterns
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between text-sm text-gray-400">
            <span>Scanning for vulnerabilities...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-3 bg-[#18181b] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-orange-500 to-red-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {[
            "Retry patterns",
            "Circuit breakers",
            "Database connections",
            "Error handling",
          ].map((pattern, i) => (
            <div
              key={i}
              className="p-4 bg-[#18181b] border border-orange-500/20 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
                <span className="text-sm text-gray-300">{pattern}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RisksStage({ data }: { data: any }) {
  const topRisks = data.risk_summary?.top_risks?.slice(0, 6) || [];

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4 mb-12">
          <AlertTriangle className="w-16 h-16 mx-auto text-orange-500" />
          <h2 className="text-4xl font-bold">Risk Correlation Results</h2>
          <p className="text-xl text-gray-400">
            {data.risk_summary?.total_risks || 0} potential risks identified
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {topRisks.map((risk: any, index: number) => (
            <RiskMatchCard key={index} risk={risk} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
}

function BlastStage({ data }: { data: any }) {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4 mb-12">
          <Target className="w-16 h-16 mx-auto text-red-500" />
          <h2 className="text-4xl font-bold">Blast Radius Simulation</h2>
          <p className="text-xl text-gray-400">
            Cascading failure impact analysis
          </p>
        </div>

        {data.graph && <BlastGraph nodes={data.graph.nodes} edges={data.graph.edges} />}

        <div className="grid grid-cols-3 gap-6 mt-8">
          <div className="p-6 bg-[#18181b] border border-red-500/20 rounded-lg text-center">
            <div className="text-3xl font-bold text-red-500 mb-2">
              {data.affected_services?.length || 0}
            </div>
            <div className="text-sm text-gray-400">Services at Risk</div>
          </div>
          <div className="p-6 bg-[#18181b] border border-orange-500/20 rounded-lg text-center">
            <div className="text-3xl font-bold text-orange-500 mb-2">
              {data.criticality_score || 0}
            </div>
            <div className="text-sm text-gray-400">Criticality Score</div>
          </div>
          <div className="p-6 bg-[#18181b] border border-yellow-500/20 rounded-lg text-center">
            <div className="text-3xl font-bold text-yellow-500 mb-2">
              {data.estimated_customer_impact || "High"}
            </div>
            <div className="text-sm text-gray-400">Customer Impact</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PreMortemStage({ data }: { data: any }) {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4 mb-12">
          <Clock className="w-16 h-16 mx-auto text-yellow-500" />
          <h2 className="text-4xl font-bold">Pre-Mortem Intelligence</h2>
          <p className="text-xl text-gray-400">
            Predicting the incident before it happens
          </p>
        </div>

        <PreMortemReport report={data} />
      </div>
    </div>
  );
}

function TimelineStage({
  repoPath,
  service,
}: {
  repoPath: string;
  service: string;
}) {
  const [timelineData, setTimelineData] = useState<any>(null);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const result = await api.generateEngineeringTimeline({
          repo_path: repoPath,
          failed_service: service,
        });
        setTimelineData(result);
      } catch (err) {
        console.error("Timeline fetch error:", err);
      }
    };
    fetchTimeline();
  }, [repoPath, service]);

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4 mb-12">
          <TrendingUp className="w-16 h-16 mx-auto text-blue-500" />
          <h2 className="text-4xl font-bold">Engineering Timeline</h2>
          <p className="text-xl text-gray-400">
            Evolution of engineering decisions leading to failure
          </p>
        </div>

        {timelineData?.timeline ? (
          <EngineeringTimeline events={timelineData.timeline} />
        ) : (
          <LoadingStage />
        )}
      </div>
    </div>
  );
}

function ExecutiveStage({ data }: { data: any }) {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4 mb-12">
          <Sparkles className="w-16 h-16 mx-auto text-purple-500" />
          <h2 className="text-4xl font-bold">Executive Intelligence</h2>
          <p className="text-xl text-gray-400">
            Strategic insights for leadership
          </p>
        </div>

        <ExecutiveIntelCard
          summary={{
            reliability_maturity_score: 65,
            maturity_level: "Developing",
            maturity_color: "yellow",
            risk_posture: "ELEVATED",
            risk_posture_description:
              "Multiple critical patterns detected requiring immediate attention",
            most_dangerous_hidden_risk: {
              title: "Cascading Database Connection Exhaustion",
              description:
                "Connection pool saturation could trigger system-wide failure",
              why_hidden:
                "No monitoring on connection pool metrics across services",
              blast_radius: "All dependent services",
              estimated_impact: "$2.5M/hour revenue loss",
              detection_difficulty: "High - requires distributed tracing",
            },
            strategic_recommendation:
              "Implement circuit breakers and connection pool monitoring immediately",
            key_metrics: {
              total_services_analyzed: data.architecture_summary?.topology
                ?.total_services || 0,
              services_at_risk: data.blast_radius?.affected_services?.length || 0,
              critical_risks_found: data.risk_summary?.critical_risks || 0,
              estimated_time_to_incident: "14-21 days",
              blast_radius_score: data.blast_radius?.criticality_score || 0,
              confidence_level: 87,
            },
            organizational_risks: [
              "Insufficient error handling patterns",
              "Missing circuit breaker implementations",
              "Inadequate connection pool management",
            ],
            executive_summary:
              "System exhibits elevated risk posture with multiple critical vulnerabilities requiring immediate remediation.",
          }}
        />
      </div>
    </div>
  );
}

function FinaleStage({ onReplay }: { onReplay: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-4xl w-full text-center space-y-12">
        <div className="space-y-6">
          <CheckCircle2 className="w-24 h-24 mx-auto text-green-500" />
          <h1 className="text-6xl font-bold bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent">
            Incident Prevented
          </h1>
          <p className="text-2xl text-gray-400">
            NEXUS identified and prevented the next major outage
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-lg">
            <DollarSign className="w-8 h-8 mx-auto text-green-500 mb-3" />
            <div className="text-3xl font-bold text-white mb-2">$2.5M</div>
            <div className="text-sm text-gray-400">Revenue Protected</div>
          </div>

          <div className="p-6 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-lg">
            <Server className="w-8 h-8 mx-auto text-blue-500 mb-3" />
            <div className="text-3xl font-bold text-white mb-2">12</div>
            <div className="text-sm text-gray-400">Services Secured</div>
          </div>

          <div className="p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-lg">
            <Clock className="w-8 h-8 mx-auto text-purple-500 mb-3" />
            <div className="text-3xl font-bold text-white mb-2">4.5hrs</div>
            <div className="text-sm text-gray-400">Outage Avoided</div>
          </div>

          <div className="p-6 bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-lg">
            <TrendingUp className="w-8 h-8 mx-auto text-orange-500 mb-3" />
            <div className="text-3xl font-bold text-white mb-2">99.99%</div>
            <div className="text-sm text-gray-400">Reliability Target</div>
          </div>
        </div>

        <div className="p-8 bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-lg">
          <p className="text-xl text-gray-300 italic">
            &ldquo;NEXUS prevented the next incident before it happened.&rdquo;
          </p>
        </div>

        <button
          onClick={onReplay}
          className="px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg font-semibold text-lg hover:shadow-lg hover:shadow-red-500/50 transition-all"
        >
          Replay Demo
        </button>
      </div>
    </div>
  );
}

// Made with Bob