"use client";

import { motion } from "framer-motion";
import {
  AlertTriangle,
  TrendingDown,
  Clock,
  DollarSign,
  Users,
  Activity,
  Shield,
  Zap,
  Target,
  AlertCircle,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import type { PreMortemReport } from "@/types";

interface PreMortemReportProps {
  report: PreMortemReport;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

const getRiskColor = (level: string) => {
  switch (level) {
    case "CRITICAL":
      return "from-red-600 to-red-800";
    case "HIGH":
      return "from-orange-600 to-orange-800";
    case "MEDIUM":
      return "from-yellow-600 to-yellow-800";
    default:
      return "from-blue-600 to-blue-800";
  }
};

const getRiskGlow = (level: string) => {
  switch (level) {
    case "CRITICAL":
      return "shadow-[0_0_30px_rgba(239,68,68,0.5)]";
    case "HIGH":
      return "shadow-[0_0_30px_rgba(249,115,22,0.5)]";
    case "MEDIUM":
      return "shadow-[0_0_30px_rgba(234,179,8,0.5)]";
    default:
      return "shadow-[0_0_30px_rgba(59,130,246,0.5)]";
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "critical":
      return "text-red-400 bg-red-950/50 border-red-800";
    case "high":
      return "text-orange-400 bg-orange-950/50 border-orange-800";
    case "warning":
      return "text-yellow-400 bg-yellow-950/50 border-yellow-800";
    default:
      return "text-blue-400 bg-blue-950/50 border-blue-800";
  }
};

export default function PreMortemReport({ report }: PreMortemReportProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header Section */}
      <motion.div
        variants={itemVariants}
        className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${getRiskColor(
          report.risk_level
        )} p-8 ${getRiskGlow(report.risk_level)}`}
      >
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <div className="relative">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-8 h-8 text-white" />
              <div>
                <h2 className="text-2xl font-bold text-white">
                  {report.incident_title}
                </h2>
                <p className="text-white/80 text-sm mt-1">
                  Report ID: {report.report_id}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-white font-bold text-lg">
                {report.risk_level} RISK
              </div>
              <div className="text-white/80 text-sm">
                Confidence: {(report.confidence_score * 100).toFixed(0)}%
              </div>
            </div>
          </div>
          <p className="text-white/90 text-lg leading-relaxed">
            {report.executive_summary}
          </p>
        </div>
      </motion.div>

      {/* Key Metrics Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-orange-400" />
            <h3 className="text-gray-300 font-semibold">Time to Incident</h3>
          </div>
          <p className="text-2xl font-bold text-white">
            {report.estimated_time_to_incident}
          </p>
        </div>

        <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-5 h-5 text-red-400" />
            <h3 className="text-gray-300 font-semibold">Revenue at Risk</h3>
          </div>
          <p className="text-2xl font-bold text-white">
            {report.estimated_revenue_loss}
          </p>
        </div>

        <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-yellow-400" />
            <h3 className="text-gray-300 font-semibold">Services at Risk</h3>
          </div>
          <p className="text-2xl font-bold text-white">
            {report.affected_services.length}
          </p>
        </div>
      </motion.div>

      {/* Failure Scenario */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-red-400" />
          <h3 className="text-xl font-bold text-white">Probable Failure Scenario</h3>
        </div>
        <div className="prose prose-invert max-w-none">
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">
            {report.probable_failure_scenario}
          </p>
        </div>
      </motion.div>

      {/* Root Cause */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="w-6 h-6 text-orange-400" />
          <h3 className="text-xl font-bold text-white">Likely Root Cause</h3>
        </div>
        <p className="text-gray-300 leading-relaxed">{report.likely_root_cause}</p>
      </motion.div>

      {/* Outage Timeline */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-6 h-6 text-blue-400" />
          <h3 className="text-xl font-bold text-white">Predicted Outage Timeline</h3>
        </div>
        <div className="space-y-4">
          {report.outage_timeline.map((event, index) => (
            <div key={index} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div
                  className={`w-3 h-3 rounded-full ${
                    event.severity === "critical"
                      ? "bg-red-500"
                      : event.severity === "high"
                      ? "bg-orange-500"
                      : "bg-yellow-500"
                  }`}
                />
                {index < report.outage_timeline.length - 1 && (
                  <div className="w-0.5 h-full bg-gray-700 mt-2" />
                )}
              </div>
              <div className="flex-1 pb-6">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-gray-400 font-mono text-sm">{event.time}</span>
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(
                      event.severity
                    )}`}
                  >
                    {event.event}
                  </span>
                </div>
                <p className="text-gray-300 text-sm">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Customer & Business Impact */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Users className="w-6 h-6 text-purple-400" />
            <h3 className="text-xl font-bold text-white">Customer Impact</h3>
          </div>
          <p className="text-gray-300 leading-relaxed">{report.customer_impact}</p>
        </motion.div>

        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <TrendingDown className="w-6 h-6 text-red-400" />
            <h3 className="text-xl font-bold text-white">Business Impact</h3>
          </div>
          <div className="space-y-2">
            {Object.entries(report.business_impact).map(([key, value]) => (
              <div key={key} className="flex justify-between items-start">
                <span className="text-gray-400 text-sm capitalize">
                  {key.replace(/_/g, " ")}:
                </span>
                <span className="text-gray-200 text-sm font-semibold text-right ml-4">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Cascading Failure Analysis */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 text-yellow-400" />
          <h3 className="text-xl font-bold text-white">Cascading Failure Analysis</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-gray-400 text-sm mb-1">Propagation Depth</p>
            <p className="text-2xl font-bold text-white">
              {report.cascading_failure_analysis.propagation_depth}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Services at Risk</p>
            <p className="text-2xl font-bold text-white">
              {report.cascading_failure_analysis.total_services_at_risk}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Cascade Velocity</p>
            <p className="text-sm font-semibold text-white">
              {report.cascading_failure_analysis.cascade_velocity}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-sm mb-1">Containment</p>
            <p className="text-sm font-semibold text-orange-400">
              {report.cascading_failure_analysis.containment_difficulty}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Mitigation Steps */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-6 h-6 text-green-400" />
          <h3 className="text-xl font-bold text-white">Immediate Mitigation Steps</h3>
        </div>
        <div className="space-y-3">
          {report.mitigation_steps.map((step, index) => (
            <div key={index} className="flex gap-3 items-start">
              <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <p className="text-gray-300">{step}</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Engineering Recommendations */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Target className="w-6 h-6 text-blue-400" />
          <h3 className="text-xl font-bold text-white">Engineering Recommendations</h3>
        </div>
        <div className="space-y-3">
          {report.engineering_recommendations.map((rec, index) => (
            <div key={index} className="flex gap-3 items-start">
              <div className="w-6 h-6 rounded-full bg-blue-950 border border-blue-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-blue-400 text-xs font-bold">{index + 1}</span>
              </div>
              <p className="text-gray-300">{rec}</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Operational Signals */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-6 h-6 text-cyan-400" />
          <h3 className="text-xl font-bold text-white">Operational Signals to Monitor</h3>
        </div>
        <div className="space-y-3">
          {report.operational_signals_to_monitor.map((signal, index) => (
            <div
              key={index}
              className="bg-gray-950/50 border border-gray-700 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <code className="text-cyan-400 text-sm font-mono">{signal.metric}</code>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    signal.alert_severity === "critical"
                      ? "bg-red-950 text-red-400 border border-red-800"
                      : "bg-yellow-950 text-yellow-400 border border-yellow-800"
                  }`}
                >
                  {signal.alert_severity.toUpperCase()}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm mb-1">
                <span className="text-gray-400">Threshold:</span>
                <code className="text-orange-400">{signal.threshold}</code>
              </div>
              <p className="text-gray-400 text-sm">{signal.description}</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Affected Services */}
      <motion.div
        variants={itemVariants}
        className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <XCircle className="w-6 h-6 text-red-400" />
          <h3 className="text-xl font-bold text-white">Affected Services</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {report.affected_services.map((service, index) => (
            <span
              key={index}
              className={`px-3 py-1 rounded-full text-sm font-semibold ${
                index === 0
                  ? "bg-red-950 text-red-400 border border-red-800"
                  : "bg-orange-950 text-orange-400 border border-orange-800"
              }`}
            >
              {service}
              {index === 0 && " (Epicenter)"}
            </span>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}

// Made with Bob