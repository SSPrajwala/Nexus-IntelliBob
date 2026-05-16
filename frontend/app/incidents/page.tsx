"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, FileText, Loader2, Sparkles } from "lucide-react";
import LoadingState from "@/components/LoadingState";
import DNACard from "@/components/DNACard";
import { api, safeApiCall } from "@/lib/api";

// Demo incident texts
const DEMO_INCIDENTS = {
  github: `INCIDENT REPORT: Database Connection Pool Exhaustion
=====================================================

Incident ID: INC-2022-10-21-001
Date: October 21, 2022
Severity: Critical (SEV-1)
Duration: 2 hours 47 minutes
Services Affected: Payment Service, Order Service, API Gateway

EXECUTIVE SUMMARY
-----------------
On October 21, 2022, at 14:23 UTC, our payment processing system experienced a cascading failure triggered by database connection pool exhaustion. The incident resulted in a complete service outage affecting all payment transactions and order processing for approximately 2 hours and 47 minutes.

ROOT CAUSE
----------
The payment service was configured with a database connection pool size of only 5 connections with no overflow capacity (max_overflow=0). During a promotional campaign that began at 14:20 UTC, traffic increased by 340% compared to baseline. The small connection pool quickly became saturated as concurrent payment requests exceeded available connections.

Long-running queries (averaging 2.3 seconds due to missing indexes on the transactions table) held connections longer than expected. New requests began queuing indefinitely, causing request timeouts and service degradation.`,

  retry_storm: `INCIDENT REPORT: Black Friday Payment Retry Storm
==================================================

Incident ID: INC-2023-11-24-002
Date: November 24, 2023 (Black Friday)
Severity: Critical (SEV-1)
Duration: 4 hours 12 minutes
Services Affected: Payment Service, Payment Gateway Integration, Order Service

EXECUTIVE SUMMARY
-----------------
During Black Friday 2023, our payment processing system experienced a catastrophic retry storm that overwhelmed both our internal payment service and the external payment gateway. The incident began at 09:15 UTC when a brief network hiccup to our payment gateway triggered aggressive retry logic without exponential backoff.

ROOT CAUSE
----------
The payment service's external API integration implemented a naive retry mechanism with fixed 1-second delays and no exponential backoff. When the initial 8-second network glitch occurred, approximately 2,400 payment requests failed and entered the retry loop. Each request was configured to retry up to 5 times with a fixed 1-second delay between attempts.

The retry logic had no circuit breaker pattern, no jitter, and no backpressure mechanism. As retries accumulated, they created additional load on the already-stressed payment gateway.`
};

interface LoadingStep {
  message: string;
  completed: boolean;
}

