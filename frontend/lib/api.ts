import {
  DashboardStats,
  IncidentDNA,
  IngestRepoRequest,
  IngestRepoResponse,
  ExtractDNARequest,
  ExtractDNAResponse,
  ScanRepoRequest,
  ScanRepoResponse,
  BlastRadiusRequest,
  BlastRadiusResponse,
  PreMortemRequest,
  PreMortemResponse,
  PreMortemReport,
  HealthResponse,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : "Unknown error"}`);
  }
}

export const api = {
  // Health check
  health: async (): Promise<HealthResponse> => {
    return fetchApi<HealthResponse>("/health");
  },

  // Dashboard stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    return fetchApi<DashboardStats>("/api/dashboard-stats");
  },

  // Incidents
  getIncidents: async (): Promise<{ success: boolean; incidents: IncidentDNA[]; extracted_dnas?: any[] }> => {
    return fetchApi<{ success: boolean; incidents: IncidentDNA[]; extracted_dnas?: any[] }>("/api/incidents");
  },

  // Extract DNA from text
  extractDNAFromText: async (data: { incident_text: string; incident_title: string }): Promise<{ success: boolean; message: string; dna?: any }> => {
    return fetchApi<{ success: boolean; message: string; dna?: any }>("/api/extract-dna", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Ingest repository
  ingestRepo: async (data: IngestRepoRequest): Promise<IngestRepoResponse> => {
    return fetchApi<IngestRepoResponse>("/api/ingest-repo", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Extract DNA from incident
  extractDNA: async (data: ExtractDNARequest): Promise<ExtractDNAResponse> => {
    return fetchApi<ExtractDNAResponse>("/api/extract-dna", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Scan repository
  scanRepo: async (data: ScanRepoRequest): Promise<ScanRepoResponse> => {
    return fetchApi<ScanRepoResponse>("/api/scan-repo", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Scan repository (enhanced version with detailed risk analysis)
  scanRepository: async (repoPath: string): Promise<ScanRepoResponse> => {
    return fetchApi<ScanRepoResponse>("/api/scan-repo", {
      method: "POST",
      body: JSON.stringify({ repo_path: repoPath }),
    });
  },

  // Calculate blast radius (legacy)
  calculateBlastRadius: async (data: BlastRadiusRequest): Promise<BlastRadiusResponse> => {
    return fetchApi<BlastRadiusResponse>("/api/blast-radius-legacy", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Compute blast radius (new implementation)
  computeBlastRadius: async (data: {
    repo_path: string;
    failed_service: string;
  }): Promise<{
    success: boolean;
    message: string;
    root_failure_service?: string;
    affected_services?: string[];
    criticality_score?: number;
    estimated_customer_impact?: string;
    estimated_revenue_risk?: string;
    propagation_chain?: Array<{
      service: string;
      time_offset: number;
      impact_type: string;
      description: string;
    }>;
    failure_type?: string;
    containment_recommendations?: string[];
    graph?: {
      nodes: Array<{
        id: string;
        label: string;
        status: string;
        criticality: string;
      }>;
      edges: Array<{
        source: string;
        target: string;
        type: string;
      }>;
    };
  }> => {
    return fetchApi("/api/blast-radius", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Generate pre-mortem (legacy)
  generatePreMortemLegacy: async (data: PreMortemRequest): Promise<PreMortemResponse> => {
    return fetchApi<PreMortemResponse>("/api/premortem-legacy", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Generate pre-mortem intelligence report (new comprehensive version)
  generatePreMortem: async (data: {
    repo_path: string;
    failed_service: string;
  }): Promise<{
    success: boolean;
    message: string;
    report?: PreMortemReport;
  }> => {
    return fetchApi("/api/premortem", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Analyze GitHub repository (complete intelligence analysis)
  analyzeGithubRepository: async (data: {
    repo_url: string;
    failed_service?: string;
  }): Promise<{
    success: boolean;
    message: string;
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
      top_risks: any[];
    };
    blast_radius: any;
    premortem_report: any;
    engineering_risk_profile: {
      total_risks: number;
      risks: Array<{
        type: string;
        severity: string;
        description: string;
      }>;
      overall_risk_level: string;
    };
  }> => {
    return fetchApi("/api/analyze-github-repo", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Generate engineering timeline
  generateEngineeringTimeline: async (data: {
    repo_path: string;
    failed_service: string;
  }): Promise<{
    success: boolean;
    message: string;
    timeline?: Array<{
      timestamp: string;
      title: string;
      description: string;
      severity: "low" | "medium" | "high" | "critical";
      affected_services: string[];
      engineering_decision: string;
      operational_impact: string;
      confidence_score: number;
    }>;
    executive_summary?: any;
    metadata?: any;
  }> => {
    return fetchApi("/api/engineering-timeline", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Safe API wrapper with fallback
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  fallback: T
): Promise<T> {
  try {
    return await apiCall();
  } catch (error) {
    console.error("API call failed:", error);
    return fallback;
  }
}

// Made with Bob
