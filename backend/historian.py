"""
Engineering Historian Intelligence Timeline Generator
Generates cinematic AI timeline showing system evolution, risk accumulation, and predicted incidents
"""

import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


def _generate_deterministic_seed(repo_path: str, failed_service: str) -> int:
    """Generate deterministic seed for consistent timeline generation"""
    seed_string = f"{repo_path}:{failed_service}"
    return int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)


def _generate_timeline_events(scan_result: Dict, blast_radius: Dict, premortem: Dict, seed: int) -> List[Dict]:
    """
    Generate 8-12 chronological engineering evolution events
    
    Args:
        scan_result: Repository scan results
        blast_radius: Blast radius analysis
        premortem: Pre-mortem report
        seed: Deterministic seed
        
    Returns:
        List of timeline events
    """
    random.seed(seed)
    
    failed_service = blast_radius.get('root_failure_service', 'unknown-service')
    affected_services = blast_radius.get('affected_services', [])
    criticality_score = blast_radius.get('criticality_score', 50)
    total_risks = scan_result.get('total_risks', 0)
    critical_risks = scan_result.get('critical_risks', 0)
    
    # Base timestamp (simulate 6 months of evolution)
    now = datetime.utcnow()
    start_date = now - timedelta(days=180)
    
    events = []
    
    # Event 1: Initial Success Phase
    events.append({
        "timestamp": (start_date + timedelta(days=0)).isoformat(),
        "title": "Initial Architecture Success",
        "description": f"System launched with {len(blast_radius.get('graph', {}).get('nodes', []))} microservices. Clean separation of concerns, low coupling. Team velocity high, deployment frequency 2-3x per week.",
        "severity": "low",
        "affected_services": [failed_service],
        "engineering_decision": "Microservices architecture adopted for scalability",
        "operational_impact": "Positive - Fast feature delivery, minimal incidents",
        "confidence_score": 0.92
    })
    
    # Event 2: Fast Feature Shipping
    events.append({
        "timestamp": (start_date + timedelta(days=30)).isoformat(),
        "title": "Rapid Feature Expansion",
        "description": f"Engineering team prioritizes speed over resilience patterns. {failed_service} gains 15+ new endpoints. Retry logic added without backoff strategy. Connection pools remain at default sizes.",
        "severity": "low",
        "affected_services": [failed_service],
        "engineering_decision": "Move fast, optimize later - technical debt accepted for market velocity",
        "operational_impact": "Neutral - No incidents yet, but architectural shortcuts accumulating",
        "confidence_score": 0.88
    })
    
    # Event 3: Retry Logic Growth
    events.append({
        "timestamp": (start_date + timedelta(days=60)).isoformat(),
        "title": "Retry Logic Proliferation",
        "description": f"Retry patterns implemented across {len(affected_services) + 1} services without coordination. No exponential backoff. No circuit breakers. Each service retries 3-5 times, creating potential for traffic amplification.",
        "severity": "medium",
        "affected_services": [failed_service] + affected_services[:2],
        "engineering_decision": "Copy-paste retry logic from Stack Overflow without understanding failure modes",
        "operational_impact": "Warning - First latency spikes observed during peak traffic",
        "confidence_score": 0.85
    })
    
    # Event 4: Database Bottlenecks Emerge
    events.append({
        "timestamp": (start_date + timedelta(days=90)).isoformat(),
        "title": "Database Connection Pool Saturation",
        "description": f"{failed_service} connection pool (size: 3-5) hits 100% utilization during traffic spikes. Requests queue for 2-5 seconds. Team increases timeout values instead of pool size, masking the problem.",
        "severity": "medium",
        "affected_services": [failed_service],
        "engineering_decision": "Increase timeouts to 60s instead of addressing root cause",
        "operational_impact": "Degraded - P95 latency increases from 200ms to 2000ms during peaks",
        "confidence_score": 0.82
    })
    
    # Event 5: Service Coupling Increases
    events.append({
        "timestamp": (start_date + timedelta(days=120)).isoformat(),
        "title": "Tight Coupling Through Shared Database",
        "description": f"Services begin sharing database tables for 'efficiency'. {failed_service} now has direct dependencies on {len(affected_services)} other services. Synchronous HTTP calls replace async patterns.",
        "severity": "high",
        "affected_services": [failed_service] + affected_services,
        "engineering_decision": "Shared database access approved to avoid 'unnecessary' API calls",
        "operational_impact": "High Risk - Blast radius expanding, single points of failure multiplying",
        "confidence_score": 0.79
    })
    
    # Event 6: Missing Observability
    events.append({
        "timestamp": (start_date + timedelta(days=135)).isoformat(),
        "title": "Observability Gaps Widen",
        "description": f"No distributed tracing implemented. Connection pool metrics not monitored. Retry counts not tracked. Team debugging incidents by reading logs manually. Mean time to detection: 15-20 minutes.",
        "severity": "high",
        "affected_services": [failed_service] + affected_services,
        "engineering_decision": "Observability tools deemed 'too expensive' - postponed to next quarter",
        "operational_impact": "Critical Gap - Incidents detected by customers before engineering team",
        "confidence_score": 0.76
    })
    
    # Event 7: Traffic Amplification Pattern
    events.append({
        "timestamp": (start_date + timedelta(days=150)).isoformat(),
        "title": "Traffic Amplification Detected",
        "description": f"Load testing reveals retry storm potential. Single failed request to {failed_service} generates 15-25 downstream requests. No circuit breakers to prevent cascade. Team aware but prioritizes new features.",
        "severity": "high",
        "affected_services": [failed_service] + affected_services,
        "engineering_decision": "Risk accepted - 'We'll fix it if it becomes a problem'",
        "operational_impact": "Severe Risk - System one traffic spike away from cascading failure",
        "confidence_score": 0.88
    })
    
    # Event 8: Cascading Failure Conditions
    events.append({
        "timestamp": (start_date + timedelta(days=165)).isoformat(),
        "title": "Perfect Storm Conditions Established",
        "description": f"All ingredients for cascading failure now present: undersized connection pools, aggressive retries without backoff, no circuit breakers, tight service coupling, missing observability. {critical_risks} critical architectural risks identified.",
        "severity": "critical",
        "affected_services": [failed_service] + affected_services,
        "engineering_decision": "Technical debt backlog grows to 180+ items - none prioritized",
        "operational_impact": "Critical - System in pre-incident state, waiting for trigger event",
        "confidence_score": 0.91
    })
    
    # Event 9: Near-Miss Incident
    events.append({
        "timestamp": (start_date + timedelta(days=172)).isoformat(),
        "title": "Near-Miss: Weekend Traffic Spike",
        "description": f"Saturday traffic spike causes {failed_service} latency to spike to 8 seconds. Connection pool at 98% utilization. Retry storm begins but traffic drops before full cascade. Team unaware of how close to outage.",
        "severity": "critical",
        "affected_services": [failed_service] + affected_services[:2],
        "engineering_decision": "Incident dismissed as 'temporary anomaly' - no post-mortem conducted",
        "operational_impact": "Near-Miss - Avoided outage by luck, not design",
        "confidence_score": 0.87
    })
    
    # Event 10: Predicted Future Incident
    predicted_days = 7 if criticality_score >= 90 else 14 if criticality_score >= 70 else 30
    events.append({
        "timestamp": (now + timedelta(days=predicted_days)).isoformat(),
        "title": "PREDICTED: Cascading Failure Incident",
        "description": f"AI prediction: {failed_service} will experience cascading failure during next major traffic event. Retry storm will amplify load 10-15x. Connection pools exhaust in 90 seconds. {len(affected_services)} dependent services fail within 3 minutes. Platform-wide outage lasting 45-90 minutes.",
        "severity": "critical",
        "affected_services": [failed_service] + affected_services,
        "engineering_decision": "PREVENTABLE - Requires immediate architectural remediation",
        "operational_impact": f"Estimated Revenue Loss: {premortem.get('estimated_revenue_loss', '$2.4M/hour')} | Customer Impact: {len(affected_services) + 1} services down",
        "confidence_score": premortem.get('confidence_score', 0.85)
    })
    
    # Add optional events based on specific risks
    if critical_risks > 2:
        events.insert(7, {
            "timestamp": (start_date + timedelta(days=145)).isoformat(),
            "title": "Multiple Critical Risks Accumulate",
            "description": f"Code review identifies {critical_risks} critical architectural anti-patterns. Hardcoded secrets, missing timeouts, unbounded caches. Security team raises concerns but changes not prioritized.",
            "severity": "high",
            "affected_services": [failed_service] + affected_services[:1],
            "engineering_decision": "Security fixes scheduled for 'next sprint' - repeatedly postponed",
            "operational_impact": "Compounding Risk - Each new risk multiplies failure probability",
            "confidence_score": 0.84
        })
    
    # Sort by timestamp
    events.sort(key=lambda x: x['timestamp'])
    
    return events