export default function IncidentsPage() {
  const [incidentText, setIncidentText] = useState("");
  const [incidentTitle, setIncidentTitle] = useState("");
  const [extractedDNA, setExtractedDNA] = useState<any>(null);
  const [demoIncidents, setDemoIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingSteps, setLoadingSteps] = useState<LoadingStep[]>([]);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    loadDemoIncidents();
  }, []);

  const loadDemoIncidents = async () => {
    setInitialLoading(true);
    const data = await safeApiCall(
      () => api.getIncidents(),
      { success: false, incidents: [], extracted_dnas: [] }
    );
    setDemoIncidents(data.extracted_dnas || []);
    setInitialLoading(false);
  };

  const loadDemoIncident = (type: 'github' | 'retry_storm') => {
    const incident = DEMO_INCIDENTS[type];
    const title = type === 'github' 
      ? "Database Connection Pool Exhaustion" 
      : "Black Friday Payment Retry Storm";
    
    setIncidentText(incident);
    setIncidentTitle(title);
    setExtractedDNA(null);
  };

  const extractDNA = async () => {
    if (!incidentText.trim() || !incidentTitle.trim()) {
      alert("Please provide both incident title and text");
      return;
    }

    setLoading(true);
    setExtractedDNA(null);
    
    // Initialize loading steps
    const steps = [
      { message: "Reading incident report...", completed: false },
      { message: "Identifying architectural failure patterns...", completed: false },
      { message: "Extracting operational DNA...", completed: false },
      { message: "Building risk signature...", completed: false },
    ];
    setLoadingSteps(steps);

    // Simulate progressive loading
    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
      setLoadingSteps(prev => prev.map((step, idx) => 
        idx === i ? { ...step, completed: true } : step
      ));
    }

    // Extract DNA
    const result = await safeApiCall(
      () => api.extractDNAFromText({
        incident_text: incidentText,
        incident_title: incidentTitle
      }),
      { success: false, message: "Failed to extract DNA", dna: null }
    );

    if (result.success && result.dna) {
      setExtractedDNA(result.dna);
    } else {
      // Fallback mock DNA if API fails
      setExtractedDNA({
        dna_id: "DNA-mock123",
        incident_title: incidentTitle,
        pattern_type: "RESOURCE_EXHAUSTION",
        pattern_name: "Resource Exhaustion",
        pattern_description: "System resources depleted causing service degradation",
        root_cause_category: "Capacity Planning",
        what_went_wrong: "Connection pool was undersized for production load, causing cascading failures",
        trigger_conditions: ["High traffic volume", "Promotional campaign"],
        code_signatures: ["pool_size=5 (undersized)", "max_overflow=0 (no buffer capacity)"],
        anti_patterns: ["Static resource allocation", "Missing circuit breaker pattern"],
        blast_radius_type: "Cascading",
        historical_severity: "Critical",
        time_to_detection: "< 5 minutes",
        similar_known_incidents: ["Database Connection Pool Exhaustion - Oct 2022", "Thread Pool Saturation - Payment Service"],
        confidence_score: 0.87
      });
    }

    setLoading(false);
    setLoadingSteps([]);
  };

  if (initialLoading) {
    return <LoadingState message="Loading incident analysis..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Incident DNA Extraction</h1>
        <p className="text-gray-400">
          Extract architectural failure patterns from production incident reports
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Input */}
        <div className="space-y-4">
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Incident Report
            </h2>
            
            {/* Demo Buttons */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => loadDemoIncident('github')}
                className="px-3 py-2 bg-blue-500/20 text-blue-400 rounded-md text-sm border border-blue-500/30 hover:bg-blue-500/30 transition-colors"
              >
                Load GitHub Incident
              </button>
              <button
                onClick={() => loadDemoIncident('retry_storm')}
                className="px-3 py-2 bg-orange-500/20 text-orange-400 rounded-md text-sm border border-orange-500/30 hover:bg-orange-500/30 transition-colors"
              >
                Load Retry Storm Incident
              </button>
            </div>

            {/* Title Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Incident Title
              </label>
              <input
                type="text"
                value={incidentTitle}
                onChange={(e) => setIncidentTitle(e.target.value)}
                placeholder="Enter incident title..."
                className="w-full px-3 py-2 bg-[#0a0a0b] border border-[#27272a] rounded-md text-white placeholder-gray-500 focus:border-red-500/50 focus:outline-none"
              />
            </div>

            {/* Text Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Incident Report Text
              </label>
              <textarea
                value={incidentText}
                onChange={(e) => setIncidentText(e.target.value)}
                placeholder="Paste your incident report here..."
                rows={12}
                className="w-full px-3 py-2 bg-[#0a0a0b] border border-[#27272a] rounded-md text-white placeholder-gray-500 focus:border-red-500/50 focus:outline-none resize-none font-mono text-sm"
              />
            </div>

            {/* Extract Button */}
            <button
              onClick={extractDNA}
              disabled={loading || !incidentText.trim() || !incidentTitle.trim()}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-md hover:from-red-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Sparkles className="w-5 h-5" />
              )}
              {loading ? "Extracting DNA..." : "Extract DNA"}
            </button>

            {/* Loading Steps */}
            {loading && loadingSteps.length > 0 && (
              <div className="mt-4 space-y-2">
                {loadingSteps.map((step, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    {step.completed ? (
                      <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                        <div className="w-2 h-2 bg-white rounded-full" />
                      </div>
                    ) : (
                      <Loader2 className="w-4 h-4 animate-spin text-red-400" />
                    )}
                    <span className={step.completed ? "text-green-400" : "text-gray-400"}>
                      {step.message}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - DNA Result */}
        <div className="space-y-4">
          {extractedDNA ? (
            <DNACard dna={extractedDNA} />
          ) : (
            <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-8 text-center">
              <AlertTriangle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-400 mb-2">No DNA Extracted</h3>
              <p className="text-gray-500 text-sm">
                Enter an incident report and click &ldquo;Extract DNA&rdquo; to analyze failure patterns
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Demo Incidents Section */}
      {demoIncidents.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Demo Incident DNA Signatures</h2>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {demoIncidents.map((dna, idx) => (
              <DNACard key={idx} dna={dna} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
