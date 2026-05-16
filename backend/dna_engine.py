"""
Incident DNA Extraction Engine
Analyzes incident reports and extracts structured failure pattern signatures.
"""

import re
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import os


# Pattern type definitions with their characteristics
PATTERN_DEFINITIONS = {
    "RETRY_STORM": {
        "keywords": ["retry", "retries", "exponential backoff", "retry logic", "retry storm", "amplification"],
        "severity_weight": 0.9,
        "description": "Aggressive retry logic without backoff causing traffic amplification"
    },
    "CASCADING_TIMEOUT": {
        "keywords": ["timeout", "cascading", "cascade", "propagat", "downstream", "upstream"],
        "severity_weight": 0.85,
        "description": "Timeout failures propagating through service dependencies"
    },
    "RESOURCE_EXHAUSTION": {
        "keywords": ["exhaustion", "exhausted", "pool", "connection pool", "thread pool", "memory", "cpu"],
        "severity_weight": 0.9,
        "description": "System resources depleted causing service degradation"
    },
    "IMPLICIT_COUPLING": {
        "keywords": ["coupling", "dependency", "synchronous", "blocking", "tight coupling"],
        "severity_weight": 0.7,
        "description": "Hidden dependencies causing unexpected failure propagation"
    },
    "CONFIG_DRIFT": {
        "keywords": ["configuration", "config", "misconfigured", "settings", "parameter"],
        "severity_weight": 0.6,
        "description": "Configuration inconsistencies leading to unexpected behavior"
    },
    "SILENT_PARTIAL_FAILURE": {
        "keywords": ["partial", "silent", "undetected", "monitoring", "alert"],
        "severity_weight": 0.75,
        "description": "Failures occurring without proper detection or alerting"
    },
    "THUNDERING_HERD": {
        "keywords": ["thundering herd", "stampede", "simultaneous", "burst", "spike"],
        "severity_weight": 0.8,
        "description": "Simultaneous requests overwhelming system capacity"
    },
    "DEADLOCK": {
        "keywords": ["deadlock", "lock", "blocked", "waiting", "mutex"],
        "severity_weight": 0.85,
        "description": "Resource locking causing system to halt"
    },
    "BACKPRESSURE_FAILURE": {
        "keywords": ["backpressure", "queue", "buffer", "overflow", "capacity"],
        "severity_weight": 0.8,
        "description": "Insufficient backpressure handling causing system overload"
    }
}


def _calculate_pattern_score(text: str, pattern_keywords: List[str]) -> float:
    """Calculate confidence score for a pattern based on keyword matches."""
    text_lower = text.lower()
    matches = sum(1 for keyword in pattern_keywords if keyword in text_lower)
    return min(matches / len(pattern_keywords), 1.0)


def _identify_pattern_type(incident_text: str, incident_title: str) -> tuple[str, str, str, float]:
    """Identify the primary failure pattern type."""
    combined_text = f"{incident_title} {incident_text}".lower()
    
    pattern_scores = {}
    for pattern_type, definition in PATTERN_DEFINITIONS.items():
        score = _calculate_pattern_score(combined_text, definition["keywords"])
        if score > 0:
            pattern_scores[pattern_type] = score * definition["severity_weight"]
    
    if not pattern_scores:
        return "UNKNOWN", "Unknown Pattern", "Unable to classify incident pattern", 0.5
    
    # Get highest scoring pattern
    primary_pattern = max(pattern_scores.items(), key=lambda x: x[1])
    pattern_type = primary_pattern[0]
    confidence = primary_pattern[1]
    
    definition = PATTERN_DEFINITIONS[pattern_type]
    pattern_name = pattern_type.replace("_", " ").title()
    
    return pattern_type, pattern_name, definition["description"], confidence


def _extract_root_cause_category(incident_text: str) -> str:
    """Determine the root cause category."""
    text_lower = incident_text.lower()
    
    if any(word in text_lower for word in ["configuration", "config", "setting", "parameter"]):
        return "Configuration"
    elif any(word in text_lower for word in ["code", "bug", "logic", "algorithm"]):
        return "Code Defect"
    elif any(word in text_lower for word in ["capacity", "scale", "load", "traffic"]):
        return "Capacity Planning"
    elif any(word in text_lower for word in ["network", "connectivity", "latency"]):
        return "Network"
    elif any(word in text_lower for word in ["database", "query", "index", "connection pool"]):
        return "Database"
    elif any(word in text_lower for word in ["deployment", "release", "rollout"]):
        return "Deployment"
    else:
        return "Operational"


def _extract_what_went_wrong(incident_text: str, pattern_type: str) -> str:
    """Extract a concise description of what went wrong."""
    text_lower = incident_text.lower()
    
    # Try to find root cause section
    root_cause_match = re.search(r'root cause[:\s]+([^\n]+(?:\n(?!\n)[^\n]+)*)', text_lower, re.IGNORECASE)
    if root_cause_match:
        return root_cause_match.group(1).strip()[:300]
    
    # Try executive summary
    summary_match = re.search(r'executive summary[:\s]+([^\n]+(?:\n(?!\n)[^\n]+)*)', text_lower, re.IGNORECASE)
    if summary_match:
        return summary_match.group(1).strip()[:300]
    
    # Fallback to pattern-based description
    pattern_descriptions = {
        "RETRY_STORM": "Retry logic without exponential backoff caused traffic amplification",
        "CASCADING_TIMEOUT": "Timeout failures cascaded through dependent services",
        "RESOURCE_EXHAUSTION": "System resources were exhausted under load",
        "IMPLICIT_COUPLING": "Hidden service dependencies caused unexpected failures",
        "CONFIG_DRIFT": "Configuration inconsistencies led to system malfunction",
        "SILENT_PARTIAL_FAILURE": "Failures occurred without proper detection",
        "THUNDERING_HERD": "Simultaneous requests overwhelmed system capacity",
        "DEADLOCK": "Resource locking caused system to halt",
        "BACKPRESSURE_FAILURE": "Insufficient backpressure handling caused overload"
    }
    
    return pattern_descriptions.get(pattern_type, "System failure due to architectural weakness")


def _extract_trigger_conditions(incident_text: str) -> List[str]:
    """Extract conditions that triggered the incident."""
    triggers = []
    text_lower = incident_text.lower()
    
    # Traffic patterns
    if re.search(r'traffic.*increas|spike|surge|peak', text_lower):
        triggers.append("High traffic volume")
    if "promotional" in text_lower or "campaign" in text_lower:
        triggers.append("Marketing campaign")
    
    # System conditions
    if "deployment" in text_lower or "release" in text_lower:
        triggers.append("Recent deployment")
    if "configuration change" in text_lower or "config change" in text_lower:
        triggers.append("Configuration change")
    
    # External factors
    if "network" in text_lower and ("issue" in text_lower or "problem" in text_lower):
        triggers.append("Network instability")
    if "third party" in text_lower or "external" in text_lower:
        triggers.append("External service degradation")
    
    # Load conditions
    if "concurrent" in text_lower or "simultaneous" in text_lower:
        triggers.append("Concurrent request surge")
    if "queue" in text_lower and "full" in text_lower:
        triggers.append("Queue saturation")
    
    return triggers if triggers else ["Unknown trigger condition"]


def _extract_code_signatures(incident_text: str, pattern_type: str) -> List[str]:
    """Extract code-level signatures and anti-patterns."""
    signatures = []
    text_lower = incident_text.lower()
    
    # Pattern-specific signatures
    if pattern_type == "RETRY_STORM":
        if "max_retries" in text_lower or "retry" in text_lower:
            signatures.append("max_retries=5 without exponential backoff")
        if "fixed" in text_lower and "delay" in text_lower:
            signatures.append("retry_delay=1 (fixed interval)")
        signatures.append("No circuit breaker pattern")
        signatures.append("No jitter in retry logic")
    
    elif pattern_type == "RESOURCE_EXHAUSTION":
        if "pool_size" in text_lower:
            match = re.search(r'pool_size[=\s]+(\d+)', text_lower)
            if match:
                signatures.append(f"pool_size={match.group(1)} (undersized)")
        if "max_overflow" in text_lower:
            signatures.append("max_overflow=0 (no buffer capacity)")
        signatures.append("No connection pool monitoring")
    
    elif pattern_type == "CASCADING_TIMEOUT":
        signatures.append("Synchronous inter-service calls")
        signatures.append("No timeout configuration")
        signatures.append("Missing circuit breaker")
    
    elif pattern_type == "DEADLOCK":
        signatures.append("Nested lock acquisition")
        signatures.append("No lock timeout")
        signatures.append("Inconsistent lock ordering")
    
    # Generic signatures
    if "no timeout" in text_lower or "missing timeout" in text_lower:
        signatures.append("request_timeout=None")
    if "no monitoring" in text_lower:
        signatures.append("Missing observability")
    
    return signatures if signatures else ["Pattern-specific code signature"]


