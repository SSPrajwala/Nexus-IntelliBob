"use client";

import { TimelineEvent } from "@/types";
import { Clock, AlertTriangle, TrendingUp, Zap, Shield } from "lucide-react";
import { motion } from "framer-motion";

interface EngineeringTimelineProps {
  events: TimelineEvent[];
}

const severityConfig = {
  low: {
    color: "from-blue-500/20 to-blue-600/20",
    border: "border-blue-500/30",
    glow: "shadow-blue-500/20",
    text: "text-blue-400",
    bg: "bg-blue-500/10",
    icon: TrendingUp,
  },
  medium: {
    color: "from-yellow-500/20 to-yellow-600/20",
    border: "border-yellow-500/30",
    glow: "shadow-yellow-500/20",
    text: "text-yellow-400",
    bg: "bg-yellow-500/10",
    icon: AlertTriangle,
  },
  high: {
    color: "from-orange-500/20 to-orange-600/20",
    border: "border-orange-500/30",
    glow: "shadow-orange-500/20",
    text: "text-orange-400",
    bg: "bg-orange-500/10",
    icon: Zap,
  },
  critical: {
    color: "from-red-500/20 to-red-600/20",
    border: "border-red-500/30",
    glow: "shadow-red-500/20",
    text: "text-red-400",
    bg: "bg-red-500/10",
    icon: Shield,
  },
};

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

export default function EngineeringTimeline({ events }: EngineeringTimelineProps) {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
          <Clock className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Engineering Evolution Timeline</h2>
          <p className="text-sm text-gray-400">
            AI-reconstructed system evolution showing risk accumulation over time
          </p>
        </div>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical connector line */}
        <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-purple-500/50 via-pink-500/50 to-red-500/50" />

        {/* Timeline events */}
        <div className="space-y-6">
          {events.map((event, index) => {
            const config = severityConfig[event.severity];
            const Icon = config.icon;
            const isPredicted = event.title.includes("PREDICTED");

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                className="relative pl-16"
              >
                {/* Timeline dot */}
                <div
                  className={`absolute left-3 top-3 w-6 h-6 rounded-full border-2 ${config.border} ${config.bg} flex items-center justify-center ${config.glow} shadow-lg`}
                >
                  <div className={`w-2 h-2 rounded-full ${config.text.replace("text-", "bg-")}`} />
                </div>

                {/* Event card */}
                <motion.div
                  whileHover={{ scale: 1.01, y: -2 }}
                  className={`relative rounded-xl border ${config.border} bg-gradient-to-br ${config.color} backdrop-blur-sm p-6 ${config.glow} shadow-xl transition-all duration-300`}
                >
                  {/* Predicted badge */}
                  {isPredicted && (
                    <div className="absolute -top-3 -right-3 px-3 py-1 rounded-full bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs font-bold shadow-lg animate-pulse">
                      AI PREDICTION
                    </div>
                  )}

                  {/* Header */}
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div className="flex items-start gap-3 flex-1">
                      <div className={`p-2 rounded-lg ${config.bg} border ${config.border}`}>
                        <Icon className={`w-5 h-5 ${config.text}`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-lg font-bold text-white">{event.title}</h3>
                        </div>
                        <p className="text-xs text-gray-400">{formatTimestamp(event.timestamp)}</p>
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${config.bg} border ${config.border}`}>
                      <span className={`text-xs font-semibold ${config.text} uppercase`}>
                        {event.severity}
                      </span>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-gray-300 leading-relaxed mb-4">{event.description}</p>

                  {/* Metadata grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Engineering Decision */}
                    <div className="space-y-1">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                        Engineering Decision
                      </p>
                      <p className="text-sm text-gray-300">{event.engineering_decision}</p>
                    </div>

                    {/* Operational Impact */}
                    <div className="space-y-1">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                        Operational Impact
                      </p>
                      <p className="text-sm text-gray-300">{event.operational_impact}</p>
                    </div>
                  </div>

                  {/* Affected Services */}
                  {event.affected_services.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                        Affected Services
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {event.affected_services.map((service, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-gray-300"
                          >
                            {service}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Confidence Score */}
                  <div className="mt-4 flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${event.confidence_score * 100}%` }}
                        transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
                        className={`h-full bg-gradient-to-r ${config.color.replace("/20", "/60")}`}
                      />
                    </div>
                    <span className="text-xs text-gray-400 font-mono">
                      {Math.round(event.confidence_score * 100)}% confidence
                    </span>
                  </div>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Made with Bob
