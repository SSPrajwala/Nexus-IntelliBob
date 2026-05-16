export type SeverityLevel = "critical" | "high" | "medium" | "low";
export type IncidentStatus = "open" | "investigating" | "resolved" | "closed";

export interface RepoDNA {
  id?: string;
  repo_path: string;
  patterns: string[];
  dependencies: string[];
  architecture_type?: string;
  language_distribution: Record<string, number>;
  complexity_score: number;
  created_at?: string;
}

export interface IncidentDNA {
  id?: string;
  incident_id: string;
  title: string;
  description: string;
  severity: SeverityLevel;
  status: IncidentStatus;
  root_cause?: string;
  failure_patterns: string[];
  affected_components: string[];
  resolution?: string;
  occurred_at: string;
  resolved_at?: string;
  created_at?: string;
  metadata: Record<string, any>;
}

export interface RiskMatch {
  id?: string;
  incident_dna_id: string;
  repo_path: string;
  file_path: string;
  line_number: number;
  pattern_matched: string;
  confidence_score: number;
  risk_level: SeverityLevel;
  description: string;
  recommendation?: string;
  created_at?: string;
}

export interface ScanResult {
  id?: string;
  repo_path: string;
  scan_type: string;
  total_files_scanned: number;
  matches_found: number;
  risk_matches: RiskMatch[];
  scan_duration_seconds: number;
  started_at: string;
  completed_at?: string;
  status: string;
  metadata: Record<string, any>;
}

export interface BlastNode {
  id: string;
  name: string;
  type: string;
  risk_level: SeverityLevel;
  dependencies: string[];
  impact_score: number;
}

export interface BlastRadius {
  id?: string;
  risk_match_id: string;
  epicenter_file: string;
  epicenter_component: string;
  affected_nodes: BlastNode[];
  total_impact_score: number;
  cascade_depth: number;
  estimated_downtime_minutes?: number;
  mitigation_priority: SeverityLevel;
  created_at?: string;
}

export interface PreMortem {
  id?: string;
  blast_radius_id: string;
  title: string;
  executive_summary: string;
  failure_scenario: string;
  impact_analysis: string;
  affected_systems: string[];
  business_impact: string;
  technical_recommendations: string[];
  preventive_actions: string[];
  estimated_cost?: number;
  confidence_level: number;
  created_at?: string;
  metadata: Record<string, any>;
}

export interface DashboardStats {
  total_incidents: number;
  total_scans: number;
  total_risk_matches: number;
  critical_risks: number;
  high_risks: number;
  medium_risks: number;
  low_risks: number;
  avg_confidence_score: number;
  last_scan_time?: string;
  repositories_monitored: number;
}

export interface IngestRepoRequest {
  repo_path: string;
  branch?: string;
}

export interface IngestRepoResponse {
  success: boolean;
  message: string;
  repo_dna_id?: string;
  patterns_found: number;
}

export interface ExtractDNARequest {
  incident_title: string;
  incident_description: string;
  severity: SeverityLevel;
  root_cause?: string;
  affected_components: string[];
}

export interface ExtractDNAResponse {
  success: boolean;
  message: string;
  incident_dna_id?: string;
  patterns_extracted: number;
}

export interface ScanRepoRequest {
  repo_path: string;
  incident_dna_ids?: string[];
}

export interface ScanRepoResponse {
  success: boolean;
  message: string;
  scan_id?: string;
  matches_found: number;
  risk_matches: RiskMatch[];
}

export interface BlastRadiusRequest {
  risk_match_id: string;
}

export interface BlastRadiusResponse {
  success: boolean;
  message: string;
  blast_radius_id?: string;
  blast_radius?: BlastRadius;
}

export interface PreMortemRequest {
  blast_radius_id: string;
}

export interface PreMortemResponse {
  success: boolean;
  message: string;
  premortem_id?: string;
  premortem?: PreMortem;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

// Made with Bob
