"""
Backend services for Nexus-IntelliBob.
"""

from .analysis_pipeline import AnalysisPipeline, analyze_github_repository
from .service_detector import ServiceDetector, detect_services, get_service_summary

__all__ = [
    'AnalysisPipeline',
    'analyze_github_repository',
    'ServiceDetector',
    'detect_services',
    'get_service_summary'
]

# Made with Bob
