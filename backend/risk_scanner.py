"""
Repository Risk Scanner
Detects architectural risk patterns in Python codebases by analyzing code for anti-patterns
that correlate with known incident DNA patterns.
"""

import os
import re
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
import hashlib

# Project root directory (parent of backend/)
BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class RiskMatch:
    """Represents a detected risk in the codebase"""
    id: str
    file_path: str
    line_number: int
    risk_type: str
    severity: str
    confidence: float
    matched_code: str
    explanation: str
    recommendation: str
    related_incident_pattern: str
    blast_radius_score: int


# Risk pattern definitions with detection logic
RISK_PATTERNS = {
    "MISSING_TIMEOUT": {
        "regex": r'requests\.(get|post|put|delete|patch)\([^)]*\)(?![^)]*timeout)',
        "severity_base": 85,
        "incident_pattern": "CASCADING_TIMEOUT",
        "explanation": "HTTP request without timeout can hang indefinitely, causing cascading failures",
        "recommendation": "Add timeout parameter: requests.{method}(..., timeout=30)",
        "blast_radius": 75
    },
    "RETRY_WITHOUT_BACKOFF": {
        "regex": r'(retry|retries|max_retries)\s*=\s*\d+(?!.*exponential|.*backoff)',
        "severity_base": 90,
        "incident_pattern": "RETRY_STORM",
        "explanation": "Retry logic without exponential backoff can cause traffic amplification",
        "recommendation": "Implement exponential backoff with jitter in retry logic",
        "blast_radius": 85
    },
    "SMALL_CONNECTION_POOL": {
        "regex": r'pool_size\s*=\s*([1-5])\b',
        "severity_base": 80,
        "incident_pattern": "RESOURCE_EXHAUSTION",
        "explanation": "Small database connection pool can cause bottlenecks under load",
        "recommendation": "Increase pool_size to at least 10-20 for production workloads",
        "blast_radius": 70
    },
    "NO_POOL_OVERFLOW": {
        "regex": r'max_overflow\s*=\s*0',
        "severity_base": 75,
        "incident_pattern": "RESOURCE_EXHAUSTION",
        "explanation": "Zero overflow buffer prevents handling traffic spikes",
        "recommendation": "Set max_overflow to 5-10 to handle burst traffic",
        "blast_radius": 65
    },
    "HARDCODED_SECRET": {
        "regex": r'(api_key|password|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
        "severity_base": 95,
        "incident_pattern": "AUTH_FAILURE_CASCADE",
        "explanation": "Hardcoded credentials pose security risk and rotation challenges",
        "recommendation": "Use environment variables or secret management service",
        "blast_radius": 90
    },
    "SHARED_MUTABLE_STATE": {
        "regex": r'(self\._\w+_cache|self\._\w+_state)\s*=\s*(\{\}|\[\]|set\(\))',
        "severity_base": 70,
        "incident_pattern": "CACHE_MEMORY_LEAK",
        "explanation": "Shared mutable cache without size limits can grow unbounded",
        "recommendation": "Use TTL-based cache with max size limit (e.g., functools.lru_cache)",
        "blast_radius": 60
    },
    "MISSING_CIRCUIT_BREAKER": {
        "regex": r'(requests\.(get|post)|session\.(get|post)).*(?!circuit|breaker)',
        "severity_base": 80,
        "incident_pattern": "CASCADING_TIMEOUT",
        "explanation": "External calls without circuit breaker can cause cascading failures",
        "recommendation": "Implement circuit breaker pattern (e.g., using pybreaker library)",
        "blast_radius": 75
    },
    "UNBOUNDED_CACHE": {
        "regex": r'cache\[.*\]\s*=.*(?!.*maxsize|.*ttl|.*expire)',
        "severity_base": 75,
        "incident_pattern": "CACHE_MEMORY_LEAK",
        "explanation": "Cache without size limit or TTL can cause memory exhaustion",
        "recommendation": "Add cache size limit and TTL: @lru_cache(maxsize=1000)",
        "blast_radius": 70
    },
    "SYNCHRONOUS_SERVICE_CALL": {
        "regex": r'(requests\.(get|post)|session\.(get|post)).*(?=.*service|.*api)(?!.*async|.*await)',
        "severity_base": 70,
        "incident_pattern": "IMPLICIT_COUPLING",
        "explanation": "Synchronous inter-service calls create tight coupling and blocking",
        "recommendation": "Use async/await or message queue for service-to-service communication",
        "blast_radius": 65
    },
    "INFINITE_RETRY": {
        "regex": r'while\s+True:.*retry|for.*in.*range\([^)]*\):.*retry',
        "severity_base": 95,
        "incident_pattern": "RETRY_STORM",
        "explanation": "Infinite or unbounded retry loop can cause resource exhaustion",
        "recommendation": "Add max retry limit and exponential backoff",
        "blast_radius": 90
    },
    "MISSING_RATE_LIMIT": {
        "regex": r'@app\.(get|post|put|delete).*(?!.*rate_limit|.*throttle)',
        "severity_base": 65,
        "incident_pattern": "RESOURCE_EXHAUSTION",
        "explanation": "API endpoint without rate limiting vulnerable to abuse",
        "recommendation": "Add rate limiting: @limiter.limit('100/minute')",
        "blast_radius": 55
    },
    "NO_QUERY_TIMEOUT": {
        "regex": r'(query|execute)\(.*\)(?!.*timeout)',
        "severity_base": 70,
        "incident_pattern": "CASCADING_TIMEOUT",
        "explanation": "Database query without timeout can block indefinitely",
        "recommendation": "Set query timeout in connection string or query options",
        "blast_radius": 60
    },
    "MISSING_LOCK_TIMEOUT": {
        "regex": r'(Lock|lock)\(.*\)(?!.*timeout)',
        "severity_base": 75,
        "incident_pattern": "DEADLOCK",
        "explanation": "Lock acquisition without timeout can cause deadlocks",
        "recommendation": "Add timeout to lock acquisition: lock.acquire(timeout=5)",
        "blast_radius": 65
    },
    "NO_PAGINATION": {
        "regex": r'\.all\(\)(?!.*limit|.*offset)',
        "severity_base": 60,
        "incident_pattern": "RESOURCE_EXHAUSTION",
        "explanation": "Query without pagination can return excessive data",
        "recommendation": "Add pagination: .limit(100).offset(page * 100)",
        "blast_radius": 50
    },
    "STALE_CACHE_READ": {
        "regex": r'if.*in.*cache:.*return.*cache\[.*\](?!.*ttl|.*expire|.*timestamp)',
        "severity_base": 55,
        "incident_pattern": "SILENT_PARTIAL_FAILURE",
        "explanation": "Cache read without staleness check can serve outdated data",
        "recommendation": "Add TTL check before returning cached data",
        "blast_radius": 45
    }
}


