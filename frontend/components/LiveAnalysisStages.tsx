"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Loader2, Circle } from "lucide-react";

export interface AnalysisStage {
  id: string;
  label: string;
  status: "pending" | "active" | "completed" | "error";
  progress?: number;
}

interface LiveAnalysisStagesProps {
  stages: AnalysisStage[];
  currentStage?: number;
}

export default function LiveAnalysisStages({
  stages,
  currentStage = 0,
}: LiveAnalysisStagesProps) {
  const [animatedStages, setAnimatedStages] = useState<AnalysisStage[]>(stages);

  useEffect(() => {
    setAnimatedStages(stages);
  }, [stages]);

  return (
    <div className="bg-gradient-to-br from-[#18181b] to-[#0a0a0f] border border-[#27272a] rounded-lg p-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-full mb-4">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          <span className="text-sm text-red-400 font-medium">
            AI Analysis in Progress
          </span>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Intelligence Extraction
        </h2>
        <p className="text-gray-400">
          Analyzing repository architecture and predicting failure scenarios
        </p>
      </div>

      {/* Stages */}
      <div className="space-y-4">
        {animatedStages.map((stage, index) => (
          <div
            key={stage.id}
            className={`
              relative flex items-start gap-4 p-4 rounded-lg transition-all duration-500
              ${
                stage.status === "active"
                  ? "bg-red-500/5 border border-red-500/20"
                  : stage.status === "completed"
                  ? "bg-green-500/5 border border-green-500/20"
                  : "bg-[#18181b]/50 border border-[#27272a]"
              }
            `}
          >
            {/* Status Icon */}
            <div className="flex-shrink-0 mt-1">
              {stage.status === "completed" ? (
                <CheckCircle2 className="w-6 h-6 text-green-500" />
              ) : stage.status === "active" ? (
                <Loader2 className="w-6 h-6 text-red-500 animate-spin" />
              ) : stage.status === "error" ? (
                <Circle className="w-6 h-6 text-red-500" />
              ) : (
                <Circle className="w-6 h-6 text-gray-600" />
              )}
            </div>

            {/* Stage Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <h3
                  className={`
                  text-base font-semibold
                  ${
                    stage.status === "active"
                      ? "text-red-400"
                      : stage.status === "completed"
                      ? "text-green-400"
                      : "text-gray-400"
                  }
                `}
                >
                  {stage.label}
                </h3>
                {stage.status === "active" && (
                  <span className="text-xs text-gray-500">Processing...</span>
                )}
                {stage.status === "completed" && (
                  <span className="text-xs text-green-500">✓ Complete</span>
                )}
              </div>

              {/* Progress Bar */}
              {stage.status === "active" && (
                <div className="w-full h-1 bg-[#27272a] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-red-500 to-orange-500 transition-all duration-300"
                    style={{
                      width: `${stage.progress || 0}%`,
                    }}
                  />
                </div>
              )}
            </div>

            {/* Connecting Line */}
            {index < animatedStages.length - 1 && (
              <div
                className={`
                absolute left-[1.75rem] top-[3.5rem] w-0.5 h-4
                ${
                  stage.status === "completed"
                    ? "bg-green-500/30"
                    : "bg-[#27272a]"
                }
              `}
              />
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-6 border-t border-[#27272a]">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">
            Stage {currentStage + 1} of {stages.length}
          </span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-gray-400">AI Engine Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob