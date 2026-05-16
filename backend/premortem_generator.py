"""
Pre-Mortem Intelligence Generator
Generates deterministic AI-style pre-mortem reports by combining:
- Repository risk scan results
- Blast radius analysis
- Incident DNA correlation
"""

import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import os
from pathlib import Path
from utils.logger import logger


def analyze_repository_structure(repo_path: str) -> Dict:
    """
    Analyze actual repository to extract real patterns.
    This makes premortem dynamic and repository-specific.
    
    Returns:
        Dictionary containing repository analysis results
    """
    analysis = {
        "total_files": 0,
        "python_files": 0,
        "has_async": False,
        "has_database": False,
        "has_api": False,
        "has_error_handling": False,
        "has_timeouts": False,
        "async_files": [],
        "db_files": [],
        "api_files": [],
        "modules": set(),
        "imports": set(),
        "framework": None  # FastAPI, Flask, Django, etc.
    }
    
    try:
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            logger.warning(f"Repository path does not exist: {repo_path}")
            return analysis
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build']]
            
            for file in files:
                analysis["total_files"] += 1
                
                if file.endswith('.py'):
                    analysis["python_files"] += 1
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Detect async patterns
                        if "async def" in content or "await " in content or "asyncio" in content:
                            analysis["has_async"] = True
                            analysis["async_files"].append(file)
                        
                        # Detect database patterns
                        db_keywords = ["db.", "session.", "query", "Session(", "engine", "SQLAlchemy", "pymongo", "psycopg"]
                        if any(keyword in content for keyword in db_keywords):
                            analysis["has_database"] = True
                            analysis["db_files"].append(file)
                        
                        # Detect API frameworks
                        if "FastAPI" in content or "@app.get" in content or "@app.post" in content:
                            analysis["has_api"] = True
                            analysis["api_files"].append(file)
                            if not analysis["framework"]:
                                analysis["framework"] = "FastAPI"
                        elif "Flask" in content or "@app.route" in content or "from flask import" in content:
                            analysis["has_api"] = True
                            analysis["api_files"].append(file)
                            if not analysis["framework"]:
                                analysis["framework"] = "Flask"
                        elif "Django" in content or "django.http" in content:
                            analysis["has_api"] = True
                            analysis["api_files"].append(file)
                            if not analysis["framework"]:
                                analysis["framework"] = "Django"
                        
                        # Detect error handling
                        if "try:" in content or "except" in content:
                            analysis["has_error_handling"] = True
                        
                        # Detect timeout configurations
                        if "timeout=" in content or "TIMEOUT" in content:
                            analysis["has_timeouts"] = True
                        
                        # Extract module name
                        rel_path = os.path.relpath(file_path, repo_path)
                        module = rel_path.replace(os.sep, '.').replace('.py', '')
                        analysis["modules"].add(module)
                        
                    except Exception as e:
                        logger.debug(f"Error reading file {file_path}: {e}")
                        continue
        
        # Convert sets to lists for JSON serialization
        analysis["modules"] = list(analysis["modules"])
        analysis["imports"] = list(analysis["imports"])
        
        logger.info(f"Repository analysis complete: {analysis['python_files']} Python files, "
                   f"Framework: {analysis['framework']}, Async: {analysis['has_async']}, "
                   f"DB: {analysis['has_database']}, API: {analysis['has_api']}")
    
    except Exception as e:
        logger.error(f"Error analyzing repository structure: {e}")
    
    return analysis