def _calculate_severity(base_score: int, confidence: float, context_multiplier: float = 1.0) -> str:
    """Calculate severity level based on base score, confidence, and context"""
    final_score = base_score * confidence * context_multiplier
    
    if final_score >= 90:
        return "critical"
    elif final_score >= 70:
        return "high"
    elif final_score >= 40:
        return "medium"
    else:
        return "low"


def _calculate_confidence(match: re.Match, line: str, pattern_key: str) -> float:
    """Calculate confidence score for a pattern match"""
    confidence = 0.7  # Base confidence
    
    # Increase confidence for specific patterns
    if pattern_key == "MISSING_TIMEOUT":
        # Higher confidence if it's in a critical path
        if any(word in line.lower() for word in ["payment", "auth", "order", "critical"]):
            confidence += 0.2
    
    elif pattern_key == "SMALL_CONNECTION_POOL":
        # Extract pool size and adjust confidence
        pool_match = re.search(r'pool_size\s*=\s*(\d+)', line)
        if pool_match:
            pool_size = int(pool_match.group(1))
            if pool_size <= 3:
                confidence += 0.25
            elif pool_size <= 5:
                confidence += 0.15
    
    elif pattern_key == "HARDCODED_SECRET":
        # Higher confidence for obvious secrets
        if any(word in line.lower() for word in ["password", "secret", "api_key", "token"]):
            confidence += 0.2
    
    elif pattern_key == "RETRY_WITHOUT_BACKOFF":
        # Check if there's any backoff logic nearby
        if "sleep" in line.lower() or "delay" in line.lower():
            confidence -= 0.1
    
    return min(confidence, 1.0)


def _generate_risk_id(file_path: str, line_number: int, risk_type: str) -> str:
    """Generate unique ID for a risk match"""
    unique_string = f"{file_path}:{line_number}:{risk_type}"
    return f"RISK-{hashlib.md5(unique_string.encode()).hexdigest()[:12]}"


def _extract_code_context(lines: List[str], line_number: int, context_lines: int = 2) -> str:
    """Extract code snippet with context around the matched line"""
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    
    snippet_lines = []
    for i in range(start, end):
        prefix = ">>> " if i == line_number - 1 else "    "
        snippet_lines.append(f"{prefix}{lines[i].rstrip()}")
    
    return "\n".join(snippet_lines)


