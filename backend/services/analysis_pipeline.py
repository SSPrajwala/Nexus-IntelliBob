"""
Unified Analysis Pipeline
Orchestrates complete repository intelligence analysis with proper lifecycle management.
Keeps cloned repositories alive throughout the entire analysis pipeline.
"""

import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

from core.path_manager import (
    is_github_url,
    resolve_repo_path,
    get_temp_manager,
)
import repo_ingestor
import repo_analyzer
import risk_scanner
import blast_analyzer
import premortem_generator
import historian

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Manages the complete analysis lifecycle for a repository.
    Ensures temp repositories stay alive until all analysis stages complete.
    """
    
    def __init__(self):
        self.temp_manager = get_temp_manager()
        self.cloned_repo_path: Optional[str] = None
        self.resolved_repo_path: Optional[str] = None
        self.ingestor = repo_ingestor.RepoIngestor()
    
    def _resolve_repository(self, repo_input: str) -> Tuple[bool, str, Optional[str]]:
        """
        Resolve repository input to a local path.
        Clones GitHub repos and tracks them for cleanup.
        
        Returns:
            Tuple of (success, local_path, error_message)
        """
        try:
            # Check if GitHub URL
            if is_github_url(repo_input):
                logger.info(f"Cloning GitHub repository: {repo_input}")
                success, local_path, error = self.ingestor.clone_repository(repo_input)
                
                if not success:
                    return False, "", f"Failed to clone repository: {error}"
                
                # Track for cleanup but DON'T cleanup yet
                self.cloned_repo_path = local_path
                self.temp_manager.track(local_path)
                self.resolved_repo_path = local_path
                
                logger.info(f"Repository cloned to: {local_path}")
                return True, local_path, None
            
            else:
                # Resolve local path
                resolved_path = resolve_repo_path(repo_input)
                if resolved_path is None:
                    return False, "", f"Invalid repository path: {repo_input}"
                
                self.resolved_repo_path = str(resolved_path)
                logger.info(f"Using local repository: {self.resolved_repo_path}")
                return True, self.resolved_repo_path, None
                
        except Exception as e:
            logger.error(f"Error resolving repository: {e}")
            return False, "", str(e)
    
    def analyze_github_repository(
        self,
        repo_url: str,
        failed_service: Optional[str] = None
    ) -> Dict:
        """
        Complete GitHub repository intelligence analysis.
        Keeps repository alive throughout entire pipeline.
        
        Args:
            repo_url: GitHub repository URL or local path
            failed_service: Optional service name for blast radius analysis
            
        Returns:
            Complete intelligence report dictionary
        """
        try:
            # Step 1: Resolve/Clone Repository
            success, repo_path, error = self._resolve_repository(repo_url)
            if not success:
                return {
                    "success": False,
                    "message": error or "Failed to resolve repository",
                    "error": error
                }
            
            # Step 2: Extract Repository Metadata
            logger.info("Extracting repository metadata...")
            repo_info = self.ingestor.get_repository_info(repo_path)
            
            # Extract owner and repo name for GitHub URLs
            if is_github_url(repo_url):
                owner, repo_name = self.ingestor.extract_repo_metadata(repo_url)
            else:
                owner = "local"
                repo_name = Path(repo_path).name
            
            repository_metadata = {
                "owner": owner,
                "repo_name": repo_name,
                "url": repo_url,
                "size_mb": repo_info.get("size_mb", 0),
                "file_count": repo_info.get("file_count", 0),
                "detected_languages": repo_info.get("detected_languages", {}),
                "frameworks": repo_info.get("frameworks", []),
                "estimated_service_count": repo_info.get("estimated_service_count", 1)
            }
            
            # Step 3: Analyze Architecture
            logger.info("Analyzing repository architecture...")
            arch_analysis = repo_analyzer.analyze_repository(repo_path)
            
            architecture_summary = {
                "summary": arch_analysis.get("architecture_summary", ""),
                "services": arch_analysis.get("services", []),
                "databases": arch_analysis.get("databases", []),
                "queues": arch_analysis.get("queues", []),
                "external_integrations": arch_analysis.get("external_integrations", []),
                "complexity_score": arch_analysis.get("complexity_score", 0),
                "topology": arch_analysis.get("topology", {})
            }
            
            # Step 4: Scan for Risks
            logger.info("Scanning for architectural risks...")
            scan_results = risk_scanner.scan_repository(repo_path)
            
            risk_summary = {
                "total_risks": scan_results.get("total_risks", 0),
                "critical_risks": scan_results.get("critical_risks", 0),
                "high_risks": scan_results.get("high_risks", 0),
                "medium_risks": scan_results.get("medium_risks", 0),
                "low_risks": scan_results.get("low_risks", 0),
                "files_scanned": scan_results.get("total_files_scanned", 0),
                "top_risks": scan_results.get("matches", [])[:5]  # Top 5 risks
            }
            
            # Step 5: Compute Blast Radius (if service specified)
            blast_radius = None
            if failed_service:
                logger.info(f"Computing blast radius for service: {failed_service}")
                try:
                    blast_radius = blast_analyzer.analyze_blast_radius(repo_path, failed_service)
                except Exception as e:
                    logger.warning(f"Blast radius analysis failed: {e}")
                    # Continue without blast radius
            
            # Step 6: Generate Pre-Mortem (if blast radius available)
            premortem_report = None
            if blast_radius and failed_service:
                logger.info("Generating pre-mortem intelligence report...")
                try:
                    # Get DNA matches from risks
                    dna_matches = []
                    for match in scan_results.get('matches', [])[:3]:
                        if match.get('related_incident_pattern'):
                            dna_matches.append({
                                'pattern': match['related_incident_pattern'],
                                'confidence': match.get('confidence', 0.7),
                                'description': match.get('explanation', '')
                            })
                    
                    premortem_report = premortem_generator.generate_premortem(
                        scan_results,
                        blast_radius,
                        dna_matches
                    )
                except Exception as e:
                    logger.warning(f"Pre-mortem generation failed: {e}")
            
            # Step 7: Engineering Risk Profile
            engineering_risk_profile = arch_analysis.get("risk_profile", {
                "total_risks": 0,
                "risks": [],
                "overall_risk_level": "low"
            })
            
            # Return complete intelligence report
            return {
                "success": True,
                "message": "Repository analysis completed successfully",
                "repository_metadata": repository_metadata,
                "architecture_summary": architecture_summary,
                "risk_summary": risk_summary,
                "blast_radius": blast_radius,
                "premortem_report": premortem_report,
                "engineering_risk_profile": engineering_risk_profile
            }
            
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    def cleanup(self):
        """
        Cleanup cloned repository.
        Call this ONLY after all analysis stages are complete.
        """
        if self.cloned_repo_path:
            logger.info(f"Cleaning up cloned repository: {self.cloned_repo_path}")
            self.temp_manager.cleanup(self.cloned_repo_path, ignore_errors=True)
            self.cloned_repo_path = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.cleanup()
        return False


def analyze_github_repository(
    repo_url: str,
    failed_service: Optional[str] = None
) -> Dict:
    """
    Convenience function for complete GitHub repository analysis.
    Automatically manages repository lifecycle.
    
    Args:
        repo_url: GitHub repository URL or local path
        failed_service: Optional service name for blast radius analysis
        
    Returns:
        Complete intelligence report dictionary
    """
    with AnalysisPipeline() as pipeline:
        return pipeline.analyze_github_repository(repo_url, failed_service)


# Made with Bob