from typing import Any, Dict, List
import hashlib
import json
from datetime import datetime


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID with timestamp."""
    timestamp = datetime.utcnow().timestamp()
    return f"{prefix}_{timestamp}"


def calculate_hash(data: str) -> str:
    """Calculate SHA256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON data with fallback."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def safe_json_dumps(data: Any) -> str:
    """Safely dump data to JSON string."""
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        return "{}"


def calculate_confidence_score(matches: int, total: int) -> float:
    """Calculate confidence score based on matches."""
    if total == 0:
        return 0.0
    return min(matches / total, 1.0)


def normalize_severity(severity: str) -> str:
    """Normalize severity level."""
    severity_map = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low",
        "info": "low"
    }
    return severity_map.get(severity.lower(), "medium")


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return datetime.utcnow()

# Made with Bob
