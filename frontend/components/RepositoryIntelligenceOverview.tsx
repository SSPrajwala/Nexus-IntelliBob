"use client";

import {
  GitBranch,
  Database,
  Zap,
  AlertTriangle,
  TrendingUp,
  Server,
  Code,
  Package,
} from "lucide-react";

interface RepositoryIntelligenceOverviewProps {
  data: {
    repository_metadata: {
      owner: string;
      repo_name: string;
      url: string;
      size_mb: number;
      file_count: number;
      detected_languages: Record<string, number>;
      frameworks: string[];
      estimated_service_count: number;
    };
    architecture_summary: {
      summary: string;
      services: Array<{
        name: string;
        path: string;
        entry_point: string;
        type: string;
      }>;
      databases: string[];
      queues: string[];
      external_integrations: string[];
      complexity_score: number;
      topology: {
        total_services: number;
        service_types: Record<string, number>;
        architecture_pattern: string;
        service_list: string[];
      };
    };
    risk_summary: {
      total_risks: number;
      critical_risks: number;
      high_risks: number;
      medium_risks: number;
      low_risks: number;
      files_scanned: number;
    };
    engineering_risk_profile: {
      total_risks: number;
      risks: Array<{
        type: string;
        severity: string;
        description: string;
      }>;
      overall_risk_level: string;
    };
  };
}

export default function RepositoryIntelligenceOverview({
  data,
}: RepositoryIntelligenceOverviewProps) {
  const { repository_metadata, architecture_summary, risk_summary, engineering_risk_profile } = data;

  // Calculate top languages
  const topLanguages = Object.entries(repository_metadata.detected_languages)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  const totalFiles = Object.values(repository_metadata.detected_languages).reduce(
    (sum, count) => sum + count,
    0
  );

  // Risk level color
  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "critical":
        return "text-red-500 bg-red-500/10 border-red-500/20";
      case "high":
        return "text-orange-500 bg-orange-500/10 border-orange-500/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      default:
        return "text-blue-500 bg-blue-500/10 border-blue-500/20";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <GitBranch className="w-6 h-6 text-red-500" />
              <h2 className="text-2xl font-bold text-white">
                {repository_metadata.owner}/{repository_metadata.repo_name}
              </h2>
            </div>
            <p className="text-gray-400 mb-4">
              {architecture_summary.summary}
            </p>
            <a
              href={repository_metadata.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-red-400 hover:text-red-300 transition-colors"
            >
              View on GitHub →
            </a>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white mb-1">
              {architecture_summary.complexity_score}
            </div>
            <div className="text-sm text-gray-400">Complexity Score</div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Repository Size */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Package className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-gray-400">Repository Size</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {repository_metadata.size_mb.toFixed(1)} MB
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {repository_metadata.file_count.toLocaleString()} files
          </div>
        </div>

        {/* Services */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <Server className="w-5 h-5 text-purple-500" />
            <span className="text-sm text-gray-400">Services</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {architecture_summary.topology.total_services}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {architecture_summary.topology.architecture_pattern}
          </div>
        </div>

        {/* Total Risks */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <span className="text-sm text-gray-400">Total Risks</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {risk_summary.total_risks}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {risk_summary.critical_risks} critical
          </div>
        </div>

        {/* Risk Level */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-400">Risk Level</span>
          </div>
          <div className="text-2xl font-bold text-white uppercase">
            {engineering_risk_profile.overall_risk_level}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {engineering_risk_profile.total_risks} patterns detected
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Languages */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <Code className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-white">
              Detected Languages
            </h3>
          </div>
          <div className="space-y-3">
            {topLanguages.map(([lang, count]) => {
              const percentage = ((count / totalFiles) * 100).toFixed(1);
              return (
                <div key={lang}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-300">{lang}</span>
                    <span className="text-xs text-gray-500">
                      {percentage}% ({count} files)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-[#27272a] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Frameworks & Technologies */}
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-white">
              Frameworks & Technologies
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {repository_metadata.frameworks.map((framework) => (
              <span
                key={framework}
                className="px-3 py-1 bg-yellow-500/10 border border-yellow-500/20 rounded-full text-sm text-yellow-400"
              >
                {framework}
              </span>
            ))}
            {repository_metadata.frameworks.length === 0 && (
              <span className="text-sm text-gray-500">
                No frameworks detected
              </span>
            )}
          </div>

          {/* Databases */}
          {architecture_summary.databases.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-400">Databases</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {architecture_summary.databases.map((db) => (
                  <span
                    key={db}
                    className="px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full text-sm text-green-400"
                  >
                    {db}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Queues */}
          {architecture_summary.queues.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-purple-500" />
                <span className="text-sm text-gray-400">Message Queues</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {architecture_summary.queues.map((queue) => (
                  <span
                    key={queue}
                    className="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-sm text-purple-400"
                  >
                    {queue}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Services List */}
      {architecture_summary.services.length > 0 && (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <Server className="w-5 h-5 text-purple-500" />
            <h3 className="text-lg font-semibold text-white">
              Detected Services
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {architecture_summary.services.map((service) => (
              <div
                key={service.name}
                className="bg-[#0a0a0f] border border-[#27272a] rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{service.name}</span>
                  <span className="text-xs px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-purple-400">
                    {service.type}
                  </span>
                </div>
                <div className="text-xs text-gray-500">{service.path}</div>
                <div className="text-xs text-gray-600 mt-1">
                  Entry: {service.entry_point}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Engineering Risks */}
      {engineering_risk_profile.risks.length > 0 && (
        <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            <h3 className="text-lg font-semibold text-white">
              Engineering Risk Patterns
            </h3>
          </div>
          <div className="space-y-3">
            {engineering_risk_profile.risks.map((risk, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border ${getRiskColor(
                  risk.severity
                )}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{risk.type}</span>
                  <span className="text-xs uppercase font-semibold">
                    {risk.severity}
                  </span>
                </div>
                <p className="text-sm opacity-90">{risk.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob