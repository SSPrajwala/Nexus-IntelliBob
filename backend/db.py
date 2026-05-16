import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "nexus.db")


@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic cleanup."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite3.Row to dictionary."""
    if row is None:
        return {}
    return dict(row)


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Convert list of sqlite3.Row to list of dictionaries."""
    return [row_to_dict(row) for row in rows]


def init_db():
    """Initialize database with all required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Repo DNA table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repo_dna (
                id TEXT PRIMARY KEY,
                repo_path TEXT NOT NULL,
                patterns TEXT,
                dependencies TEXT,
                architecture_type TEXT,
                language_distribution TEXT,
                complexity_score REAL DEFAULT 0.0,
                created_at TEXT
            )
        """)
        
        # Incident DNA table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_dna (
                id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                severity TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                root_cause TEXT,
                failure_patterns TEXT,
                affected_components TEXT,
                resolution TEXT,
                occurred_at TEXT NOT NULL,
                resolved_at TEXT,
                created_at TEXT,
                metadata TEXT
            )
        """)
        
        # Risk matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_matches (
                id TEXT PRIMARY KEY,
                incident_dna_id TEXT NOT NULL,
                repo_path TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                pattern_matched TEXT,
                confidence_score REAL,
                risk_level TEXT,
                description TEXT,
                recommendation TEXT,
                created_at TEXT,
                FOREIGN KEY (incident_dna_id) REFERENCES incident_dna(id)
            )
        """)
        
        # Scan results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                id TEXT PRIMARY KEY,
                repo_path TEXT NOT NULL,
                scan_type TEXT,
                total_files_scanned INTEGER DEFAULT 0,
                matches_found INTEGER DEFAULT 0,
                scan_duration_seconds REAL DEFAULT 0.0,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT DEFAULT 'pending',
                metadata TEXT
            )
        """)
        
        # Blast radius table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blast_radius (
                id TEXT PRIMARY KEY,
                risk_match_id TEXT NOT NULL,
                epicenter_file TEXT NOT NULL,
                epicenter_component TEXT,
                affected_nodes TEXT,
                total_impact_score REAL,
                cascade_depth INTEGER DEFAULT 0,
                estimated_downtime_minutes INTEGER,
                mitigation_priority TEXT,
                created_at TEXT,
                FOREIGN KEY (risk_match_id) REFERENCES risk_matches(id)
            )
        """)
        
        # Pre-mortem table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS premortems (
                id TEXT PRIMARY KEY,
                blast_radius_id TEXT NOT NULL,
                title TEXT NOT NULL,
                executive_summary TEXT,
                failure_scenario TEXT,
                impact_analysis TEXT,
                affected_systems TEXT,
                business_impact TEXT,
                technical_recommendations TEXT,
                preventive_actions TEXT,
                estimated_cost REAL,
                confidence_level REAL,
                created_at TEXT,
                metadata TEXT,
                FOREIGN KEY (blast_radius_id) REFERENCES blast_radius(id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_matches_incident ON risk_matches(incident_dna_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_matches_repo ON risk_matches(repo_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blast_radius_risk ON blast_radius(risk_match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_premortems_blast ON premortems(blast_radius_id)")
        
        conn.commit()


def insert_repo_dna(data: Dict[str, Any]) -> str:
    """Insert repo DNA record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        repo_id = data.get("id", f"repo_{datetime.utcnow().timestamp()}")
        cursor.execute("""
            INSERT INTO repo_dna (id, repo_path, patterns, dependencies, architecture_type, 
                                  language_distribution, complexity_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            repo_id,
            data["repo_path"],
            json.dumps(data.get("patterns", [])),
            json.dumps(data.get("dependencies", [])),
            data.get("architecture_type"),
            json.dumps(data.get("language_distribution", {})),
            data.get("complexity_score", 0.0),
            data.get("created_at", datetime.utcnow().isoformat())
        ))
        return repo_id


def insert_incident_dna(data: Dict[str, Any]) -> str:
    """Insert incident DNA record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        incident_id = data.get("id", f"incident_{datetime.utcnow().timestamp()}")
        cursor.execute("""
            INSERT INTO incident_dna (id, incident_id, title, description, severity, status,
                                      root_cause, failure_patterns, affected_components, resolution,
                                      occurred_at, resolved_at, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            data.get("incident_id", incident_id),
            data["title"],
            data.get("description"),
            data["severity"],
            data.get("status", "open"),
            data.get("root_cause"),
            json.dumps(data.get("failure_patterns", [])),
            json.dumps(data.get("affected_components", [])),
            data.get("resolution"),
            data.get("occurred_at", datetime.utcnow().isoformat()),
            data.get("resolved_at"),
            data.get("created_at", datetime.utcnow().isoformat()),
            json.dumps(data.get("metadata", {}))
        ))
        return incident_id


def insert_risk_match(data: Dict[str, Any]) -> str:
    """Insert risk match record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        match_id = data.get("id", f"match_{datetime.utcnow().timestamp()}")
        cursor.execute("""
            INSERT INTO risk_matches (id, incident_dna_id, repo_path, file_path, line_number,
                                      pattern_matched, confidence_score, risk_level, description,
                                      recommendation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            data["incident_dna_id"],
            data["repo_path"],
            data["file_path"],
            data.get("line_number", 0),
            data.get("pattern_matched"),
            data.get("confidence_score", 0.0),
            data.get("risk_level", "low"),
            data.get("description"),
            data.get("recommendation"),
            data.get("created_at", datetime.utcnow().isoformat())
        ))
        return match_id


def insert_scan_result(data: Dict[str, Any]) -> str:
    """Insert scan result record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        scan_id = data.get("id", f"scan_{datetime.utcnow().timestamp()}")
        cursor.execute("""
            INSERT INTO scan_results (id, repo_path, scan_type, total_files_scanned, matches_found,
                                      scan_duration_seconds, started_at, completed_at, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            data["repo_path"],
            data.get("scan_type", "full"),
            data.get("total_files_scanned", 0),
            data.get("matches_found", 0),
            data.get("scan_duration_seconds", 0.0),
            data.get("started_at", datetime.utcnow().isoformat()),
            data.get("completed_at"),
            data.get("status", "pending"),
            json.dumps(data.get("metadata", {}))
        ))
        return scan_id


def insert_blast_radius(data: Dict[str, Any]) -> str:
    """Insert blast radius record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        blast_id = data.get("id", f"blast_{datetime.utcnow().timestamp()}")
        cursor.execute("""
            INSERT INTO blast_radius (id, risk_match_id, epicenter_file, epicenter_component,
                                      affected_nodes, total_impact_score, cascade_depth,
                                      estimated_downtime_minutes, mitigation_priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            blast_id,
            data["risk_match_id"],
            data["epicenter_file"],
            data.get("epicenter_component"),
            json.dumps(data.get("affected_nodes", [])),
            data.get("total_impact_score", 0.0),
            data.get("cascade_depth", 0),
            data.get("estimated_downtime_minutes"),
            data.get("mitigation_priority", "medium"),
            data.get("created_at", datetime.utcnow().isoformat())
        ))
        return blast_id


def insert_premortem(data: Dict[str, Any]) -> str:
    """Insert pre-mortem record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        premortem_id = data.get("id", f"premortem_{datetime.utcnow().timestamp()}")
        cursor.execute("""
            INSERT INTO premortems (id, blast_radius_id, title, executive_summary, failure_scenario,
                                    impact_analysis, affected_systems, business_impact,
                                    technical_recommendations, preventive_actions, estimated_cost,
                                    confidence_level, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            premortem_id,
            data["blast_radius_id"],
            data["title"],
            data.get("executive_summary"),
            data.get("failure_scenario"),
            data.get("impact_analysis"),
            json.dumps(data.get("affected_systems", [])),
            data.get("business_impact"),
            json.dumps(data.get("technical_recommendations", [])),
            json.dumps(data.get("preventive_actions", [])),
            data.get("estimated_cost"),
            data.get("confidence_level", 0.0),
            data.get("created_at", datetime.utcnow().isoformat()),
            json.dumps(data.get("metadata", {}))
        ))
        return premortem_id


def get_all_incidents() -> List[Dict[str, Any]]:
    """Get all incident DNA records."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incident_dna ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return rows_to_dicts(rows)


def get_incident_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get incident DNA by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incident_dna WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        return row_to_dict(row) if row else None


def get_risk_matches_by_repo(repo_path: str) -> List[Dict[str, Any]]:
    """Get all risk matches for a repository."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM risk_matches WHERE repo_path = ? ORDER BY confidence_score DESC", (repo_path,))
        rows = cursor.fetchall()
        return rows_to_dicts(rows)


def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM incident_dna")
        total_incidents = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM scan_results")
        total_scans = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM risk_matches")
        total_risk_matches = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM risk_matches WHERE risk_level = 'critical'")
        critical_risks = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM risk_matches WHERE risk_level = 'high'")
        high_risks = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM risk_matches WHERE risk_level = 'medium'")
        medium_risks = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM risk_matches WHERE risk_level = 'low'")
        low_risks = cursor.fetchone()["count"]
        
        cursor.execute("SELECT AVG(confidence_score) as avg_score FROM risk_matches")
        avg_result = cursor.fetchone()
        avg_confidence_score = avg_result["avg_score"] if avg_result["avg_score"] else 0.0
        
        cursor.execute("SELECT completed_at FROM scan_results WHERE status = 'completed' ORDER BY completed_at DESC LIMIT 1")
        last_scan = cursor.fetchone()
        last_scan_time = last_scan["completed_at"] if last_scan else None
        
        cursor.execute("SELECT COUNT(DISTINCT repo_path) as count FROM repo_dna")
        repositories_monitored = cursor.fetchone()["count"]
        
        return {
            "total_incidents": total_incidents,
            "total_scans": total_scans,
            "total_risk_matches": total_risk_matches,
            "critical_risks": critical_risks,
            "high_risks": high_risks,
            "medium_risks": medium_risks,
            "low_risks": low_risks,
            "avg_confidence_score": round(avg_confidence_score, 2),
            "last_scan_time": last_scan_time,
            "repositories_monitored": repositories_monitored
        }

# Made with Bob
