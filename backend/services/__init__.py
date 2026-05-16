"""
Backend services for Nexus-IntelliBob.
"""

from .analysis_pipeline import AnalysisPipeline, analyze_github_repository
from .service_detector import ServiceDetector, detect_services, get_service_summary
from .failure_simulator import (
    FailureSimulator,
    simulate_failure,
    get_failure_mode_options,
    FailureMode
)

__all__ = [
    'AnalysisPipeline',
    'analyze_github_repository',
    'ServiceDetector',
    'detect_services',
    'get_service_summary',
    'FailureSimulator',
    'simulate_failure',
    'get_failure_mode_options',
    'FailureMode'
]

# Made with Bob
