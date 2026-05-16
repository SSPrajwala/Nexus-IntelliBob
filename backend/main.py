from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import os
import logging

# Initialize logger
logger = logging.getLogger(__name__)

from models import (
    HealthResponse,
    IngestRepoRequest, IngestRepoResponse,
    ExtractDNARequest, ExtractDNAResponse,
    ScanRepoRequest, ScanRepoResponse,
    BlastRadiusRequest, BlastRadiusResponse,
    PreMortemRequest, PreMortemResponse,
    DashboardStats
)
import db
import dna_engine
import risk_scanner
import blast_analyzer
import repo_ingestor
import repo_analyzer
import premortem_generator
import historian
import system_validator

# Import centralized path manager
from core.path_manager import (
    resolve_repo_path,
    is_github_url,
    generate_temp_repo_path,
    get_temp_manager,
    DEMO_REPOS_DIR
)

# Import analysis pipeline and service detection
from services.analysis_pipeline import analyze_github_repository
from services.service_detector import get_service_summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("🚀 Initializing Nexus-IntelliBob...")
    db.init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down Nexus-IntelliBob...")


app = FastAPI(
    title="Nexus-IntelliBob API",
    description="AI Incident Intelligence for Living Codebases",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@app.get("/api/system-health")
async def system_health_check():
    """
    System health validation endpoint.
    Checks paths, dependencies, Git availability, and system configuration.
    """
    try:
        validation_result = system_validator.validate_system()
        return validation_result
    except Exception as e:
        return {
            "status": "error",
            "checks": [],
            "warnings": [],
            "errors": [f"System validation failed: {str(e)}"],
            "paths": {},
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 1,
                "warnings_count": 0,
                "errors_count": 1
            }
        }


@app.post("/api/analyze-github-repo")
async def analyze_github_repo_endpoint(request: dict):
    """
    Complete GitHub repository intelligence analysis.
    This is the MAIN orchestration endpoint that keeps temp repos alive
    throughout the entire analysis pipeline.
    
    Supports both GitHub URLs and local paths.
    """
    try:
        repo_url = request.get('repo_url', '').strip()
        failed_service = request.get('failed_service', '').strip() or None
        
        # Validate input
        if not repo_url:
            raise HTTPException(
                status_code=400,
                detail="Repository URL cannot be empty"
            )
        
        # Run complete analysis pipeline
        # The pipeline manages temp repo lifecycle internally
        result = analyze_github_repository(repo_url, failed_service)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Analysis failed')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze repository: {str(e)}"
        )


@app.post("/api/detect-services")
async def detect_services_endpoint(request: dict):
    """
    Dynamically detect services/components in a repository.
    Works for ANY repository structure - microservices, monoliths, or hybrid.
    
    Returns list of detected services with auto-selection for analysis.
    """
    temp_manager = get_temp_manager()
    cloned_repo_path = None
    
    try:
        repo_path = request.get('repo_path', '').strip()
        
        # Validate input
        if not repo_path:
            raise HTTPException(
                status_code=400,
                detail="Repository path cannot be empty"
            )
        
        # Handle GitHub URLs
        if is_github_url(repo_path):
            ingestor = repo_ingestor.RepoIngestor()
            success, local_path, error = ingestor.clone_repository(repo_path)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to clone repository: {error}"
                )
            cloned_repo_path = local_path
            temp_manager.track(local_path)
            repo_path = local_path
        else:
            # Resolve local path
            try:
                resolved_path = resolve_repo_path(repo_path)
                if resolved_path is None:
                    raise ValueError("Invalid repository path")
                repo_path = str(resolved_path)
            except ValueError as ve:
                raise HTTPException(
                    status_code=404,
                    detail=str(ve)
                )
        
        # Detect services
        service_summary = get_service_summary(repo_path)
        
        return {
            "success": True,
            "message": f"Detected {service_summary['total_services']} services/components",
            **service_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect services: {str(e)}"
        )
    finally:
        # Cleanup cloned repository if needed
        if cloned_repo_path:
            temp_manager.cleanup(cloned_repo_path, ignore_errors=True)


