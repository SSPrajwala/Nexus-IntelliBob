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

  // Calculate blast radius
  calculateBlastRadius: async (data: BlastRadiusRequest): Promise<BlastRadiusResponse> => {
    return fetchApi<BlastRadiusResponse>("/api/blast-radius", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Generate pre-mortem
  generatePreMortem: async (data: PreMortemRequest): Promise<PreMortemResponse> => {
    return fetchApi<PreMortemResponse>("/api/premortem", {
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
