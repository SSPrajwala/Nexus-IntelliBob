"""
Blast Radius Analyzer
Analyzes service dependencies and computes cascading failure impact
"""
import os
import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

# Import centralized path manager
from core.path_manager import resolve_repo_path, get_relative_path

# Import dynamic service detector
from services.service_detector import ServiceDetector

logger = logging.getLogger(__name__)


@dataclass
class ServiceNode:
    """Represents a service in the dependency graph"""
    name: str
    path: str
    dependencies: Set[str]
    dependents: Set[str]
    criticality: str  # 'critical', 'high', 'medium', 'low'
    
    def to_dict(self):
        return {
            "name": self.name,
            "path": self.path,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "criticality": self.criticality
        }


@dataclass
class BlastRadiusResult:
    """Result of blast radius analysis"""
    root_failure_service: str
    affected_services: List[str]
    criticality_score: int
    estimated_customer_impact: str
    estimated_revenue_risk: str
    propagation_chain: List[Dict]
    failure_type: str
    containment_recommendations: List[str]
    graph: Dict
    
    def to_dict(self):
        return {
            "root_failure_service": self.root_failure_service,
            "affected_services": self.affected_services,
            "criticality_score": self.criticality_score,
            "estimated_customer_impact": self.estimated_customer_impact,
            "estimated_revenue_risk": self.estimated_revenue_risk,
            "propagation_chain": self.propagation_chain,
            "failure_type": self.failure_type,
            "containment_recommendations": self.containment_recommendations,
            "graph": self.graph
        }