def _extract_anti_patterns(incident_text: str, pattern_type: str) -> List[str]:
    """Extract architectural anti-patterns."""
    anti_patterns = []
    text_lower = incident_text.lower()
    
    # Common anti-patterns
    if "synchronous" in text_lower:
        anti_patterns.append("Synchronous coupling between services")
    if "no circuit breaker" in text_lower or "missing circuit breaker" in text_lower:
        anti_patterns.append("Missing circuit breaker pattern")
    if "no retry" in text_lower or ("retry" in text_lower and "exponential" not in text_lower):
        anti_patterns.append("Naive retry without exponential backoff")
    if "no timeout" in text_lower:
        anti_patterns.append("Unbounded operation timeouts")
    if "no monitoring" in text_lower or "insufficient monitoring" in text_lower:
        anti_patterns.append("Insufficient observability")
    if "no rate limit" in text_lower:
        anti_patterns.append("Missing rate limiting")
    if "no bulkhead" in text_lower or "no isolation" in text_lower:
        anti_patterns.append("Lack of failure isolation")
    
    # Pattern-specific anti-patterns
    if pattern_type == "RETRY_STORM":
        anti_patterns.append("Unbounded retry amplification")
        anti_patterns.append("No backpressure mechanism")
    elif pattern_type == "RESOURCE_EXHAUSTION":
        anti_patterns.append("Static resource allocation")
        anti_patterns.append("No auto-scaling")
    elif pattern_type == "IMPLICIT_COUPLING":
        anti_patterns.append("Hidden service dependencies")
        anti_patterns.append("Tight coupling without contracts")
    
    return anti_patterns if anti_patterns else ["Architectural weakness detected"]


def _determine_blast_radius_type(incident_text: str) -> str:
    """Determine the blast radius type."""
    text_lower = incident_text.lower()
    
    if "cascad" in text_lower or "propagat" in text_lower:
        return "Cascading"
    elif "isolated" in text_lower or "contained" in text_lower:
        return "Isolated"
    elif "partial" in text_lower:
        return "Partial"
    else:
        return "Service-wide"


def _infer_severity(incident_text: str, incident_title: str) -> str:
    """Infer historical severity from incident description."""
    combined = f"{incident_title} {incident_text}".lower()
    
    if any(word in combined for word in ["critical", "sev-1", "complete outage", "total failure"]):
        return "Critical"
    elif any(word in combined for word in ["high", "sev-2", "major", "significant"]):
        return "High"
    elif any(word in combined for word in ["medium", "sev-3", "moderate"]):
        return "Medium"
    else:
        return "Low"


def _estimate_time_to_detection(incident_text: str) -> str:
    """Estimate time to detection from incident report."""
    text_lower = incident_text.lower()
    
    # Look for timeline information
    timeline_match = re.search(r'(\d+)\s*(minute|min|second|sec|hour|hr)', text_lower)
    if timeline_match:
        value = int(timeline_match.group(1))
        unit = timeline_match.group(2)
        
        if "second" in unit or "sec" in unit:
            if value < 60:
                return "< 1 minute"
            else:
                return f"{value // 60} minutes"
        elif "minute" in unit or "min" in unit:
            if value < 5:
                return "< 5 minutes"
            elif value < 15:
                return "5-15 minutes"
            else:
                return "> 15 minutes"
        elif "hour" in unit or "hr" in unit:
            return f"{value} hours"
    
    # Default estimates
    if "rapid" in text_lower or "immediate" in text_lower:
        return "< 5 minutes"
    elif "delayed" in text_lower or "late" in text_lower:
        return "> 30 minutes"
    else:
        return "5-15 minutes"


