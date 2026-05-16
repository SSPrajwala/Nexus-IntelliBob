"""
Intelligent Failure Simulation System
Replaces hardcoded "failed_service" with smart failure modes
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

from services.service_detector import ServiceDetector

logger = logging.getLogger(__name__)


class FailureMode(str, Enum):
    """Failure simulation modes"""
    AUTO = "auto"  # Automatically select most critical component
    ALL = "all"    # Simulate system-wide failure
    SPECIFIC = "specific"  # User-specified component


class FailureSimulator:
    """
    Intelligent failure simulation that works with ANY repository.
    No more guessing which service to fail.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.detector = ServiceDetector(repo_path)
        self.services = None
        
    def determine_failure_target(
        self, 
        failure_mode: str = "auto",
        specific_target: Optional[str] = None
    ) -> Dict:
        """
        Intelligently determine what should fail based on mode.
        
        Args:
            failure_mode: "auto", "all", or "specific"
            specific_target: Required if mode is "specific"
            
        Returns:
            Dict with failure target information
        """
        mode = FailureMode(failure_mode)
        
        if mode == FailureMode.AUTO:
            return self._auto_select_failure_target()
        elif mode == FailureMode.ALL:
            return self._system_wide_failure()
        elif mode == FailureMode.SPECIFIC:
            return self._specific_failure(specific_target)
        else:
            raise ValueError(f"Unknown failure mode: {failure_mode}")
    
    def _auto_select_failure_target(self) -> Dict:
        """
        AUTO MODE: Automatically select the most critical failure point.
        This is the recommended mode - no user input required.
        """
        logger.info("AUTO MODE: Analyzing repository to find most critical component")
        
        # Detect all services/components
        if self.services is None:
            self.services = self.detector.detect_services()
        
        if not self.services:
            return {
                "mode": "auto",
                "target_type": "system",
                "target_name": "entire-system",
                "display_name": "Entire System",
                "reason": "No distinct services detected - analyzing as monolithic system",
                "criticality_score": 85,
                "description": "System-wide architectural analysis"
            }
        
        # Get auto-selected service (highest criticality)
        auto_service = self.detector.get_auto_selected_service()
        
        if auto_service:
            return {
                "mode": "auto",
                "target_type": auto_service['type'],
                "target_name": auto_service['name'],
                "display_name": auto_service['name'].replace('-', ' ').replace('_', ' ').title(),
                "reason": auto_service.get('reason', 'Highest criticality score'),
                "criticality_score": auto_service.get('criticality_score', 75),
                "description": f"Critical {auto_service['type']} component",
                "path": auto_service.get('path', '')
            }
        
        # Fallback: select first service
        first_service = self.services[0]
        return {
            "mode": "auto",
            "target_type": first_service['type'],
            "target_name": first_service['name'],
            "display_name": first_service['name'].replace('-', ' ').replace('_', ' ').title(),
            "reason": "Primary component in repository",
            "criticality_score": first_service.get('criticality_score', 70),
            "description": f"Primary {first_service['type']} component",
            "path": first_service.get('path', '')
        }
    
    def _system_wide_failure(self) -> Dict:
        """
        ALL MODE: Simulate complete system failure.
        Analyzes global architecture-level risks.
        """
        logger.info("ALL MODE: Simulating system-wide failure")
        
        # Detect all services to understand scope
        if self.services is None:
            self.services = self.detector.detect_services()
        
        service_count = len(self.services) if self.services else 0
        
        return {
            "mode": "all",
            "target_type": "system",
            "target_name": "entire-system",
            "display_name": "Entire System",
            "reason": "Comprehensive platform-wide failure analysis",
            "criticality_score": 100,
            "description": f"System-wide failure affecting {service_count} component(s)",
            "scope": "platform-wide",
            "affected_components": service_count
        }
    
    def _specific_failure(self, target: Optional[str]) -> Dict:
        """
        SPECIFIC MODE: User-specified component failure.
        Validates target exists in repository.
        """
        if not target:
            raise ValueError("Specific mode requires a target component")
        
        logger.info(f"SPECIFIC MODE: Analyzing failure of {target}")
        
        # Detect services to validate target
        if self.services is None:
            self.services = self.detector.detect_services()
        
        # Find matching service
        matching_service = None
        if self.services:
            for service in self.services:
                if service['name'] == target or service['path'] == target:
                    matching_service = service
                    break
        
        if matching_service:
            return {
                "mode": "specific",
                "target_type": matching_service['type'],
                "target_name": matching_service['name'],
                "display_name": matching_service['name'].replace('-', ' ').replace('_', ' ').title(),
                "reason": "User-specified component",
                "criticality_score": matching_service.get('criticality_score', 70),
                "description": f"Targeted failure of {matching_service['type']}",
                "path": matching_service.get('path', '')
            }
        else:
            # Target not found in detected services - treat as file/module
            return {
                "mode": "specific",
                "target_type": "component",
                "target_name": target,
                "display_name": target.replace('-', ' ').replace('_', ' ').title(),
                "reason": "User-specified component",
                "criticality_score": 60,
                "description": "Targeted component failure",
                "path": target
            }
    
    def get_failure_context(self, failure_target: Dict) -> Dict:
        """
        Generate contextual information for the failure simulation.
        Used to enhance blast radius and pre-mortem analysis.
        """
        mode = failure_target['mode']
        
        if mode == "auto":
            return {
                "simulation_type": "intelligent_auto_selection",
                "confidence": "high",
                "explanation": (
                    f"Automatically identified {failure_target['display_name']} as the most "
                    f"critical failure point based on architectural analysis. "
                    f"Criticality score: {failure_target['criticality_score']}/100."
                )
            }
        elif mode == "all":
            return {
                "simulation_type": "system_wide_failure",
                "confidence": "high",
                "explanation": (
                    "Simulating complete platform failure to analyze worst-case scenarios "
                    "and identify systemic architectural weaknesses."
                )
            }
        else:  # specific
            return {
                "simulation_type": "targeted_component_failure",
                "confidence": "medium",
                "explanation": (
                    f"Analyzing failure impact of user-specified component: "
                    f"{failure_target['display_name']}."
                )
            }
    
    def get_available_targets(self) -> List[Dict]:
        """
        Get list of available targets for SPECIFIC mode.
        Returns detected services/components that can be selected.
        """
        if self.services is None:
            self.services = self.detector.detect_services()
        
        if not self.services:
            return []
        
        # Format for frontend dropdown
        targets = []
        for service in self.services:
            targets.append({
                "value": service['name'],
                "label": service['name'].replace('-', ' ').replace('_', ' ').title(),
                "type": service['type'],
                "criticality": service.get('criticality_score', 50),
                "description": f"{service['type'].title()} component"
            })
        
        # Sort by criticality (highest first)
        targets.sort(key=lambda x: x['criticality'], reverse=True)
        
        return targets


def simulate_failure(
    repo_path: str,
    failure_mode: str = "auto",
    specific_target: Optional[str] = None
) -> Tuple[Dict, Dict]:
    """
    Main entry point for failure simulation.
    
    Args:
        repo_path: Path to repository
        failure_mode: "auto", "all", or "specific"
        specific_target: Required if mode is "specific"
        
    Returns:
        Tuple of (failure_target, failure_context)
    """
    simulator = FailureSimulator(repo_path)
    
    # Determine what should fail
    failure_target = simulator.determine_failure_target(failure_mode, specific_target)
    
    # Get contextual information
    failure_context = simulator.get_failure_context(failure_target)
    
    return failure_target, failure_context


def get_failure_mode_options() -> List[Dict]:
    """
    Get available failure modes for frontend.
    """
    return [
        {
            "value": "auto",
            "label": "🤖 Auto (Recommended)",
            "description": "Automatically select the most critical component",
            "default": True
        },
        {
            "value": "all",
            "label": "🌐 Entire System",
            "description": "Simulate platform-wide failure",
            "default": False
        },
        {
            "value": "specific",
            "label": "🎯 Select Component",
            "description": "Choose a specific component to fail",
            "default": False
        }
    ]


# Made with Bob