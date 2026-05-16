"use client";

import { AlertTriangle, Code, Zap, Target, Clock, TrendingUp } from "lucide-react";

interface DNACardProps {
  dna: {
    dna_id: string;
    incident_title: string;
    pattern_type: string;
    pattern_name: string;
    pattern_description: string;
    root_cause_category: string;
    what_went_wrong: string;
    trigger_conditions: string[];
    code_signatures: string[];
    anti_patterns: string[];
    blast_radius_type: string;
    historical_severity: string;
    time_to_detection: string;
    similar_known_incidents: string[];
    confidence_score?: number;
  };
}

const PATTERN_COLORS: Record<string, string> = {
  RETRY_STORM: "from-orange-500 to-red-500",
  CASCADING_TIMEOUT: "from-yellow-500 to-orange-500",
  RESOURCE_EXHAUSTION: "from-red-500 to-pink-500",
  IMPLICIT_COUPLING: "from-purple-500 to-pink-500",
  CONFIG_DRIFT: "from-blue-500 to-cyan-500",
  SILENT_PARTIAL_FAILURE: "from-gray-500 to-slate-500",
  THUNDERING_HERD: "from-amber-500 to-orange-500",
  DEADLOCK: "from-red-600 to-rose-600",
  BACKPRESSURE_FAILURE: "from-indigo-500 to-purple-500",
  UNKNOWN: "from-gray-600 to-gray-700",
};

const SEVERITY_COLORS: Record<string, string> = {
  Critical: "bg-red-500/20 text-red-400 border-red-500/30",
  High: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  Medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  Low: "bg-blue-500/20 text-blue-400 border-blue-500/30",
};

export default function DNACard({ dna }: DNACardProps) {
  const patternColor = PATTERN_COLORS[dna.pattern_type] || PATTERN_COLORS.UNKNOWN;
  const severityColor = SEVERITY_COLORS[dna.historical_severity] || SEVERITY_COLORS.Medium;

  return (
    <div className="bg-[#18181b] border border-[#27272a] rounded-lg overflow-hidden hover:border-red-500/30 transition-all duration-300 shadow-xl">
      {/* Header with Pattern Badge */}
      <div className={`bg-gradient-to-r ${patternColor} p-6`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="w-6 h-6 text-white" />
              <h2 className="text-2xl font-bold text-white">{dna.pattern_name}</h2>
            </div>
            <p className="text-white/90 text-sm">{dna.pattern_description}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${severityColor}`}>
              {dna.historical_severity}
            </span>
            {dna.confidence_score && (
              <span className="px-3 py-1 bg-white/20 text-white rounded-full text-xs font-semibold">
                {Math.round(dna.confidence_score * 100)}% Match
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* DNA ID and Metadata */}
        <div className="flex items-center justify-between text-xs text-gray-500 pb-4 border-b border-[#27272a]">
          <span className="font-mono">{dna.dna_id}</span>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {dna.time_to_detection}
            </span>
            <span className="flex items-center gap-1">
              <Target className="w-3 h-3" />
              {dna.blast_radius_type}
            </span>
          </div>
        </div>

        {/* What Went Wrong */}
        <div>
          <h3 className="text-sm font-semibold text-red-400 uppercase mb-2 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            What Went Wrong
          </h3>
          <p className="text-gray-300 text-sm leading-relaxed bg-[#0a0a0b] p-4 rounded-lg border border-[#27272a]">
            {dna.what_went_wrong}
          </p>
        </div>

        {/* Root Cause Category */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">
            Root Cause Category
          </h3>
          <span className="inline-block px-3 py-1 bg-purple-500/20 text-purple-400 rounded-md text-sm border border-purple-500/30">
            {dna.root_cause_category}
          </span>
        </div>

        {/* Trigger Conditions */}
        {dna.trigger_conditions && dna.trigger_conditions.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Trigger Conditions
            </h3>
            <div className="flex flex-wrap gap-2">
              {dna.trigger_conditions.map((trigger, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 bg-amber-500/10 text-amber-400 rounded-md text-sm border border-amber-500/20 hover:bg-amber-500/20 transition-colors"
                >
                  {trigger}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Code Signatures */}
        {dna.code_signatures && dna.code_signatures.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
              <Code className="w-4 h-4" />
              Code Signatures
            </h3>
            <div className="space-y-2">
              {dna.code_signatures.map((signature, idx) => (
                <div
                  key={idx}
                  className="font-mono text-xs bg-[#0a0a0b] text-cyan-400 p-3 rounded-md border border-cyan-500/20 hover:border-cyan-500/40 transition-colors"
                >
                  {signature}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Anti-Patterns */}
        {dna.anti_patterns && dna.anti_patterns.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
              Anti-Patterns Detected
            </h3>
            <div className="space-y-2">
              {dna.anti_patterns.map((pattern, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2 text-sm text-gray-300 bg-red-500/5 p-3 rounded-md border border-red-500/20"
                >
                  <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                  <span>{pattern}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Similar Known Incidents */}
        {dna.similar_known_incidents && dna.similar_known_incidents.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Similar Known Incidents
            </h3>
            <div className="space-y-2">
              {dna.similar_known_incidents.map((incident, idx) => (
                <div
                  key={idx}
                  className="text-sm text-gray-400 bg-[#0a0a0b] p-3 rounded-md border border-[#27272a] hover:border-blue-500/30 transition-colors cursor-pointer"
                >
                  {incident}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Made with Bob