def scan_file(file_path: str, repo_root: str) -> List[RiskMatch]:
    """Scan a single Python file for risk patterns"""
    risks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        relative_path = os.path.relpath(file_path, repo_root)
        
        # Scan for each risk pattern
        for pattern_key, pattern_def in RISK_PATTERNS.items():
            regex = pattern_def["regex"]
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments and empty lines
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                match = re.search(regex, line, re.IGNORECASE)
                if match:
                    confidence = _calculate_confidence(match, line, pattern_key)
                    
                    # Context multiplier based on file location
                    context_multiplier = 1.0
                    if "service" in file_path.lower():
                        context_multiplier = 1.2
                    elif "db" in file_path.lower() or "database" in file_path.lower():
                        context_multiplier = 1.15
                    
                    severity = _calculate_severity(
                        pattern_def["severity_base"],
                        confidence,
                        context_multiplier
                    )
                    
                    risk = RiskMatch(
                        id=_generate_risk_id(relative_path, line_num, pattern_key),
                        file_path=relative_path,
                        line_number=line_num,
                        risk_type=pattern_key,
                        severity=severity,
                        confidence=round(confidence, 2),
                        matched_code=_extract_code_context(lines, line_num),
                        explanation=pattern_def["explanation"],
                        recommendation=pattern_def["recommendation"].format(
                            method=match.group(1) if match.lastindex and match.lastindex >= 1 else "method"
                        ),
                        related_incident_pattern=pattern_def["incident_pattern"],
                        blast_radius_score=pattern_def["blast_radius"]
                    )
                    
                    risks.append(risk)
    
    except Exception as e:
        print(f"Error scanning {file_path}: {str(e)}")
    
    return risks


def _resolve_repo_path(repo_path: str) -> Path:
    """
    Resolve repository path to absolute path, supporting both relative and absolute paths.
    
    Args:
        repo_path: Repository path (relative or absolute)
        
    Returns:
        Resolved absolute Path object
        
    Raises:
        ValueError: If path is invalid or doesn't exist
    """
    # Validate input
    if not repo_path or not repo_path.strip():
        raise ValueError("Repository path cannot be empty")
    
    # Convert to Path object
    path = Path(repo_path)
    
    # If it's already absolute and exists, use it
    if path.is_absolute():
        if not path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {repo_path}")
        return path.resolve()
    
    # Try resolving relative to project root (BASE_DIR)
    resolved_path = (BASE_DIR / path).resolve()
    if resolved_path.exists() and resolved_path.is_dir():
        return resolved_path
    
    # Try resolving relative to current working directory
    cwd_path = (Path.cwd() / path).resolve()
    if cwd_path.exists() and cwd_path.is_dir():
        return cwd_path
    
    # Path not found
    raise ValueError(
        f"Repository path not found: {repo_path}\n"
        f"Tried:\n"
        f"  - Absolute: {path}\n"
        f"  - Relative to project: {resolved_path}\n"
        f"  - Relative to CWD: {cwd_path}"
    )


def scan_repository(repo_path: str) -> Dict:
    """
    Scan entire repository for architectural risk patterns
    
    Args:
        repo_path: Path to repository root (relative or absolute)
        
    Returns:
        Dictionary containing scan results with risk matches
        
    Raises:
        ValueError: If repository path is invalid or inaccessible
    """
    try:
        repo_root = _resolve_repo_path(repo_path)
    except ValueError as e:
        raise ValueError(str(e))
    
    # Check if directory is empty
    try:
        if not any(repo_root.iterdir()):
            raise ValueError(f"Repository directory is empty: {repo_path}")
    except PermissionError:
        raise ValueError(f"Permission denied accessing repository: {repo_path}")
    
    all_risks = []
    files_scanned = 0
    
    # Recursively scan all Python files
    for py_file in repo_root.rglob("*.py"):
        # Skip __pycache__ and virtual environments
        if "__pycache__" in str(py_file) or "venv" in str(py_file) or ".venv" in str(py_file):
            continue
        
        files_scanned += 1
        file_risks = scan_file(str(py_file), str(repo_root))
        all_risks.extend(file_risks)
    
    # Count risks by severity
    severity_counts = {
        "critical": sum(1 for r in all_risks if r.severity == "critical"),
        "high": sum(1 for r in all_risks if r.severity == "high"),
        "medium": sum(1 for r in all_risks if r.severity == "medium"),
        "low": sum(1 for r in all_risks if r.severity == "low")
    }
    
    # Convert RiskMatch objects to dictionaries
    risk_dicts = []
    for risk in all_risks:
        risk_dicts.append({
            "id": risk.id,
            "file_path": risk.file_path,
            "line_number": risk.line_number,
            "risk_type": risk.risk_type,
            "severity": risk.severity,
            "confidence": risk.confidence,
            "matched_code": risk.matched_code,
            "explanation": risk.explanation,
            "recommendation": risk.recommendation,
            "related_incident_pattern": risk.related_incident_pattern,
            "blast_radius_score": risk.blast_radius_score
        })
    
    return {
        "repository": repo_path,
        "total_files_scanned": files_scanned,
        "total_risks": len(all_risks),
        "critical_risks": severity_counts["critical"],
        "high_risks": severity_counts["high"],
        "medium_risks": severity_counts["medium"],
        "low_risks": severity_counts["low"],
        "matches": risk_dicts
    }


# Made with Bob