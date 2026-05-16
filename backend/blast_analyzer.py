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
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dictionary of service nodes
        """
        logger.info(f"Analyzing repository: {repo_path}")
        
        # Discover services
        services = self._discover_services(repo_path)
        
        # Analyze dependencies for each service
        for service_name, service_path in services.items():
            dependencies = self._analyze_service_dependencies(service_path, services)
            
            # Determine criticality based on service type
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
        
        logger.info(f"Discovered {len(self.services)} services")
        return self.services
    
    def _discover_services(self, repo_path: str) -> Dict[str, str]:
        """Discover services in repository"""
        services = {}
        
        # Look for service directories
        if os.path.exists(repo_path):
            for item in os.listdir(repo_path):
                item_path = os.path.join(repo_path, item)
                if os.path.isdir(item_path) and item.endswith('-service'):
                    services[item] = item_path
        
        return services
    
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
        
        # Critical services
        if 'auth' in service_lower:
            return 'critical'
        if 'payment' in service_lower:
            return 'critical'
        
        # High criticality
        if 'order' in service_lower:
            return 'high'
        if len(dependencies) > 2:
            return 'high'
        
        # Medium criticality
        if len(dependencies) > 0:
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
        """Generate failure description"""
        service_type = affected_service.replace('-service', '').title()
        root_type = root_service.replace('-service', '').title()
        
        descriptions = {
            'auth-service': f"{service_type} authentication validation failures due to {root_type} outage",
            'payment-service': f"{service_type} transaction processing blocked by {root_type} failure",
            'order-service': f"{service_type} processing degraded due to {root_type} unavailability"
        }
        
        return descriptions.get(affected_service, f"{service_type} impacted by {root_type} failure")
    
    def _determine_failure_type(self, failed_service: str, affected_services: List[str]) -> str:
        """Determine the type of failure"""
        if failed_service == 'auth-service':
            return "authentication_cascade"
        elif failed_service == 'payment-service':
            return "payment_outage"
        elif len(affected_services) >= 2:
            return "platform_wide_outage"
        else:
            return "service_degradation"
    
    def _compute_criticality_score(self, failed_service: str, affected_services: List[str]) -> int:
        """Compute criticality score (0-100)"""
        base_score = 0
        
        # Base score from failed service
        if failed_service == 'auth-service':
            base_score = 95
        elif failed_service == 'payment-service':
            base_score = 90
        elif failed_service == 'order-service':
            base_score = 75
        else:
            base_score = 50
        
        # Add points for affected services
        affected_score = len(affected_services) * 10
        
        # Cap at 100
        return min(base_score + affected_score, 100)
    
    def _estimate_customer_impact(self, failed_service: str, affected_services: List[str]) -> str:
        """Estimate customer impact"""
        total_affected = len(affected_services) + 1
        
        if failed_service == 'auth-service' or total_affected >= 3:
            return "Complete platform unavailability - All users unable to access services"
        elif failed_service == 'payment-service':
            return "Critical - All payment transactions blocked, orders cannot be completed"
        elif total_affected >= 2:
            return "High - Major service degradation affecting core user workflows"
        else:
            return "Medium - Partial service degradation with workarounds available"
    
    def _estimate_revenue_risk(self, failed_service: str, affected_services: List[str]) -> str:
        """Estimate revenue risk"""
        total_affected = len(affected_services) + 1
        
        if failed_service == 'auth-service' or total_affected >= 3:
            return "$2.4M/hour - Complete transaction halt"
        elif failed_service == 'payment-service':
            return "$1.8M/hour - Payment processing blocked"
        elif total_affected >= 2:
            return "$850K/hour - Degraded transaction capacity"
        else:
            return "$200K/hour - Partial service impact"
    
    def _generate_recommendations(self, failed_service: str, affected_services: List[str]) -> List[str]:
        """Generate containment recommendations"""
        recommendations = []
        
        if failed_service == 'auth-service':
            recommendations.extend([
                "Implement circuit breaker on auth service dependencies",
                "Enable cached authentication tokens with extended TTL",
                "Deploy read-only mode for non-critical operations",
                "Activate emergency authentication bypass for critical services"
            ])
        elif failed_service == 'payment-service':
            recommendations.extend([
                "Queue payment requests for retry when service recovers",
                "Enable alternative payment gateway failover",
                "Implement graceful degradation for order processing",
                "Notify customers of payment processing delays"
            ])
        else:
            recommendations.extend([
                "Isolate failed service to prevent cascade",
                "Enable circuit breakers on dependent services",
                "Scale up healthy services to handle load",
                "Implement graceful degradation patterns"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "Monitor dependent service health metrics",
            "Prepare rollback procedures",
            "Activate incident response team"
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
        repo_path: Path to repository
        failed_service: Name of failed service
        
    Returns:
        Dictionary with blast radius analysis
    """
    analyzer = BlastAnalyzer()
    
    # Analyze repository
    analyzer.analyze_repository(repo_path)
    
    # Compute blast radius
    result = analyzer.compute_blast_radius(failed_service)
    
    return result.to_dict()


# Made with Bob