@app.get("/api/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        stats = db.get_dashboard_stats()
        return DashboardStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


# New request/response models for DNA extraction
class ExtractDNAFromTextRequest(BaseModel):
    incident_text: str
    incident_title: str


class ExtractDNAFromTextResponse(BaseModel):
    success: bool
    message: str
    dna: Optional[dict] = None


@app.get("/api/incidents")
async def get_incidents():
    """
    Get all incidents with optional DNA extraction from demo files.
    Automatically loads and extracts DNA from demo incident reports.
    """
    try:
        import os
        from pathlib import Path
        
        # Check if we have demo incidents to load
        demo_incidents_dir = Path("demo-repos/incidents")
        extracted_dnas = []
        
        if demo_incidents_dir.exists():
            incident_files = list(demo_incidents_dir.glob("*.txt"))
            if incident_files:
                # Extract DNA from demo incidents
                extracted_dnas = dna_engine.extract_dna_batch([str(f) for f in incident_files])
        
        # Get existing incidents from database
        incidents = db.get_all_incidents()
        
        return {
            "success": True,
            "incidents": incidents,
            "extracted_dnas": extracted_dnas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incidents: {str(e)}")


@app.post("/api/extract-dna", response_model=ExtractDNAFromTextResponse)
async def extract_dna_from_text(request: ExtractDNAFromTextRequest):
    """
    Extract DNA signature from incident text.
    Analyzes the incident report and identifies failure patterns.
    """
    try:
        if not request.incident_text or not request.incident_title:
            return ExtractDNAFromTextResponse(
                success=False,
                message="Both incident_text and incident_title are required"
            )
        
        # Extract DNA using the engine
        dna = dna_engine.extract_dna(request.incident_text, request.incident_title)
        
        return ExtractDNAFromTextResponse(
            success=True,
            message="DNA extracted successfully",
            dna=dna
        )
        
    except Exception as e:
        return ExtractDNAFromTextResponse(
            success=False,
            message=f"Failed to extract DNA: {str(e)}"
        )


@app.post("/api/ingest-repo", response_model=IngestRepoResponse)
async def ingest_repo(request: IngestRepoRequest):
    """
    Ingest a repository and extract its DNA.
    This analyzes the repository structure, dependencies, and patterns.
    """
    try:
        import os
        from pathlib import Path
        
        repo_path = request.repo_path
        
        # Validate repository path
        if not os.path.exists(repo_path):
            return IngestRepoResponse(
                success=False,
                message=f"Repository path does not exist: {repo_path}",
                patterns_found=0
            )
        
        # Extract basic patterns (simplified for now)
        patterns = []
        dependencies = []
        language_dist = {}
        
        # Scan for common files
        path_obj = Path(repo_path)
        for ext in ['.py', '.js', '.ts', '.java', '.go']:
            count = len(list(path_obj.rglob(f'*{ext}')))
            if count > 0:
                language_dist[ext[1:]] = count
        
        # Look for dependency files
        if (path_obj / 'package.json').exists():
            dependencies.append('npm')
        if (path_obj / 'requirements.txt').exists():
            dependencies.append('pip')
        if (path_obj / 'go.mod').exists():
            dependencies.append('go')
        
        # Create repo DNA
        repo_dna = {
            "repo_path": repo_path,
            "patterns": patterns,
            "dependencies": dependencies,
            "language_distribution": language_dist,
            "complexity_score": sum(language_dist.values()) / 100.0,
            "architecture_type": "microservices" if len(dependencies) > 1 else "monolith"
        }
        
        repo_id = db.insert_repo_dna(repo_dna)
        
        return IngestRepoResponse(
            success=True,
            message=f"Repository ingested successfully",
            repo_dna_id=repo_id,
            patterns_found=len(patterns)
        )
        
    except Exception as e:
        return IngestRepoResponse(
            success=False,
            message=f"Failed to ingest repository: {str(e)}",
            patterns_found=0
        )


@app.post("/api/extract-dna", response_model=ExtractDNAResponse)
async def extract_dna(request: ExtractDNARequest):
    """
    Extract DNA from an incident description.
    This identifies failure patterns and architectural weaknesses.
    """
    try:
        # Extract patterns from incident description
        patterns = []
        description_lower = request.incident_description.lower()
        
        # Pattern detection (simplified)
        if "null pointer" in description_lower or "nullpointerexception" in description_lower:
            patterns.append("null_pointer_dereference")
        if "memory leak" in description_lower:
            patterns.append("memory_leak")
        if "deadlock" in description_lower:
            patterns.append("deadlock")
        if "race condition" in description_lower:
            patterns.append("race_condition")
        if "timeout" in description_lower:
            patterns.append("timeout")
        if "connection" in description_lower and "pool" in description_lower:
            patterns.append("connection_pool_exhaustion")
        if "out of memory" in description_lower or "oom" in description_lower:
            patterns.append("out_of_memory")
        if "stack overflow" in description_lower:
            patterns.append("stack_overflow")
        
        # Create incident DNA
        incident_dna = {
            "incident_id": f"INC-{datetime.utcnow().timestamp()}",
            "title": request.incident_title,
            "description": request.incident_description,
            "severity": request.severity,
            "root_cause": request.root_cause,
            "failure_patterns": patterns,
            "affected_components": request.affected_components,
            "occurred_at": datetime.utcnow().isoformat()
        }
        
        incident_id = db.insert_incident_dna(incident_dna)
        
        return ExtractDNAResponse(
            success=True,
            message="Incident DNA extracted successfully",
            incident_dna_id=incident_id,
            patterns_extracted=len(patterns)
        )
        
    except Exception as e:
        return ExtractDNAResponse(
            success=False,
            message=f"Failed to extract DNA: {str(e)}",
            patterns_extracted=0
        )


@app.post("/api/scan-repo")
async def scan_repo(request: ScanRepoRequest):
    """
    Scan a repository for architectural risk patterns.
    Uses production-quality pattern detection to identify risks before they become incidents.
    Supports both relative paths (e.g., 'demo-repos/payment-system') and absolute paths.
    """
    try:
        repo_path = request.repo_path
        
        # Validate input
        if not repo_path or not repo_path.strip():
            raise HTTPException(
                status_code=400,
                detail="Repository path cannot be empty"
            )
        
        # Run the risk scanner (it handles path resolution internally)
        try:
            scan_results = risk_scanner.scan_repository(repo_path)
        except ValueError as ve:
            # Path resolution or validation error
            raise HTTPException(
                status_code=404,
                detail=str(ve)
            )
        except PermissionError:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied accessing repository: {repo_path}"
            )
        
        # Store scan results in database
        scan_record = {
            "repo_path": repo_path,
            "scan_type": "architectural_risk_analysis",
            "total_files_scanned": scan_results["total_files_scanned"],
            "matches_found": scan_results["total_risks"],
            "scan_duration_seconds": 0.0,  # Scanner doesn't track duration yet
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        scan_id = db.insert_scan_result(scan_record)
        
        # Store individual risk matches
        for match in scan_results["matches"]:
            risk_match = {
                "incident_dna_id": match["related_incident_pattern"],
                "repo_path": repo_path,
                "file_path": match["file_path"],
                "line_number": match["line_number"],
                "pattern_matched": match["risk_type"],
                "confidence_score": match["confidence"],
                "risk_level": match["severity"],
                "description": match["explanation"],
                "recommendation": match["recommendation"]
            }
            match_id = db.insert_risk_match(risk_match)
            match["db_id"] = match_id
        
        return {
            "success": True,
            "message": f"Scan completed. Found {scan_results['total_risks']} potential risks.",
            "scan_id": scan_id,
            "repository": scan_results["repository"],
            "total_files_scanned": scan_results["total_files_scanned"],
            "total_risks": scan_results["total_risks"],
            "critical_risks": scan_results["critical_risks"],
            "high_risks": scan_results["high_risks"],
            "medium_risks": scan_results["medium_risks"],
            "low_risks": scan_results["low_risks"],
            "matches": scan_results["matches"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scan repository: {str(e)}"
        )


@app.get("/api/failure-modes")
async def get_failure_modes():
    """
    Get available failure simulation modes for the frontend.
    Returns options for the failure mode selector.
    """
    from services.failure_simulator import get_failure_mode_options
    
    try:
        modes = get_failure_mode_options()
        return {
            "success": True,
            "modes": modes
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get failure modes: {str(e)}"
        )


# New request/response models for blast radius
class ComputeBlastRadiusRequest(BaseModel):
    repo_path: str
    failed_service: Optional[str] = None  # Now optional - can use failure modes
    failure_mode: str = "auto"  # "auto", "all", or "specific"


class ComputeBlastRadiusResponse(BaseModel):
    success: bool
    message: str
    root_failure_service: Optional[str] = None
    affected_services: Optional[List[str]] = None
    criticality_score: Optional[int] = None
    estimated_customer_impact: Optional[str] = None
    estimated_revenue_risk: Optional[str] = None
    propagation_chain: Optional[List[dict]] = None
    failure_type: Optional[str] = None
    containment_recommendations: Optional[List[str]] = None
    graph: Optional[dict] = None


@app.post("/api/blast-radius", response_model=ComputeBlastRadiusResponse)
async def compute_blast_radius(request: ComputeBlastRadiusRequest):
    """
    Compute blast radius for a failed service.
    Analyzes service dependencies and simulates cascading failures.
    Supports both local paths and GitHub URLs.
    """
    temp_manager = get_temp_manager()
    cloned_repo_path = None
    
    try:
        repo_path = request.repo_path.strip()
        failed_service = request.failed_service.strip() if request.failed_service else None
        failure_mode = request.failure_mode or "auto"
        
        # Validate inputs
        if not repo_path:
            raise HTTPException(
                status_code=400,
                detail="Repository path cannot be empty"
            )
        
        # Validate failure mode
        if failure_mode not in ["auto", "all", "specific"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid failure_mode. Must be 'auto', 'all', or 'specific'"
            )
        
        # If specific mode, failed_service is required
        if failure_mode == "specific" and not failed_service:
            raise HTTPException(
                status_code=400,
                detail="Failed service name required when using 'specific' failure mode"
            )
        
        # Check if it's a GitHub URL
        if is_github_url(repo_path):
            # Clone the repository to temp location
            ingestor = repo_ingestor.RepoIngestor()
            success, local_path, error = ingestor.clone_repository(repo_path)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to clone repository: {error}"
                )
            cloned_repo_path = local_path
            temp_manager.track(local_path)
            repo_path = local_path
        else:
            # Resolve local path using centralized manager
            try:
                resolved_path = resolve_repo_path(repo_path)
                if resolved_path is None:
                    raise ValueError("Invalid repository path")
                repo_path = str(resolved_path)
            except ValueError as ve:
                raise HTTPException(
                    status_code=404,
                    detail=str(ve)
                )
        
        # Analyze blast radius with intelligent failure mode
        result = blast_analyzer.analyze_blast_radius(
            repo_path,
            failed_service=failed_service,
            failure_mode=failure_mode
        )
        
        # Get display name for message
        target_name = result["root_failure_service"]
        if failure_mode == "all":
            message = "System-wide blast radius computed successfully"
        elif failure_mode == "auto":
            message = f"Blast radius computed successfully (auto-selected: {target_name})"
        else:
            message = f"Blast radius computed successfully for {target_name}"
        
        return ComputeBlastRadiusResponse(
            success=True,
            message=message,
            root_failure_service=result["root_failure_service"],
            affected_services=result["affected_services"],
            criticality_score=result["criticality_score"],
            estimated_customer_impact=result["estimated_customer_impact"],
            estimated_revenue_risk=result["estimated_revenue_risk"],
            propagation_chain=result["propagation_chain"],
            failure_type=result["failure_type"],
            containment_recommendations=result["containment_recommendations"],
            graph=result["graph"]
        )
        
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute blast radius: {str(e)}"
        )
    finally:
        # Cleanup cloned repository if needed
        if cloned_repo_path:
            temp_manager.cleanup(cloned_repo_path, ignore_errors=True)


@app.post("/api/blast-radius-legacy", response_model=BlastRadiusResponse)
async def calculate_blast_radius(request: BlastRadiusRequest):
    """
    Legacy blast radius endpoint (kept for backward compatibility).
    Calculate the blast radius of a risk match.
    This determines what would be affected if this risk becomes an incident.
    """
    try:
        # For now, create a simplified blast radius
        blast_radius = {
            "risk_match_id": request.risk_match_id,
            "epicenter_file": "example.py",
            "epicenter_component": "UserService",
            "affected_nodes": [
                {
                    "id": "node1",
                    "name": "UserService",
                    "type": "service",
                    "risk_level": "high",
                    "dependencies": ["AuthService", "DatabaseLayer"],
                    "impact_score": 0.85
                },
                {
                    "id": "node2",
                    "name": "AuthService",
                    "type": "service",
                    "risk_level": "medium",
                    "dependencies": ["TokenManager"],
                    "impact_score": 0.65
                }
            ],
            "total_impact_score": 0.75,
            "cascade_depth": 2,
            "estimated_downtime_minutes": 45,
            "mitigation_priority": "high"
        }
        
        blast_id = db.insert_blast_radius(blast_radius)
        blast_radius['id'] = blast_id
        
        return BlastRadiusResponse(
            success=True,
            message="Blast radius calculated successfully",
            blast_radius_id=blast_id,
            blast_radius=blast_radius
        )
        
    except Exception as e:
        return BlastRadiusResponse(
            success=False,
            message=f"Failed to calculate blast radius: {str(e)}"
        )


@app.post("/api/premortem")
async def generate_premortem_intelligence(request: dict):
    """
    Generate comprehensive pre-mortem intelligence report with intelligent failure modes.
    Combines repository scan, blast radius, and incident DNA correlation.
    Supports both local paths and GitHub URLs.
    Now supports failure modes: auto, all, specific
    """
    temp_manager = get_temp_manager()
    cloned_repo_path = None
    
    try:
        repo_path = request.get('repo_path', '').strip()
        failure_mode = request.get('failure_mode', 'auto')
        failed_service = request.get('failed_service', '').strip() if request.get('failed_service') else None
        
        # Validate inputs
        if not repo_path:
            raise HTTPException(
                status_code=400,
                detail="Repository path cannot be empty"
            )
        
        # Validate failure mode
        if failure_mode not in ["auto", "all", "specific"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid failure_mode. Must be 'auto', 'all', or 'specific'"
            )
        
        # If specific mode, failed_service is required
        if failure_mode == "specific" and not failed_service:
            raise HTTPException(
                status_code=400,
                detail="Failed service name required when using 'specific' failure mode"
            )
        
        # Handle GitHub URLs
        if is_github_url(repo_path):
            logger.info(f"🔍 CLONING GitHub repository: {repo_path}")
            ingestor = repo_ingestor.RepoIngestor()
            success, local_path, error = ingestor.clone_repository(repo_path)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to clone repository: {error}"
                )
            cloned_repo_path = local_path
            temp_manager.track(local_path)
            repo_path = local_path
            logger.info(f"✅ Repository cloned to: {repo_path}")
            
            # Log repository contents for verification
            import os
            if os.path.exists(repo_path):
                files = os.listdir(repo_path)[:10]  # First 10 files
                logger.info(f"📁 Repository contents (first 10): {files}")
        else:
            # Resolve local path using centralized manager
            try:
                resolved_path = resolve_repo_path(repo_path)
                if resolved_path is None:
                    raise ValueError("Invalid repository path")
                repo_path = str(resolved_path)
            except ValueError as ve:
                raise HTTPException(
                    status_code=404,
                    detail=str(ve)
                )
        
        # Determine failure target using intelligent simulation
        from services.failure_simulator import simulate_failure
        
        if failure_mode in ["auto", "all"]:
            failure_target, failure_context = simulate_failure(
                repo_path,
                failure_mode=failure_mode
            )
            failed_service = failure_target['target_name']
        elif not failed_service:
            # If specific mode but no service provided, fall back to auto
            failure_target, failure_context = simulate_failure(
                repo_path,
                failure_mode="auto"
            )
            failed_service = failure_target['target_name']
        
        # Step 1: Scan repository for risks
        logger.info(f"📊 STEP 1: Scanning repository: {repo_path}")
        scan_results = risk_scanner.scan_repository(repo_path)
        logger.info(f"✅ Scan complete: {scan_results.get('total_risks', 0)} risks found, {scan_results.get('total_files_scanned', 0)} files scanned")
        
        # Step 2: Compute blast radius with failure mode
        logger.info(f"💥 STEP 2: Computing blast radius (mode: {failure_mode}, target: {failed_service})")
        blast_results = blast_analyzer.analyze_blast_radius(
            repo_path,
            failed_service=failed_service,
            failure_mode=failure_mode
        )
        affected_count = len(blast_results.get('affected_services', []))
        logger.info(f"✅ Blast radius computed: {affected_count} services affected, criticality: {blast_results.get('criticality_score', 0)}")
        
        # Step 3: Correlate with incident DNA (get similar patterns)
        dna_matches = []
        if scan_results.get('matches'):
            # Get related incident patterns from the first few high-severity risks
            for match in scan_results['matches'][:3]:
                if match.get('related_incident_pattern'):
                    dna_matches.append({
                        'pattern': match['related_incident_pattern'],
                        'confidence': match.get('confidence', 0.7),
                        'description': match.get('explanation', '')
                    })
        logger.info(f"🧬 STEP 3: DNA correlation: {len(dna_matches)} patterns matched")
        
        # Step 4: Generate pre-mortem report with repository path for dynamic analysis
        logger.info(f"📝 STEP 4: Generating pre-mortem report with repo_path: {repo_path}")
        premortem_report = premortem_generator.generate_premortem(
            scan_results,
            blast_results,
            dna_matches,
            repo_path=repo_path  # PASS REPO PATH FOR DYNAMIC ANALYSIS
        )
        logger.info(f"✅ Pre-mortem generated: {premortem_report.get('incident_title', 'Unknown')}")
        
        return {
            "success": True,
            "message": f"Pre-mortem intelligence report generated successfully (mode: {failure_mode})",
            "report": premortem_report
        }
        
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pre-mortem: {str(e)}"
        )
    finally:
        # Cleanup cloned repository if needed
        if cloned_repo_path:
            temp_manager.cleanup(cloned_repo_path, ignore_errors=True)


@app.post("/api/premortem-legacy", response_model=PreMortemResponse)
async def generate_premortem_legacy(request: PreMortemRequest):
    """
    Legacy pre-mortem endpoint (kept for backward compatibility).
    Generate a pre-mortem report for a blast radius.
    """
    try:
        premortem = {
            "blast_radius_id": request.blast_radius_id,
            "title": "Pre-Mortem: Potential Service Cascade Failure",
            "executive_summary": "Analysis indicates a high-risk pattern that could lead to service degradation affecting multiple components.",
            "failure_scenario": "If the identified pattern triggers, it could cause a cascade failure starting from UserService and propagating to dependent services.",
            "impact_analysis": "Estimated impact includes service downtime, data inconsistency, and potential data loss in edge cases.",
            "affected_systems": ["UserService", "AuthService", "DatabaseLayer", "API Gateway"],
            "business_impact": "Potential revenue loss of $50K-$100K per hour of downtime. Customer trust impact rated as HIGH.",
            "technical_recommendations": [
                "Implement circuit breaker pattern",
                "Add comprehensive error handling",
                "Increase monitoring and alerting",
                "Add fallback mechanisms"
            ],
            "preventive_actions": [
                "Code review of identified patterns",
                "Add unit tests for edge cases",
                "Implement chaos engineering tests",
                "Update runbooks"
            ],
            "estimated_cost": 75000.0,
            "confidence_level": 0.82
        }
        
        premortem_id = db.insert_premortem(premortem)
        premortem['id'] = premortem_id
        
        return PreMortemResponse(
            success=True,
            message="Pre-mortem report generated successfully",
            premortem_id=premortem_id,
            premortem=premortem
        )
        
    except Exception as e:
        return PreMortemResponse(
            success=False,
            message=f"Failed to generate pre-mortem: {str(e)}"
        )