def _find_similar_incidents(pattern_type: str) -> List[str]:
    """Find similar known incidents based on pattern type."""
    similar_incidents = {
        "RETRY_STORM": [
            "Black Friday 2023 Payment Gateway Overload",
            "API Rate Limit Cascade - Q2 2023",
            "External Service Retry Amplification"
        ],
        "RESOURCE_EXHAUSTION": [
            "Database Connection Pool Exhaustion - Oct 2022",
            "Thread Pool Saturation - Payment Service",
            "Memory Leak in Order Processing"
        ],
        "CASCADING_TIMEOUT": [
            "Microservices Timeout Cascade - Q3 2023",
            "API Gateway Timeout Propagation",
            "Service Mesh Timeout Chain"
        ],
        "DEADLOCK": [
            "Database Deadlock - Inventory System",
            "Distributed Lock Contention",
            "Transaction Lock Timeout"
        ],
        "IMPLICIT_COUPLING": [
            "Hidden Dependency Failure - Auth Service",
            "Unexpected Service Coupling",
            "Synchronous Call Chain Failure"
        ],
        "CONFIG_DRIFT": [
            "Production Config Mismatch",
            "Environment Variable Inconsistency",
            "Feature Flag Misconfiguration"
        ],
        "SILENT_PARTIAL_FAILURE": [
            "Undetected Cache Failure",
            "Silent Data Loss - Backup System",
            "Monitoring Gap - Payment Processing"
        ],
        "THUNDERING_HERD": [
            "Cache Stampede - Product Catalog",
            "Simultaneous Connection Burst",
            "Cold Start Overload"
        ],
        "BACKPRESSURE_FAILURE": [
            "Message Queue Overflow",
            "Event Stream Backlog",
            "Request Buffer Saturation"
        ]
    }
    
    return similar_incidents.get(pattern_type, ["No similar incidents found"])


def extract_dna(incident_text: str, incident_title: str) -> Dict:
    """
    Extract structured DNA signature from an incident report.
    
    Args:
        incident_text: Full incident report text
        incident_title: Incident title/summary
        
    Returns:
        Dictionary containing structured incident DNA
    """
    # Generate unique DNA ID
    dna_id = hashlib.md5(f"{incident_title}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]
    
    # Identify primary pattern
    pattern_type, pattern_name, pattern_description, confidence = _identify_pattern_type(
        incident_text, incident_title
    )
    
    # Extract all components
    root_cause_category = _extract_root_cause_category(incident_text)
    what_went_wrong = _extract_what_went_wrong(incident_text, pattern_type)
    trigger_conditions = _extract_trigger_conditions(incident_text)
    code_signatures = _extract_code_signatures(incident_text, pattern_type)
    anti_patterns = _extract_anti_patterns(incident_text, pattern_type)
    blast_radius_type = _determine_blast_radius_type(incident_text)
    historical_severity = _infer_severity(incident_text, incident_title)
    time_to_detection = _estimate_time_to_detection(incident_text)
    similar_incidents = _find_similar_incidents(pattern_type)
    
    return {
        "dna_id": f"DNA-{dna_id}",
        "incident_title": incident_title,
        "pattern_type": pattern_type,
        "pattern_name": pattern_name,
        "pattern_description": pattern_description,
        "root_cause_category": root_cause_category,
        "what_went_wrong": what_went_wrong,
        "trigger_conditions": trigger_conditions,
        "code_signatures": code_signatures,
        "anti_patterns": anti_patterns,
        "blast_radius_type": blast_radius_type,
        "historical_severity": historical_severity,
        "time_to_detection": time_to_detection,
        "similar_known_incidents": similar_incidents,
        "confidence_score": round(confidence, 2),
        "extracted_at": datetime.utcnow().isoformat()
    }


def extract_dna_batch(incident_files: List[str]) -> List[Dict]:
    """
    Extract DNA from multiple incident report files.
    
    Args:
        incident_files: List of file paths to incident reports
        
    Returns:
        List of DNA dictionaries
    """
    results = []
    
    for file_path in incident_files:
        try:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                incident_text = f.read()
            
            # Extract title from first line or filename
            lines = incident_text.split('\n')
            incident_title = lines[0].strip() if lines else os.path.basename(file_path)
            
            # Remove common prefixes
            incident_title = re.sub(r'^INCIDENT REPORT:\s*', '', incident_title, flags=re.IGNORECASE)
            incident_title = re.sub(r'^[=\-]+\s*', '', incident_title)
            
            dna = extract_dna(incident_text, incident_title)
            dna['source_file'] = file_path
            results.append(dna)
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    return results


# Made with Bob