def _generate_executive_summary(scan_result: Dict, blast_radius: Dict, premortem: Dict, timeline: List[Dict]) -> Dict:
    """
    Generate CTO-style executive intelligence summary
    
    Args:
        scan_result: Repository scan results
        blast_radius: Blast radius analysis
        premortem: Pre-mortem report
        timeline: Generated timeline events
        
    Returns:
        Executive summary dictionary
    """
    failed_service = blast_radius.get('root_failure_service', 'unknown-service')
    affected_services = blast_radius.get('affected_services', [])
    criticality_score = blast_radius.get('criticality_score', 50)
    total_risks = scan_result.get('total_risks', 0)
    critical_risks = scan_result.get('critical_risks', 0)
    
    # Calculate reliability maturity score (0-100)
    maturity_score = 100
    maturity_score -= (critical_risks * 15)  # -15 per critical risk
    maturity_score -= (scan_result.get('high_risks', 0) * 8)  # -8 per high risk
    maturity_score -= (len(affected_services) * 5)  # -5 per affected service
    maturity_score = max(maturity_score, 0)
    
    # Determine maturity level
    if maturity_score >= 80:
        maturity_level = "MATURE"
        maturity_color = "green"
    elif maturity_score >= 60:
        maturity_level = "DEVELOPING"
        maturity_color = "yellow"
    elif maturity_score >= 40:
        maturity_level = "EMERGING"
        maturity_color = "orange"
    else:
        maturity_level = "IMMATURE"
        maturity_color = "red"
    
    # Identify most dangerous hidden risk
    hidden_risk = {
        "title": "Retry Storm Amplification",
        "description": f"Retry logic across {len(affected_services) + 1} services lacks exponential backoff. Under failure conditions, single request amplifies to 15-25 downstream calls. This creates positive feedback loop leading to cascading failure.",
        "why_hidden": "Appears benign in normal conditions. Only manifests during partial failures or latency spikes. Not visible in standard monitoring. Requires distributed tracing to detect.",
        "blast_radius": f"{len(affected_services) + 1} services",
        "estimated_impact": premortem.get('estimated_revenue_loss', '$2.4M/hour'),
        "detection_difficulty": "HIGH - Requires correlation of retry metrics across services"
    }
    
    # Generate strategic recommendation
    strategic_recommendation = f"""
IMMEDIATE ACTIONS (0-48 hours):
1. Deploy circuit breakers on all {failed_service} external calls
2. Implement exponential backoff with jitter on retry logic
3. Increase connection pool sizes based on traffic analysis
4. Enable distributed tracing for dependency visibility

STRATEGIC PRIORITIES (1-4 weeks):
1. Establish reliability engineering practice
2. Implement chaos engineering testing program
3. Deploy service mesh for standardized resilience patterns
4. Create architectural review board for design decisions

ORGANIZATIONAL CHANGE:
Current velocity-first culture has created {total_risks} architectural risks. Recommend shifting to "sustainable velocity" model where reliability is non-negotiable requirement, not optional feature.
    """.strip()
    
    # Calculate risk posture
    if criticality_score >= 90:
        risk_posture = "CRITICAL"
        risk_posture_description = "System in pre-incident state. Cascading failure imminent under normal traffic conditions."
    elif criticality_score >= 70:
        risk_posture = "HIGH"
        risk_posture_description = "Multiple critical risks present. Incident likely within 2-4 weeks without intervention."
    elif criticality_score >= 50:
        risk_posture = "ELEVATED"
        risk_posture_description = "Architectural weaknesses accumulating. Proactive remediation recommended."
    else:
        risk_posture = "MODERATE"
        risk_posture_description = "Some risks present but system generally stable. Continue monitoring."
    
    return {
        "reliability_maturity_score": maturity_score,
        "maturity_level": maturity_level,
        "maturity_color": maturity_color,
        "risk_posture": risk_posture,
        "risk_posture_description": risk_posture_description,
        "most_dangerous_hidden_risk": hidden_risk,
        "strategic_recommendation": strategic_recommendation,
        "key_metrics": {
            "total_services_analyzed": len(blast_radius.get('graph', {}).get('nodes', [])),
            "services_at_risk": len(affected_services) + 1,
            "critical_risks_found": critical_risks,
            "estimated_time_to_incident": premortem.get('estimated_time_to_incident', 'Unknown'),
            "blast_radius_score": criticality_score,
            "confidence_level": premortem.get('confidence_score', 0.85)
        },
        "organizational_risks": [
            "Velocity prioritized over reliability in engineering culture",
            "Technical debt backlog not actively managed",
            "Observability gaps prevent early incident detection",
            "No chaos engineering or resilience testing practice",
            "Architectural review process absent or ineffective"
        ],
        "executive_summary": f"Analysis of {failed_service} reveals {critical_risks} critical architectural risks with {int(premortem.get('confidence_score', 0.85) * 100)}% confidence of cascading failure. Current reliability maturity: {maturity_level} ({maturity_score}/100). Estimated blast radius: {len(affected_services) + 1} services. Recommended immediate action to prevent platform-wide outage."
    }


def generate_engineering_timeline(scan_result: Dict, blast_radius: Dict, premortem: Dict) -> Dict:
    """
    Generate complete engineering historian intelligence timeline
    
    Args:
        scan_result: Repository scan results from risk_scanner
        blast_radius: Blast radius analysis from blast_analyzer
        premortem: Pre-mortem report from premortem_generator
        
    Returns:
        Complete timeline with events and executive summary
    """
    # Generate deterministic seed
    repo_path = scan_result.get('repository', 'unknown')
    failed_service = blast_radius.get('root_failure_service', 'unknown-service')
    seed = _generate_deterministic_seed(repo_path, failed_service)
    
    # Generate timeline events
    timeline_events = _generate_timeline_events(scan_result, blast_radius, premortem, seed)
    
    # Generate executive summary
    executive_summary = _generate_executive_summary(scan_result, blast_radius, premortem, timeline_events)
    
    return {
        "timeline": timeline_events,
        "executive_summary": executive_summary,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "repository": repo_path,
            "failed_service": failed_service,
            "total_events": len(timeline_events),
            "analysis_confidence": premortem.get('confidence_score', 0.85)
        }
    }


# Made with Bob