@app.post("/api/engineering-timeline")
async def generate_engineering_timeline_endpoint(request: dict):
    """
    Generate Engineering Historian Intelligence Timeline.
    Combines repository scan, blast radius, and pre-mortem to create
    a cinematic AI timeline showing system evolution and predicted incidents.
    Supports both local paths and GitHub URLs.
    """
    temp_manager = get_temp_manager()
    cloned_repo_path = None
    
    try:
        repo_path = request.get('repo_path', '').strip()
        failed_service = request.get('failed_service', '').strip()
        
        # Validate inputs
        if not repo_path:
            raise HTTPException(
                status_code=400,
                detail="Repository path cannot be empty"
            )
        
        if not failed_service:
            raise HTTPException(
                status_code=400,
                detail="Failed service name cannot be empty"
            )
        
        # Handle GitHub URLs
        if is_github_url(repo_path):
            ingestor = repo_ingestor.RepoIngestor()
            success, local_path, error = ingestor.clone_repository(repo_path)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to clone repository: {error}"
                )
            cloned_repo_path = local_path
            temp_manager.track(local_path)
            repo_path = local_path
        else:
            # Resolve local path using centralized manager
            try:
                resolved_path = resolve_repo_path(repo_path)
                if resolved_path is None:
                    raise ValueError("Invalid repository path")
                repo_path = str(resolved_path)
            except ValueError as ve:
                raise HTTPException(
                    status_code=404,
                    detail=str(ve)
                )
        
        # Step 1: Scan repository for risks
        scan_results = risk_scanner.scan_repository(repo_path)
        
        # Step 2: Compute blast radius
        blast_results = blast_analyzer.analyze_blast_radius(repo_path, failed_service)
        
        # Step 3: Correlate with incident DNA
        dna_matches = []
        if scan_results.get('matches'):
            for match in scan_results['matches'][:3]:
                if match.get('related_incident_pattern'):
                    dna_matches.append({
                        'pattern': match['related_incident_pattern'],
                        'confidence': match.get('confidence', 0.7),
                        'description': match.get('explanation', '')
                    })
        
        # Step 4: Generate pre-mortem report
        premortem_report = premortem_generator.generate_premortem(
            scan_results,
            blast_results,
            dna_matches
        )
        
        # Step 5: Generate engineering timeline
        timeline_data = historian.generate_engineering_timeline(
            scan_results,
            blast_results,
            premortem_report
        )
        
        return {
            "success": True,
            "message": "Engineering timeline generated successfully",
            "timeline": timeline_data['timeline'],
            "executive_summary": timeline_data['executive_summary'],
            "metadata": timeline_data['metadata']
        }
        
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate engineering timeline: {str(e)}"
        )
    finally:
        # Cleanup cloned repository if needed
        if cloned_repo_path:
            temp_manager.cleanup(cloned_repo_path, ignore_errors=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