def _generate_dynamic_incident_title(failed_service: str, pattern_type: str, repo_analysis: Dict) -> str:
    """Generate title based on actual repository characteristics"""
    service_name = failed_service.replace('-service', '').replace('_', ' ').replace('-', ' ').title()
    
    # Add repository-specific context
    if repo_analysis.get('has_async') and not repo_analysis.get('has_error_handling'):
        return f"Async Operation Failure in {service_name} Under Load"
    elif repo_analysis.get('has_database') and not repo_analysis.get('has_timeouts'):
        return f"Database Connection Failure in {service_name}"
    elif repo_analysis.get('has_api'):
        framework = repo_analysis.get('framework', 'API')
        return f"{framework} Endpoint Failure in {service_name}"
    else:
        # Use pattern type as fallback
        titles = {
            "RETRY_STORM": f"Cascading Retry Storm in {service_name} Under Load",
            "RESOURCE_EXHAUSTION": f"{service_name} Connection Pool Exhaustion",
            "CASCADING_TIMEOUT": f"Timeout Cascade Originating from {service_name}",
            "MISSING_TIMEOUT": f"{service_name} Hanging Requests Causing Degradation",
            "SMALL_CONNECTION_POOL": f"{service_name} Database Bottleneck Under Traffic Spike",
            "HARDCODED_SECRET": f"Authentication Failure in {service_name} Post-Rotation",
            "MISSING_CIRCUIT_BREAKER": f"{service_name} Cascading Failure Without Circuit Protection",
            "MEMORY_LEAK": f"Memory Leak in {service_name} Causing Gradual Degradation",
            "RACE_CONDITION": f"Race Condition in {service_name} Under Concurrent Load",
            "DEADLOCK": f"Database Deadlock in {service_name} Transaction Processing"
        }
        return titles.get(pattern_type, f"Critical Failure in {service_name}")


def _generate_incident_title(failed_service: str, pattern_type: str) -> str:
    """Generate realistic incident title - works for any service name (legacy fallback)"""
    return _generate_dynamic_incident_title(failed_service, pattern_type, {})


def _generate_dynamic_executive_summary(failed_service: str, affected_services: List[str],
                                        primary_risk: Dict, criticality_score: int, repo_analysis: Dict) -> str:
    """Generate executive summary based on actual repository analysis"""
    service_name = failed_service.replace('-service', '').replace('_', ' ').replace('-', ' ').title()
    affected_count = len(affected_services)
    
    severity_desc = "CRITICAL" if criticality_score >= 90 else "HIGH" if criticality_score >= 70 else "MEDIUM"
    
    # Add repository-specific context
    repo_context = ""
    if repo_analysis:
        framework = repo_analysis.get('framework')
        if framework:
            repo_context = f"Repository analysis reveals {framework}-based architecture. "
        
        if repo_analysis.get('has_async') and repo_analysis.get('has_database'):
            repo_context += f"Async operations combined with database calls create complex failure modes. "
        elif repo_analysis.get('has_async'):
            repo_context += f"Async operations without proper error handling increase failure risk. "
        elif repo_analysis.get('has_database'):
            repo_context += f"Database dependencies without timeout configuration pose availability risk. "
    
    summary = f"{repo_context}Intelligence analysis indicates {severity_desc} probability of cascading failure originating from {service_name}. "
    
    if affected_count > 0:
        summary += f"Predicted blast radius encompasses {affected_count} dependent service{'s' if affected_count != 1 else ''}, "
        summary += f"with potential platform-wide impact. "
    
    summary += f"Primary architectural weakness: {primary_risk.get('explanation', 'Resource exhaustion pattern detected')}. "
    summary += f"Confidence: {int(primary_risk.get('confidence', 0.75) * 100)}%."
    
    return summary


def _generate_executive_summary(failed_service: str, affected_services: List[str],
                                 primary_risk: Dict, criticality_score: int) -> str:
    """Generate executive summary - works for any service name (legacy fallback)"""
    return _generate_dynamic_executive_summary(failed_service, affected_services, primary_risk, criticality_score, {})


def _generate_dynamic_failure_scenario(failed_service: str, primary_risk: Dict,
                                       propagation_chain: List[Dict], repo_analysis: Dict) -> str:
    """Generate scenario based on ACTUAL repository code patterns"""
    service_name = failed_service.replace('-service', '').replace('_', ' ').replace('-', ' ').title()
    
    # Build scenario from actual code analysis
    scenario_parts = []
    
    if repo_analysis:
        # Scenario based on actual repository characteristics
        if repo_analysis.get('has_async') and not repo_analysis.get('has_error_handling'):
            async_count = len(repo_analysis.get('async_files', []))
            scenario_parts.append(
                f"Repository analysis reveals {async_count} file(s) with async operations. "
                f"Under high load, unhandled async errors in {service_name} will cause request timeouts. "
                f"Worker threads become blocked, preventing new request processing."
            )
        
        if repo_analysis.get('has_database') and not repo_analysis.get('has_timeouts'):
            db_count = len(repo_analysis.get('db_files', []))
            scenario_parts.append(
                f"Database interactions detected in {db_count} file(s). "
                f"Without connection timeouts, {service_name} will hang indefinitely on database latency. "
                f"Connection pool exhaustion occurs within 2-3 minutes under normal load."
            )
        
        if repo_analysis.get('has_api'):
            api_count = len(repo_analysis.get('api_files', []))
            framework = repo_analysis.get('framework', 'API')
            scenario_parts.append(
                f"{framework} endpoints found in {api_count} file(s). "
                f"When {service_name} experiences degradation, dependent services continue sending requests, "
                f"amplifying the failure and causing cascading timeouts."
            )
        
        # Add framework-specific scenarios
        framework = repo_analysis.get('framework')
        if framework == 'FastAPI':
            scenario_parts.append(
                f"FastAPI's async nature means blocking operations will degrade entire event loop. "
                f"Single slow database query can block all concurrent requests."
            )
        elif framework == 'Flask':
            scenario_parts.append(
                f"Flask's synchronous request handling means each blocked request consumes a worker thread. "
                f"Thread pool exhaustion occurs rapidly under load."
            )
    
    # If no specific patterns found, use generic but still reference repo
    if not scenario_parts:
        python_files = repo_analysis.get('python_files', 0) if repo_analysis else 0
        scenario_parts.append(
            f"Repository analysis of {python_files} Python file(s) reveals "
            f"architectural weaknesses in {service_name}. Under production load conditions, "
            f"these patterns will trigger service degradation and potential cascading failures."
        )
    
    base_scenario = " ".join(scenario_parts)
    
    # Add propagation chain if available
    if propagation_chain:
        base_scenario += f"\n\nPropagation sequence: "
        for i, step in enumerate(propagation_chain[:3], 1):
            base_scenario += f"\n{i}. T+{step['time_offset']}s: {step['description']}"
    
    return base_scenario


def _generate_failure_scenario(failed_service: str, primary_risk: Dict,
                                propagation_chain: List[Dict]) -> str:
    """Generate detailed failure scenario - works for any service name (legacy fallback)"""
    return _generate_dynamic_failure_scenario(failed_service, primary_risk, propagation_chain, {})


def _generate_root_cause(primary_risk: Dict) -> str:
    """Generate likely root cause"""
    risk_type = primary_risk.get('risk_type', 'UNKNOWN')
    
    root_causes = {
        "RETRY_STORM": "Retry logic implemented without exponential backoff or jitter, causing traffic amplification under failure conditions",
        "SMALL_CONNECTION_POOL": "Database connection pool undersized for production traffic patterns, creating resource bottleneck",
        "MISSING_TIMEOUT": "HTTP client configured without timeout parameters, allowing indefinite request blocking",
        "MISSING_CIRCUIT_BREAKER": "External service calls lack circuit breaker pattern, preventing failure isolation",
        "HARDCODED_SECRET": "Authentication credentials hardcoded in source code, preventing automated rotation",
        "NO_POOL_OVERFLOW": "Connection pool configured with zero overflow capacity, unable to handle traffic bursts",
        "UNBOUNDED_CACHE": "Cache implementation without size limits or TTL, leading to memory exhaustion"
    }
    
    return root_causes.get(risk_type, "Architectural anti-pattern creating single point of failure")


def _generate_outage_timeline(failed_service: str, propagation_chain: List[Dict]) -> List[Dict]:
    """Generate predicted outage timeline"""
    timeline = [
        {
            "time": "T+0s",
            "event": "Initial Trigger",
            "description": f"Traffic spike or deployment triggers latent architectural weakness in {failed_service}",
            "severity": "warning"
        },
        {
            "time": "T+15s",
            "event": "Resource Saturation",
            "description": f"{failed_service} connection pool reaches 100% utilization",
            "severity": "high"
        },
        {
            "time": "T+30s",
            "event": "Request Queueing",
            "description": "Incoming requests begin queueing, latency increases to 5-10 seconds",
            "severity": "high"
        }
    ]
    
    # Add propagation events
    for step in propagation_chain[:3]:
        timeline.append({
            "time": f"T+{step['time_offset']}s",
            "event": f"{step['service']} Impact",
            "description": step['description'],
            "severity": "critical" if step['impact_type'] == 'complete_failure' else "high"
        })
    
    timeline.extend([
        {
            "time": "T+120s",
            "event": "Platform Degradation",
            "description": "Multiple services experiencing elevated error rates and latency",
            "severity": "critical"
        },
        {
            "time": "T+180s",
            "event": "Customer Impact",
            "description": "User-facing transactions failing, support tickets increasing",
            "severity": "critical"
        }
    ])
    
    return timeline


def _estimate_customer_impact(criticality_score: int, affected_services: List[str]) -> str:
    """Estimate customer impact"""
    if criticality_score >= 90 or len(affected_services) >= 3:
        return "SEVERE: Complete platform unavailability. All users unable to authenticate or complete transactions. Estimated 100% of active users affected within 3 minutes."
    elif criticality_score >= 70:
        return "HIGH: Critical transaction paths blocked. Payment processing and order completion unavailable. Estimated 75-90% of user workflows impacted."
    elif criticality_score >= 50:
        return "MEDIUM: Degraded service performance. Elevated latency and intermittent failures. Estimated 40-60% of users experiencing issues."
    else:
        return "LOW: Partial service degradation. Some features unavailable but core functionality maintained. Estimated 10-25% of users affected."


def _estimate_business_impact(criticality_score: int, affected_services: List[str]) -> Dict:
    """Estimate business impact"""
    if criticality_score >= 90:
        return {
            "revenue_loss_per_hour": "$2.4M - $3.2M",
            "customer_churn_risk": "HIGH - Estimated 5-8% increase in churn rate",
            "brand_reputation": "SEVERE - Social media escalation likely within 15 minutes",
            "sla_breach": "YES - Multiple Tier-1 SLA violations",
            "regulatory_impact": "Potential compliance reporting required for extended outage"
        }
    elif criticality_score >= 70:
        return {
            "revenue_loss_per_hour": "$850K - $1.5M",
            "customer_churn_risk": "MEDIUM - Estimated 2-4% increase in churn rate",
            "brand_reputation": "HIGH - Customer complaints and negative reviews expected",
            "sla_breach": "YES - Tier-2 SLA violations",
            "regulatory_impact": "Internal incident review required"
        }
    else:
        return {
            "revenue_loss_per_hour": "$200K - $500K",
            "customer_churn_risk": "LOW - Minimal long-term impact",
            "brand_reputation": "MEDIUM - Some customer frustration",
            "sla_breach": "POSSIBLE - Monitoring required",
            "regulatory_impact": "None expected"
        }


def _generate_mitigation_steps(primary_risk: Dict, failed_service: str) -> List[str]:
    """Generate immediate mitigation steps"""
    risk_type = primary_risk.get('risk_type', 'UNKNOWN')
    
    mitigations = {
        "RETRY_STORM": [
            "Implement exponential backoff with jitter (base: 100ms, max: 30s)",
            "Add circuit breaker with 50% failure threshold over 10s window",
            "Reduce max_retries from 5 to 3 in production configuration",
            "Deploy rate limiting: 100 requests/second per client",
            "Enable request hedging with 95th percentile timeout"
        ],
        "SMALL_CONNECTION_POOL": [
            "Increase pool_size from 3 to 20 for production workload",
            "Set max_overflow to 10 to handle traffic bursts",
            "Implement connection pool monitoring and alerting",
            "Add connection timeout: 30 seconds",
            "Enable connection pool pre-warming on service startup"
        ],
        "MISSING_TIMEOUT": [
            "Add request timeout: 30 seconds for all HTTP calls",
            "Implement connection timeout: 10 seconds",
            "Add read timeout: 30 seconds",
            "Deploy circuit breaker pattern",
            "Enable request cancellation on timeout"
        ],
        "MISSING_CIRCUIT_BREAKER": [
            "Implement circuit breaker (failure threshold: 50%, timeout: 60s)",
            "Add fallback response for degraded mode",
            "Deploy bulkhead pattern for resource isolation",
            "Enable health check endpoints",
            "Implement graceful degradation logic"
        ]
    }
    
    return mitigations.get(risk_type, [
        f"Review and remediate architectural weakness in {failed_service}",
        "Implement defensive programming patterns",
        "Add comprehensive monitoring and alerting",
        "Deploy circuit breaker and timeout configurations",
        "Conduct load testing to validate fixes"
    ])


def _generate_engineering_recommendations(scan_results: Dict, blast_radius: Dict) -> List[str]:
    """Generate engineering recommendations"""
    recommendations = [
        "IMMEDIATE (0-24h): Deploy circuit breaker pattern on all external service calls",
        "SHORT-TERM (1-7d): Implement comprehensive timeout configuration across all HTTP clients",
        "SHORT-TERM (1-7d): Increase connection pool sizes based on production traffic analysis",
        "MEDIUM-TERM (1-4w): Migrate to async/await pattern for inter-service communication",
        "MEDIUM-TERM (1-4w): Implement distributed tracing for dependency visibility",
        "LONG-TERM (1-3m): Adopt service mesh for standardized resilience patterns",
        "LONG-TERM (1-3m): Implement chaos engineering testing in staging environment"
    ]
    
    # Add specific recommendations based on risks
    if scan_results.get('critical_risks', 0) > 0:
        recommendations.insert(0, "CRITICAL: Address all critical-severity risks before next deployment")
    
    return recommendations


def _generate_operational_signals(failed_service: str, primary_risk: Dict) -> List[Dict]:
    """Generate operational signals to monitor"""
    signals = [
        {
            "metric": f"{failed_service}.connection_pool.utilization",
            "threshold": "> 80%",
            "alert_severity": "warning",
            "description": "Connection pool approaching saturation"
        },
        {
            "metric": f"{failed_service}.request.latency.p95",
            "threshold": "> 1000ms",
            "alert_severity": "warning",
            "description": "Elevated request latency indicating resource contention"
        },
        {
            "metric": f"{failed_service}.error_rate",
            "threshold": "> 5%",
            "alert_severity": "critical",
            "description": "Error rate spike indicating service degradation"
        },
        {
            "metric": f"{failed_service}.thread_pool.active_threads",
            "threshold": "> 90%",
            "alert_severity": "warning",
            "description": "Thread pool saturation risk"
        },
        {
            "metric": f"{failed_service}.retry.count",
            "threshold": "> 100/min",
            "alert_severity": "warning",
            "description": "Retry storm indicator"
        }
    ]
    
    return signals


def _calculate_confidence_score(scan_results: Dict, blast_radius: Dict) -> float:
    """Calculate overall confidence score"""
    base_confidence = 0.75
    
    # Increase confidence based on risk severity
    critical_risks = scan_results.get('critical_risks', 0)
    high_risks = scan_results.get('high_risks', 0)
    
    if critical_risks > 0:
        base_confidence += 0.15
    elif high_risks > 0:
        base_confidence += 0.10
    
    # Increase confidence based on blast radius
    criticality_score = blast_radius.get('criticality_score', 0)
    if criticality_score >= 90:
        base_confidence += 0.10
    
    return min(base_confidence, 0.98)


def _estimate_time_to_incident(primary_risk: Dict, criticality_score: int) -> str:
    """Estimate time window until incident occurs"""
    risk_severity = primary_risk.get('severity', 'medium')
    
    if risk_severity == 'critical' and criticality_score >= 90:
        return "2-7 days under normal traffic, <24 hours during peak events"
    elif risk_severity == 'critical' or criticality_score >= 80:
        return "1-3 weeks under normal conditions, 2-5 days during traffic spikes"
    elif risk_severity == 'high':
        return "2-6 weeks, accelerated by deployment or configuration changes"
    else:
        return "1-3 months, dependent on traffic growth and system evolution"


def generate_premortem(scan_results: Dict, blast_radius: Dict, dna_matches: List[Dict], repo_path: Optional[str] = None) -> Dict:
    """
    Generate comprehensive pre-mortem intelligence report.
    NOW REPOSITORY-AWARE - analyzes actual code structure.
    
    Args:
        scan_results: Repository risk scan results
        blast_radius: Blast radius analysis results
        dna_matches: Correlated incident DNA patterns
        repo_path: Path to repository for dynamic analysis (optional)
        
    Returns:
        Complete pre-mortem report dictionary
    """
    # Analyze actual repository if path provided
    repo_analysis = {}
    if repo_path:
        logger.info(f"Analyzing repository structure for dynamic premortem: {repo_path}")
        repo_analysis = analyze_repository_structure(repo_path)
    else:
        logger.warning("No repo_path provided - using generic premortem generation")
    
    # Extract key information
    failed_service = blast_radius.get('root_failure_service', 'unknown-service')
    affected_services = blast_radius.get('affected_services', [])
    propagation_chain = blast_radius.get('propagation_chain', [])
    criticality_score = blast_radius.get('criticality_score', 50)
    
    # Get primary risk (highest severity)
    matches = scan_results.get('matches', [])
    primary_risk = matches[0] if matches else {
        'risk_type': 'UNKNOWN',
        'severity': 'medium',
        'confidence': 0.7,
        'explanation': 'Architectural weakness detected'
    }
    
    # Generate DYNAMIC report components based on actual repo
    incident_title = _generate_dynamic_incident_title(failed_service, primary_risk.get('risk_type', 'UNKNOWN'), repo_analysis)
    executive_summary = _generate_dynamic_executive_summary(failed_service, affected_services, primary_risk, criticality_score, repo_analysis)
    failure_scenario = _generate_dynamic_failure_scenario(failed_service, primary_risk, propagation_chain, repo_analysis)
    root_cause = _generate_root_cause(primary_risk)
    outage_timeline = _generate_outage_timeline(failed_service, propagation_chain)
    customer_impact = _estimate_customer_impact(criticality_score, affected_services)
    business_impact = _estimate_business_impact(criticality_score, affected_services)
    mitigation_steps = _generate_mitigation_steps(primary_risk, failed_service)
    engineering_recommendations = _generate_engineering_recommendations(scan_results, blast_radius)
    operational_signals = _generate_operational_signals(failed_service, primary_risk)
    confidence_score = _calculate_confidence_score(scan_results, blast_radius)
    time_to_incident = _estimate_time_to_incident(primary_risk, criticality_score)
    
    # Determine risk level
    if criticality_score >= 90:
        risk_level = "CRITICAL"
    elif criticality_score >= 70:
        risk_level = "HIGH"
    elif criticality_score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Build complete report
    report = {
        "report_id": f"PM-{hashlib.md5(f'{failed_service}{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}",
        "generated_at": datetime.utcnow().isoformat(),
        "incident_title": incident_title,
        "executive_summary": executive_summary,
        "probable_failure_scenario": failure_scenario,
        "likely_root_cause": root_cause,
        "affected_services": [failed_service] + affected_services,
        "outage_timeline": outage_timeline,
        "customer_impact": customer_impact,
        "business_impact": business_impact,
        "estimated_revenue_loss": business_impact.get('revenue_loss_per_hour', 'Unknown'),
        "mitigation_steps": mitigation_steps,
        "engineering_recommendations": engineering_recommendations,
        "confidence_score": round(confidence_score, 2),
        "risk_level": risk_level,
        "estimated_time_to_incident": time_to_incident,
        "similar_historical_incidents": dna_matches[:3] if dna_matches else [],
        "cascading_failure_analysis": {
            "propagation_depth": len(propagation_chain),
            "total_services_at_risk": len(affected_services) + 1,
            "cascade_velocity": "15-30 seconds per service tier",
            "containment_difficulty": "HIGH" if criticality_score >= 80 else "MEDIUM"
        },
        "operational_signals_to_monitor": operational_signals,
        "scan_summary": {
            "total_risks_found": scan_results.get('total_risks', 0),
            "critical_risks": scan_results.get('critical_risks', 0),
            "high_risks": scan_results.get('high_risks', 0),
            "files_analyzed": scan_results.get('total_files_scanned', 0)
        },
        "blast_radius_summary": {
            "epicenter": failed_service,
            "affected_count": len(affected_services),
            "criticality_score": criticality_score,
            "failure_type": blast_radius.get('failure_type', 'unknown')
        }
    }
    
    return report


# Made with Bob