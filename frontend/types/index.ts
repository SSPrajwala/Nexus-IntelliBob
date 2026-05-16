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
  // New fields from risk scanner
  risk_type?: string;
  severity?: SeverityLevel;
  confidence?: number;
  matched_code?: string;
  explanation?: string;
  related_incident_pattern?: string;
  blast_radius_score?: number;
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

export interface OutageTimelineEvent {
  time: string;
  event: string;
  description: string;
  severity: "warning" | "high" | "critical";
}

export interface BusinessImpact {
  revenue_loss_per_hour: string;
  customer_churn_risk: string;
  brand_reputation: string;
  sla_breach: string;
  regulatory_impact: string;
}

export interface OperationalSignal {
  metric: string;
  threshold: string;
  alert_severity: "warning" | "critical";
  description: string;
}

export interface CascadingFailureAnalysis {
  propagation_depth: number;
  total_services_at_risk: number;
  cascade_velocity: string;
  containment_difficulty: string;
}

export interface ScanSummary {
  total_risks_found: number;
  critical_risks: number;
  high_risks: number;
  files_analyzed: number;
}

export interface BlastRadiusSummary {
  epicenter: string;
  affected_count: number;
  criticality_score: number;
  failure_type: string;
}

export interface PreMortemReport {
  report_id: string;
  generated_at: string;
  incident_title: string;
  executive_summary: string;
  probable_failure_scenario: string;
  likely_root_cause: string;
  affected_services: string[];
  outage_timeline: OutageTimelineEvent[];
  customer_impact: string;
  business_impact: BusinessImpact;
  estimated_revenue_loss: string;
  mitigation_steps: string[];
  engineering_recommendations: string[];
  confidence_score: number;
  risk_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  estimated_time_to_incident: string;
  similar_historical_incidents: Array<{
    pattern: string;
    confidence: number;
    description: string;
  }>;
  cascading_failure_analysis: CascadingFailureAnalysis;
  operational_signals_to_monitor: OperationalSignal[];
  scan_summary: ScanSummary;
  blast_radius_summary: BlastRadiusSummary;
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
  // New fields from enhanced scanner
  repository?: string;
  total_files_scanned?: number;
  total_risks?: number;
  critical_risks?: number;
  high_risks?: number;
  medium_risks?: number;
  low_risks?: number;
  matches?: RiskMatch[];
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

// GitHub Repository Intelligence Types
export interface RepositoryMetadata {
  owner: string;
  repo_name: string;
  url: string;
  size_mb: number;
  file_count: number;
  detected_languages: Record<string, number>;
  frameworks: string[];
  estimated_service_count: number;
}

export interface ServiceInfo {
  name: string;
  path: string;
  entry_point: string;
  type: string;
}

export interface TopologyOverview {
  total_services: number;
  service_types: Record<string, number>;
  architecture_pattern: string;
  service_list: string[];
}

export interface ArchitectureSummary {
  summary: string;
  services: ServiceInfo[];
  databases: string[];
  queues: string[];
  external_integrations: string[];
  complexity_score: number;
  topology: TopologyOverview;
}

export interface EngineeringRisk {
  type: string;
  severity: string;
  description: string;
}

export interface OperationalRiskProfile {
  total_risks: number;
  risks: EngineeringRisk[];
  overall_risk_level: string;
}

export interface RiskSummary {
  total_risks: number;
  critical_risks: number;
  high_risks: number;
  medium_risks: number;
  low_risks: number;
  files_scanned: number;
  top_risks: RiskMatch[];
}

export interface BlastRadiusData {
  root_failure_service: string;
  affected_services: string[];
  criticality_score: number;
  estimated_customer_impact: string;
  estimated_revenue_risk: string;
  propagation_chain: Array<{
    service: string;
    time_offset: number;
    impact_type: string;
    description: string;
  }>;
  failure_type: string;
  containment_recommendations: string[];
  graph: {
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
}

export interface IntelligenceOverview {
  success: boolean;
  message: string;
  repository_metadata: RepositoryMetadata;
  architecture_summary: ArchitectureSummary;
  risk_summary: RiskSummary;
  blast_radius: BlastRadiusData;
  premortem_report: PreMortemReport;
  engineering_risk_profile: OperationalRiskProfile;
}

export interface AnalyzeGithubRepoRequest {
  repo_url: string;
  failed_service?: string;
}

export interface AnalysisStage {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  progress?: number;
}

// Engineering Historian Timeline Types
export interface TimelineEvent {
  timestamp: string;
  title: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  affected_services: string[];
  engineering_decision: string;
  operational_impact: string;
  confidence_score: number;
}

export interface HiddenRisk {
  title: string;
  description: string;
  why_hidden: string;
  blast_radius: string;
  estimated_impact: string;
  detection_difficulty: string;
}

export interface ExecutiveSummary {
  reliability_maturity_score: number;
  maturity_level: string;
  maturity_color: string;
  risk_posture: string;
  risk_posture_description: string;
  most_dangerous_hidden_risk: HiddenRisk;
  strategic_recommendation: string;
  key_metrics: {
    total_services_analyzed: number;
    services_at_risk: number;
    critical_risks_found: number;
    estimated_time_to_incident: string;
    blast_radius_score: number;
    confidence_level: number;
  };
  organizational_risks: string[];
  executive_summary: string;
}

export interface EngineeringTimelineData {
  timeline: TimelineEvent[];
  executive_summary: ExecutiveSummary;
  metadata: {
    generated_at: string;
    repository: string;
    failed_service: string;
    total_events: number;
    analysis_confidence: number;
  };
}

// Made with Bob