class BlastAnalyzer:
    """Analyzes service dependencies and computes blast radius"""
    
    def __init__(self):
        self.services: Dict[str, ServiceNode] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
    def analyze_repository(self, repo_path: str) -> Dict[str, ServiceNode]:
        """
        Analyze a repository to build service dependency graph
        Uses dynamic service detection to work with ANY repository structure
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dictionary of service nodes
        """
        logger.info(f"Analyzing repository: {repo_path}")
        
        # Use dynamic service detector
        detector = ServiceDetector(repo_path)
        detected_services = detector.detect_services()
        
        if not detected_services:
            logger.warning(f"No services detected in {repo_path}")
            return {}
        
        # Convert detected services to our format
        services = {}
        for svc in detected_services:
            services[svc['name']] = svc['path']
        
        logger.info(f"Detected {len(services)} services/components")
        
        # Analyze dependencies for each service
        for service_name, service_path in services.items():
            dependencies = self._analyze_service_dependencies(service_path, services)
            
            # Get criticality from detector or determine it
            detected_svc = next((s for s in detected_services if s['name'] == service_name), None)
            if detected_svc and 'criticality_score' in detected_svc:
                # Map score to criticality level
                score = detected_svc['criticality_score']
                if score >= 80:
                    criticality = 'critical'
                elif score >= 60:
                    criticality = 'high'
                elif score >= 40:
                    criticality = 'medium'
                else:
                    criticality = 'low'
            else:
                criticality = self._determine_criticality(service_name, dependencies)
            
            self.services[service_name] = ServiceNode(
                name=service_name,
                path=service_path,
                dependencies=dependencies,
                dependents=set(),
                criticality=criticality
            )
        
        # Build reverse dependencies (dependents)
        for service_name, service_node in self.services.items():
            for dep in service_node.dependencies:
                if dep in self.services:
                    self.services[dep].dependents.add(service_name)
        
        logger.info(f"Built dependency graph with {len(self.services)} nodes")
        return self.services
    
    def _analyze_service_dependencies(self, service_path: str, all_services: Dict[str, str]) -> Set[str]:
        """Analyze dependencies for a single service"""
        dependencies = set()
        
        # Scan Python files for imports and HTTP calls
        for root, _, files in os.walk(service_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    deps = self._extract_dependencies_from_file(file_path, all_services)
                    dependencies.update(deps)
        
        return dependencies
    
    def _extract_dependencies_from_file(self, file_path: str, all_services: Dict[str, str]) -> Set[str]:
        """Extract dependencies from a Python file"""
        dependencies = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Detect HTTP service calls
                for service_name in all_services.keys():
                    # Look for service URL references
                    service_pattern = service_name.replace('-', '[_-]')
                    if re.search(rf'{service_pattern}', content, re.IGNORECASE):
                        dependencies.add(service_name)
                    
                    # Look for requests to service endpoints
                    if re.search(rf'requests\.(get|post|put|delete).*{service_pattern}', content, re.IGNORECASE):
                        dependencies.add(service_name)
                
                # Detect shared database usage (implies dependency)
                if 'db.session' in content or 'db.connection' in content:
                    # Services sharing DB have implicit dependencies
                    pass
        
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
        
        return dependencies
    
    def _determine_criticality(self, service_name: str, dependencies: Set[str]) -> str:
        """Determine service criticality based on name and dependencies"""
        service_lower = service_name.lower()
        
        # Critical services (common patterns)
        critical_keywords = ['auth', 'payment', 'security', 'gateway', 'api', 'core']
        if any(keyword in service_lower for keyword in critical_keywords):
            return 'critical'
        
        # High criticality
        high_keywords = ['order', 'user', 'account', 'transaction', 'billing']
        if any(keyword in service_lower for keyword in high_keywords):
            return 'high'
        
        # Based on dependency count
        if len(dependencies) > 3:
            return 'high'
        elif len(dependencies) > 1:
            return 'medium'
        elif len(dependencies) > 0:
            return 'medium'
        
        return 'low'
    
    def compute_blast_radius(self, failed_service: str) -> BlastRadiusResult:
        """
        Compute blast radius for a failed service
        
        Args:
            failed_service: Name of the service that failed
            
        Returns:
            BlastRadiusResult with impact analysis
        """
        if failed_service not in self.services:
            raise ValueError(f"Service {failed_service} not found")
        
        logger.info(f"Computing blast radius for {failed_service}")
        
        # Compute affected services through cascading failures
        affected_services, propagation_chain = self._compute_cascading_failures(failed_service)
        
        # Determine failure type
        failure_type = self._determine_failure_type(failed_service, affected_services)
        
        # Compute criticality score
        criticality_score = self._compute_criticality_score(failed_service, affected_services)
        
        # Estimate business impact
        customer_impact = self._estimate_customer_impact(failed_service, affected_services)
        revenue_risk = self._estimate_revenue_risk(failed_service, affected_services)
        
        # Generate containment recommendations
        recommendations = self._generate_recommendations(failed_service, affected_services)
        
        # Build graph representation
        graph = self._build_graph_representation(failed_service, affected_services)
        
        return BlastRadiusResult(
            root_failure_service=failed_service,
            affected_services=affected_services,
            criticality_score=criticality_score,
            estimated_customer_impact=customer_impact,
            estimated_revenue_risk=revenue_risk,
            propagation_chain=propagation_chain,
            failure_type=failure_type,
            containment_recommendations=recommendations,
            graph=graph
        )
    
    def _compute_cascading_failures(self, failed_service: str) -> Tuple[List[str], List[Dict]]:
        """Compute cascading failures using BFS"""
        affected = []
        propagation_chain = []
        visited = set()
        queue = [(failed_service, 0)]  # (service, time_offset)
        
        while queue:
            current_service, time_offset = queue.pop(0)
            
            if current_service in visited:
                continue
            
            visited.add(current_service)
            
            if current_service != failed_service:
                affected.append(current_service)
                propagation_chain.append({
                    "service": current_service,
                    "time_offset": time_offset,
                    "impact_type": self._get_impact_type(current_service),
                    "description": self._get_failure_description(current_service, failed_service)
                })
            
            # Add dependents to queue
            if current_service in self.services:
                for dependent in self.services[current_service].dependents:
                    if dependent not in visited:
                        # Add time delay based on service criticality
                        delay = 15 if self.services[dependent].criticality == 'critical' else 30
                        queue.append((dependent, time_offset + delay))
        
        return affected, propagation_chain
    
    def _get_impact_type(self, service: str) -> str:
        """Get impact type for a service"""
        if service not in self.services:
            return "unknown"
        
        criticality = self.services[service].criticality
        if criticality == 'critical':
            return "complete_failure"
        elif criticality == 'high':
            return "degraded_performance"
        else:
            return "partial_degradation"
    
    def _get_failure_description(self, affected_service: str, root_service: str) -> str:
        """Generate failure description - works for any service name"""
        # Clean up service names for display
        affected_clean = affected_service.replace('-service', '').replace('_', ' ').replace('-', ' ').title()
        root_clean = root_service.replace('-service', '').replace('_', ' ').replace('-', ' ').title()
        
        # Generate contextual description based on service type
        service_lower = affected_service.lower()
        
        if 'auth' in service_lower:
            return f"{affected_clean} authentication validation failures due to {root_clean} outage"
        elif 'payment' in service_lower:
            return f"{affected_clean} transaction processing blocked by {root_clean} failure"
        elif 'order' in service_lower:
            return f"{affected_clean} processing degraded due to {root_clean} unavailability"
        elif 'api' in service_lower or 'gateway' in service_lower:
            return f"{affected_clean} requests failing due to {root_clean} dependency failure"
        elif 'database' in service_lower or 'db' in service_lower:
            return f"{affected_clean} data access blocked by {root_clean} outage"
        else:
            return f"{affected_clean} impacted by {root_clean} failure"
    
    def _determine_failure_type(self, failed_service: str, affected_services: List[str]) -> str:
        """Determine the type of failure - works for any service"""
        service_lower = failed_service.lower()
        
        # Determine based on service type
        if 'auth' in service_lower:
            return "authentication_cascade"
        elif 'payment' in service_lower:
            return "payment_outage"
        elif 'api' in service_lower or 'gateway' in service_lower:
            return "api_gateway_failure"
        elif 'database' in service_lower or 'db' in service_lower:
            return "data_layer_failure"
        elif len(affected_services) >= 3:
            return "platform_wide_outage"
        elif len(affected_services) >= 1:
            return "cascading_failure"
        else:
            return "service_degradation"
    
    def _compute_criticality_score(self, failed_service: str, affected_services: List[str]) -> int:
        """Compute criticality score (0-100) - works for any service"""
        service_lower = failed_service.lower()
        
        # Base score from failed service type
        if 'auth' in service_lower or 'security' in service_lower:
            base_score = 95
        elif 'payment' in service_lower or 'billing' in service_lower:
            base_score = 90
        elif 'api' in service_lower or 'gateway' in service_lower:
            base_score = 85
        elif 'database' in service_lower or 'db' in service_lower:
            base_score = 80
        elif 'order' in service_lower or 'transaction' in service_lower:
            base_score = 75
        elif 'user' in service_lower or 'account' in service_lower:
            base_score = 70
        else:
            # Default based on service criticality if available
            if failed_service in self.services:
                criticality = self.services[failed_service].criticality
                if criticality == 'critical':
                    base_score = 85
                elif criticality == 'high':
                    base_score = 70
                elif criticality == 'medium':
                    base_score = 55
                else:
                    base_score = 40
            else:
                base_score = 50
        
        # Add points for affected services (each adds impact)
        affected_score = len(affected_services) * 8
        
        # Cap at 100
        return min(base_score + affected_score, 100)
    
    def _estimate_customer_impact(self, failed_service: str, affected_services: List[str]) -> str:
        """Estimate customer impact - works for any service"""
        total_affected = len(affected_services) + 1
        service_lower = failed_service.lower()
        
        # Critical impact scenarios
        if 'auth' in service_lower or 'security' in service_lower:
            return "Complete platform unavailability - All users unable to access services"
        elif total_affected >= 4:
            return "Severe - Platform-wide outage affecting all major functionalities"
        elif 'payment' in service_lower or 'billing' in service_lower:
            return "Critical - All payment transactions blocked, orders cannot be completed"
        elif 'api' in service_lower or 'gateway' in service_lower:
            return "Critical - API gateway failure blocking all external integrations"
        elif 'database' in service_lower or 'db' in service_lower:
            return "Critical - Data layer failure causing widespread service disruption"
        elif total_affected >= 2:
            return "High - Major service degradation affecting core user workflows"
        else:
            return "Medium - Partial service degradation with workarounds available"
    
    def _estimate_revenue_risk(self, failed_service: str, affected_services: List[str]) -> str:
        """Estimate revenue risk - works for any service"""
        total_affected = len(affected_services) + 1
        service_lower = failed_service.lower()
        
        # High revenue risk scenarios
        if 'auth' in service_lower or 'security' in service_lower:
            return "$2.4M/hour - Complete transaction halt"
        elif total_affected >= 4:
            return "$2.0M/hour - Platform-wide outage"
        elif 'payment' in service_lower or 'billing' in service_lower:
            return "$1.8M/hour - Payment processing blocked"
        elif 'api' in service_lower or 'gateway' in service_lower:
            return "$1.5M/hour - API gateway failure blocking integrations"
        elif 'order' in service_lower or 'transaction' in service_lower:
            return "$1.2M/hour - Order processing disrupted"
        elif total_affected >= 2:
            return "$850K/hour - Degraded transaction capacity"
        else:
            return "$200K/hour - Partial service impact"
    
    def _generate_recommendations(self, failed_service: str, affected_services: List[str]) -> List[str]:
        """Generate containment recommendations - works for any service"""
        recommendations = []
        service_lower = failed_service.lower()
        
        # Service-specific recommendations
        if 'auth' in service_lower or 'security' in service_lower:
            recommendations.extend([
                "Implement circuit breaker on auth service dependencies",
                "Enable cached authentication tokens with extended TTL",
                "Deploy read-only mode for non-critical operations",
                "Activate emergency authentication bypass for critical services"
            ])
        elif 'payment' in service_lower or 'billing' in service_lower:
            recommendations.extend([
                "Queue payment requests for retry when service recovers",
                "Enable alternative payment gateway failover",
                "Implement graceful degradation for order processing",
                "Notify customers of payment processing delays"
            ])
        elif 'api' in service_lower or 'gateway' in service_lower:
            recommendations.extend([
                "Route traffic to backup API gateway instances",
                "Enable API request queuing and retry logic",
                "Activate rate limiting to protect recovering services",
                "Notify integration partners of service degradation"
            ])
        elif 'database' in service_lower or 'db' in service_lower:
            recommendations.extend([
                "Failover to read replicas for read operations",
                "Enable database connection pooling limits",
                "Implement query caching for frequently accessed data",
                "Prepare for potential data consistency issues"
            ])
        else:
            recommendations.extend([
                "Isolate failed service to prevent cascade",
                "Enable circuit breakers on dependent services",
                "Scale up healthy services to handle load",
                "Implement graceful degradation patterns"
            ])
        
        # Add general recommendations based on impact
        if len(affected_services) >= 2:
            recommendations.extend([
                "Activate full incident response team",
                "Prepare customer communication plan",
                "Consider emergency maintenance window"
            ])
        
        recommendations.extend([
            "Monitor dependent service health metrics",
            "Prepare rollback procedures",
            "Document incident timeline for post-mortem"
        ])
        
        return recommendations
    
    def _build_graph_representation(self, failed_service: str, affected_services: List[str]) -> Dict:
        """Build graph representation for visualization"""
        nodes = []
        edges = []
        
        # Add all services as nodes
        for service_name, service_node in self.services.items():
            status = 'failed' if service_name == failed_service else \
                    'affected' if service_name in affected_services else 'healthy'
            
            nodes.append({
                "id": service_name,
                "label": service_name.replace('-service', '').title(),
                "status": status,
                "criticality": service_node.criticality
            })
        
        # Add edges for dependencies
        for service_name, service_node in self.services.items():
            for dep in service_node.dependencies:
                if dep in self.services:
                    edges.append({
                        "source": dep,
                        "target": service_name,
                        "type": "dependency"
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }


def analyze_blast_radius(repo_path: str, failed_service: str) -> Dict:
    """
    Main entry point for blast radius analysis
    
    Args:
        repo_path: Path to repository (will be resolved using centralized path manager)
        failed_service: Name of failed service
        
    Returns:
        Dictionary with blast radius analysis
    """
    # Resolve repository path using centralized manager
    resolved_path = resolve_repo_path(repo_path)
    if resolved_path is None:
        raise ValueError(f"GitHub URLs not supported in analyze_blast_radius. Please clone first.")
    
    analyzer = BlastAnalyzer()
    
    # Analyze repository with resolved path
    analyzer.analyze_repository(str(resolved_path))
    
    # Compute blast radius
    result = analyzer.compute_blast_radius(failed_service)
    
    return result.to_dict()


# Made with Bob