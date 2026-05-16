"use client";

import { ExecutiveSummary } from "@/types";
import { Shield, AlertTriangle, TrendingUp, Target, Brain, Zap } from "lucide-react";
import { motion } from "framer-motion";

interface ExecutiveIntelCardProps {
  summary: ExecutiveSummary;
}

const maturityColorMap: Record<string, string> = {
  green: "from-green-500/20 to-emerald-500/20 border-green-500/30 text-green-400",
  yellow: "from-yellow-500/20 to-amber-500/20 border-yellow-500/30 text-yellow-400",
  orange: "from-orange-500/20 to-red-500/20 border-orange-500/30 text-orange-400",
  red: "from-red-500/20 to-pink-500/20 border-red-500/30 text-red-400",
};

const riskPostureConfig: Record<string, { color: string; icon: any }> = {
  CRITICAL: { color: "text-red-400", icon: AlertTriangle },
  HIGH: { color: "text-orange-400", icon: Zap },
  ELEVATED: { color: "text-yellow-400", icon: TrendingUp },
  MODERATE: { color: "text-blue-400", icon: Shield },
};

export default function ExecutiveIntelCard({ summary }: ExecutiveIntelCardProps) {
  const maturityColorClass = maturityColorMap[summary.maturity_color] || maturityColorMap.red;
  const RiskIcon = riskPostureConfig[summary.risk_posture]?.icon || AlertTriangle;
  const riskColor = riskPostureConfig[summary.risk_posture]?.color || "text-red-400";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30">
          <Brain className="w-5 h-5 text-indigo-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Executive Intelligence Summary</h2>
          <p className="text-sm text-gray-400">AI-generated strategic risk assessment for leadership</p>
        </div>
      </div>

      {/* Executive Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="rounded-xl border border-indigo-500/30 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-sm p-6 shadow-xl shadow-indigo-500/10"
      >
        <p className="text-gray-300 leading-relaxed">{summary.executive_summary}</p>
      </motion.div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Reliability Maturity Score */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className={`rounded-xl border bg-gradient-to-br ${maturityColorClass} backdrop-blur-sm p-6 shadow-xl`}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                Reliability Maturity
              </p>
              <p className="text-3xl font-bold text-white mt-1">{summary.reliability_maturity_score}</p>
            </div>
            <div className="p-3 rounded-lg bg-white/10">
              <Target className="w-6 h-6 text-white" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-bold ${maturityColorClass.split(" ")[2]}`}>
              {summary.maturity_level}
            </span>
            <span className="text-xs text-gray-400">/ 100</span>
          </div>
          <div className="mt-3 h-2 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${summary.reliability_maturity_score}%` }}
              transition={{ delay: 0.3, duration: 1 }}
              className={`h-full bg-gradient-to-r ${maturityColorClass.split(" ").slice(0, 2).join(" ")}`}
            />
          </div>
        </motion.div>

        {/* Risk Posture */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="rounded-xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-pink-500/10 backdrop-blur-sm p-6 shadow-xl shadow-red-500/10"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Risk Posture</p>
              <p className={`text-2xl font-bold mt-1 ${riskColor}`}>{summary.risk_posture}</p>
            </div>
            <div className="p-3 rounded-lg bg-red-500/20">
              <RiskIcon className={`w-6 h-6 ${riskColor}`} />
            </div>
          </div>
          <p className="text-sm text-gray-300">{summary.risk_posture_description}</p>
        </motion.div>

        {/* Key Metrics */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="rounded-xl border border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-sm p-6 shadow-xl shadow-purple-500/10"
        >
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">
            Critical Metrics
          </p>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Services at Risk</span>
              <span className="text-sm font-bold text-white">
                {summary.key_metrics.services_at_risk} / {summary.key_metrics.total_services_analyzed}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Critical Risks</span>
              <span className="text-sm font-bold text-red-400">
                {summary.key_metrics.critical_risks_found}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Blast Radius</span>
              <span className="text-sm font-bold text-orange-400">
                {summary.key_metrics.blast_radius_score}/100
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-400">Confidence</span>
              <span className="text-sm font-bold text-green-400">
                {Math.round(summary.key_metrics.confidence_level * 100)}%
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Most Dangerous Hidden Risk */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        className="rounded-xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-pink-500/10 backdrop-blur-sm p-6 shadow-xl shadow-red-500/10"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-red-500/20 border border-red-500/30">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Most Dangerous Hidden Risk</h3>
            <p className="text-xs text-gray-400">AI-identified critical vulnerability</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-bold text-red-400 mb-2">
              {summary.most_dangerous_hidden_risk.title}
            </h4>
            <p className="text-sm text-gray-300 leading-relaxed">
              {summary.most_dangerous_hidden_risk.description}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/10">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Why Hidden
              </p>
              <p className="text-sm text-gray-300">{summary.most_dangerous_hidden_risk.why_hidden}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Detection Difficulty
              </p>
              <p className="text-sm text-orange-400 font-bold">
                {summary.most_dangerous_hidden_risk.detection_difficulty}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Blast Radius
              </p>
              <p className="text-sm text-gray-300">{summary.most_dangerous_hidden_risk.blast_radius}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Estimated Impact
              </p>
              <p className="text-sm text-red-400 font-bold">
                {summary.most_dangerous_hidden_risk.estimated_impact}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Strategic Recommendation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="rounded-xl border border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 backdrop-blur-sm p-6 shadow-xl shadow-blue-500/10"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
            <Target className="w-5 h-5 text-blue-400" />
          </div>
          <h3 className="text-lg font-bold text-white">Strategic Recommendation</h3>
        </div>
        <pre className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap font-sans">
          {summary.strategic_recommendation}
        </pre>
      </motion.div>

      {/* Organizational Risks */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
        className="rounded-xl border border-yellow-500/30 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 backdrop-blur-sm p-6 shadow-xl shadow-yellow-500/10"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-yellow-500/20 border border-yellow-500/30">
            <Shield className="w-5 h-5 text-yellow-400" />
          </div>
          <h3 className="text-lg font-bold text-white">Organizational Risk Factors</h3>
        </div>
        <ul className="space-y-2">
          {summary.organizational_risks.map((risk, index) => (
            <li key={index} className="flex items-start gap-3">
              <div className="mt-1 w-1.5 h-1.5 rounded-full bg-yellow-400 flex-shrink-0" />
              <span className="text-sm text-gray-300">{risk}</span>
            </li>
          ))}
        </ul>
      </motion.div>

      {/* Time to Incident */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7, duration: 0.5 }}
        className="rounded-xl border border-red-500/30 bg-gradient-to-br from-red-500/10 to-pink-500/10 backdrop-blur-sm p-4 shadow-xl shadow-red-500/10"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-red-400" />
            <span className="text-sm font-semibold text-gray-300">Estimated Time to Incident:</span>
          </div>
          <span className="text-sm font-bold text-red-400">
            {summary.key_metrics.estimated_time_to_incident}
          </span>
        </div>
      </motion.div>
    </div>
  );
}

// Made with Bob
