"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Plus } from "lucide-react";
import LoadingState from "@/components/LoadingState";
import EmptyState from "@/components/EmptyState";
import { IncidentDNA } from "@/types";
import { api, safeApiCall } from "@/lib/api";
import { SEVERITY_COLORS, STATUS_COLORS } from "@/lib/constants";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentDNA[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    setLoading(true);
    const data = await safeApiCall(
      () => api.getIncidents(),
      { success: false, incidents: [] }
    );
    setIncidents(data.incidents || []);
    setLoading(false);
  };

  if (loading) {
    return <LoadingState message="Loading incidents..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Incidents</h1>
          <p className="text-gray-400">
            Manage and analyze past production incidents
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors">
          <Plus className="w-4 h-4" />
          Add Incident
        </button>
      </div>

      {/* Incidents List */}
      {incidents.length === 0 ? (
        <EmptyState
          icon={AlertTriangle}
          title="No incidents yet"
          description="Start by adding your first incident to extract failure patterns and DNA."
          action={{
            label: "Add Incident",
            onClick: () => console.log("Add incident"),
          }}
        />
      ) : (
        <div className="space-y-4">
          {incidents.map((incident) => (
            <div
              key={incident.id}
              className="bg-[#18181b] border border-[#27272a] rounded-lg p-6 hover:border-red-500/20 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-white">
                      {incident.title}
                    </h3>
                    <span
                      className={`badge ${
                        SEVERITY_COLORS[incident.severity]
                      }`}
                    >
                      {incident.severity.toUpperCase()}
                    </span>
                    <span
                      className={`badge ${STATUS_COLORS[incident.status]}`}
                    >
                      {incident.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-3">
                    {incident.description}
                  </p>
                  {incident.root_cause && (
                    <div className="mb-3">
                      <span className="text-xs font-semibold text-gray-500 uppercase">
                        Root Cause:
                      </span>
                      <p className="text-sm text-gray-300 mt-1">
                        {incident.root_cause}
                      </p>
                    </div>
                  )}
                  {incident.failure_patterns &&
                    incident.failure_patterns.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="text-xs font-semibold text-gray-500 uppercase">
                          Patterns:
                        </span>
                        {incident.failure_patterns.map((pattern, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-[#27272a] text-xs text-gray-300 rounded"
                          >
                            {pattern}
                          </span>
                        ))}
                      </div>
                    )}
                  {incident.affected_components &&
                    incident.affected_components.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs font-semibold text-gray-500 uppercase">
                          Affected:
                        </span>
                        {incident.affected_components.map((component, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-red-500/10 text-xs text-red-400 rounded border border-red-500/20"
                          >
                            {component}
                          </span>
                        ))}
                      </div>
                    )}
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-[#27272a]">
                <span>ID: {incident.incident_id}</span>
                <span>
                  Occurred:{" "}
                  {new Date(incident.occurred_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Made with Bob
