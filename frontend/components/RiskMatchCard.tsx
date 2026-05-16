"use client";

import { RiskMatch } from "@/types";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  FileCode,
  Target,
  Zap,
  TrendingUp,
} from "lucide-react";

interface RiskMatchCardProps {
  risk: RiskMatch;
  index: number;
}

const severityConfig = {
  critical: {
    color: "red",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/30",
    textColor: "text-red-400",
    glowColor: "shadow-red-500/20",
    icon: AlertTriangle,
  },
  high: {
    color: "orange",
    bgColor: "bg-orange-500/10",
    borderColor: "border-orange-500/30",
    textColor: "text-orange-400",
    glowColor: "shadow-orange-500/20",
    icon: AlertCircle,
  },
  medium: {
    color: "yellow",
    bgColor: "bg-yellow-500/10",
    borderColor: "border-yellow-500/30",
    textColor: "text-yellow-400",
    glowColor: "shadow-yellow-500/20",
    icon: Info,
  },
  low: {
    color: "blue",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/30",
    textColor: "text-blue-400",
    glowColor: "shadow-blue-500/20",
    icon: CheckCircle,
  },
};

export default function RiskMatchCard({ risk, index }: RiskMatchCardProps) {
  const severity = (risk.severity || risk.risk_level) as keyof typeof severityConfig;
  const config = severityConfig[severity] || severityConfig.medium;
  const SeverityIcon = config.icon;
  
  const confidence = risk.confidence || risk.confidence_score || 0;
  const blastRadius = risk.blast_radius_score || 50;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={`
        relative bg-[#18181b] border ${config.borderColor} rounded-lg p-5
        hover:${config.glowColor} hover:shadow-xl transition-all duration-300
        group
      `}
    >
      {/* Glow effect on hover */}
      <div
        className={`
          absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100
          transition-opacity duration-300 blur-xl -z-10
          ${config.bgColor}
        `}
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`${config.bgColor} p-2 rounded-lg`}>
            <SeverityIcon className={`w-5 h-5 ${config.textColor}`} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold uppercase tracking-wider ${config.textColor}`}>
                {severity}
              </span>
              <span className="text-xs text-gray-500">•</span>
              <span className="text-xs text-gray-400 font-mono">
                {risk.risk_type || risk.pattern_matched}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <FileCode className="w-3 h-3 text-gray-500" />
              <span className="text-xs text-gray-400 font-mono">
                {risk.file_path}:{risk.line_number}
              </span>
            </div>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className="flex flex-col items-end gap-1">
          <div className="flex items-center gap-1.5 bg-[#27272a] px-2 py-1 rounded-md">
            <Target className="w-3 h-3 text-cyan-400" />
            <span className="text-xs font-semibold text-cyan-400">
              {Math.round(confidence * 100)}%
            </span>
          </div>
          <span className="text-[10px] text-gray-500">confidence</span>
        </div>
      </div>

      {/* Code Snippet */}
      {risk.matched_code && (
        <div className="mb-4">
          <div className="bg-[#0a0a0f] border border-[#27272a] rounded-md p-3 overflow-x-auto">
            <pre className="text-xs font-mono text-gray-300 whitespace-pre">
              {risk.matched_code}
            </pre>
          </div>
        </div>
      )}

      {/* Explanation */}
      <div className="mb-4">
        <p className="text-sm text-gray-300 leading-relaxed">
          {risk.explanation || risk.description}
        </p>
      </div>

      {/* Metrics Row */}
      <div className="flex items-center gap-4 mb-4 pb-4 border-b border-[#27272a]">
        {/* Blast Radius */}
        <div className="flex items-center gap-2">
          <div className="bg-purple-500/10 p-1.5 rounded">
            <Zap className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <div>
            <div className="text-xs text-gray-500">Blast Radius</div>
            <div className="text-sm font-semibold text-purple-400">
              {blastRadius}/100
            </div>
          </div>
        </div>

        {/* Incident Pattern */}
        {risk.related_incident_pattern && (
          <div className="flex items-center gap-2">
            <div className="bg-red-500/10 p-1.5 rounded">
              <TrendingUp className="w-3.5 h-3.5 text-red-400" />
            </div>
            <div>
              <div className="text-xs text-gray-500">Pattern Match</div>
              <div className="text-xs font-semibold text-red-400 font-mono">
                {risk.related_incident_pattern}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recommendation */}
      {risk.recommendation && (
        <div className="bg-green-500/5 border border-green-500/20 rounded-md p-3">
          <div className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-xs font-semibold text-green-400 mb-1">
                Recommendation
              </div>
              <p className="text-xs text-gray-300 leading-relaxed">
                {risk.recommendation}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Hover indicator */}
      <div
        className={`
          absolute bottom-0 left-0 right-0 h-1 rounded-b-lg
          ${config.bgColor} opacity-0 group-hover:opacity-100
          transition-opacity duration-300
        `}
      />
    </motion.div>
  );
}

// Made with Bob