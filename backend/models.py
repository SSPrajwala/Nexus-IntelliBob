from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RepoDNA(BaseModel):
    id: Optional[str] = None
    repo_path: str
    patterns: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    architecture_type: Optional[str] = None
    language_distribution: Dict[str, float] = Field(default_factory=dict)
    complexity_score: float = 0.0
    created_at: Optional[datetime] = None


class IncidentDNA(BaseModel):
    id: Optional[str] = None
    incident_id: str
    title: str
    description: str
    severity: SeverityLevel
    status: IncidentStatus = IncidentStatus.OPEN
    root_cause: Optional[str] = None
    failure_patterns: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    resolution: Optional[str] = None
    occurred_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskMatch(BaseModel):
    id: Optional[str] = None
    incident_dna_id: str
    repo_path: str
    file_path: str
    line_number: int
    pattern_matched: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: SeverityLevel
    description: str
    recommendation: Optional[str] = None
    created_at: Optional[datetime] = None


class ScanResult(BaseModel):
    id: Optional[str] = None
    repo_path: str
    scan_type: str
    total_files_scanned: int = 0
    matches_found: int = 0
    risk_matches: List[RiskMatch] = Field(default_factory=list)
    scan_duration_seconds: float = 0.0
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BlastNode(BaseModel):
    id: str
    name: str
    type: str
    risk_level: SeverityLevel
    dependencies: List[str] = Field(default_factory=list)
    impact_score: float = Field(ge=0.0, le=1.0)


class BlastRadius(BaseModel):
    id: Optional[str] = None
    risk_match_id: str
    epicenter_file: str
    epicenter_component: str
    affected_nodes: List[BlastNode] = Field(default_factory=list)
    total_impact_score: float = Field(ge=0.0, le=1.0)
    cascade_depth: int = 0
    estimated_downtime_minutes: Optional[int] = None
    mitigation_priority: SeverityLevel
    created_at: Optional[datetime] = None


class PreMortem(BaseModel):
    id: Optional[str] = None
    blast_radius_id: str
    title: str
    executive_summary: str
    failure_scenario: str
    impact_analysis: str
    affected_systems: List[str] = Field(default_factory=list)
    business_impact: str
    technical_recommendations: List[str] = Field(default_factory=list)
    preventive_actions: List[str] = Field(default_factory=list)
    estimated_cost: Optional[float] = None
    confidence_level: float = Field(ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DashboardStats(BaseModel):
    total_incidents: int = 0
    total_scans: int = 0
    total_risk_matches: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0
    avg_confidence_score: float = 0.0
    last_scan_time: Optional[datetime] = None
    repositories_monitored: int = 0


class IngestRepoRequest(BaseModel):
    repo_path: str
    branch: str = "main"


class IngestRepoResponse(BaseModel):
    success: bool
    message: str
    repo_dna_id: Optional[str] = None
    patterns_found: int = 0


class ExtractDNARequest(BaseModel):
    incident_title: str
    incident_description: str
    severity: SeverityLevel
    root_cause: Optional[str] = None
    affected_components: List[str] = Field(default_factory=list)


class ExtractDNAResponse(BaseModel):
    success: bool
    message: str
    incident_dna_id: Optional[str] = None
    patterns_extracted: int = 0


class ScanRepoRequest(BaseModel):
    repo_path: str
    incident_dna_ids: Optional[List[str]] = None


class ScanRepoResponse(BaseModel):
    success: bool
    message: str
    scan_id: Optional[str] = None
    matches_found: int = 0
    risk_matches: List[RiskMatch] = Field(default_factory=list)


class BlastRadiusRequest(BaseModel):
    risk_match_id: str


class BlastRadiusResponse(BaseModel):
    success: bool
    message: str
    blast_radius_id: Optional[str] = None
    blast_radius: Optional[BlastRadius] = None


class PreMortemRequest(BaseModel):
    blast_radius_id: str


class PreMortemResponse(BaseModel):
    success: bool
    message: str
    premortem_id: Optional[str] = None
    premortem: Optional[PreMortem] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

# Made with Bob
