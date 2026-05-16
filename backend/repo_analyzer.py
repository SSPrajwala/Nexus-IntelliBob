"""
Repository Architecture Analyzer
Analyzes repository structure and generates architecture intelligence
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)

# Directories to exclude from analysis
EXCLUDED_DIRS = {
    'node_modules', '.git', 'dist', 'build', 'venv', '__pycache__',
    '.next', 'out', 'target', 'bin', 'obj', '.vscode', '.idea',
    'coverage', '.pytest_cache', '.mypy_cache', 'vendor'
}


class RepositoryAnalyzer:
    """Analyzes repository architecture and generates intelligence"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
    def detect_microservices(self) -> List[Dict]:
        """
        Detect microservices in the repository
        
        Returns:
            List of detected services with metadata
        """
        services = []
        
        try:
            for item in self.repo_path.iterdir():
                if item.is_dir() and item.name not in EXCLUDED_DIRS:
                    # Check for service indicators
                    service_files = ['main.py', 'app.py', 'server.js', 'index.js', 'main.go', 'server.py']
                    
                    for service_file in service_files:
                        if (item / service_file).exists():
                            services.append({
                                'name': item.name,
                                'path': str(item.relative_to(self.repo_path)),
                                'entry_point': service_file,
                                'type': self._detect_service_type(item)
                            })
                            break
        except Exception as e:
            logger.warning(f"Error detecting microservices: {e}")
        
        return services
    
    def _detect_service_type(self, service_path: Path) -> str:
        """Detect the type of service (API, frontend, worker, etc.)"""
        service_name = service_path.name.lower()
        
        if 'api' in service_name or 'backend' in service_name:
            return 'api'
        elif 'frontend' in service_name or 'ui' in service_name or 'web' in service_name:
            return 'frontend'
        elif 'worker' in service_name or 'job' in service_name or 'queue' in service_name:
            return 'worker'
        elif 'auth' in service_name:
            return 'authentication'
        elif 'payment' in service_name:
            return 'payment'
        elif 'notification' in service_name:
            return 'notification'
        else:
            return 'service'
    
    def detect_databases(self) -> List[str]:
        """
        Detect database usage in repository
        
        Returns:
            List of detected database types
        """
        databases = set()
        
        try:
            # Check configuration files
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                for file in files:
                    if file in ['package.json', 'requirements.txt', 'go.mod', 'pom.xml']:
                        file_path = Path(root) / file
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                            
                            if 'postgres' in content or 'pg' in content:
                                databases.add('PostgreSQL')
                            if 'mysql' in content:
                                databases.add('MySQL')
                            if 'mongodb' in content or 'mongo' in content:
                                databases.add('MongoDB')
                            if 'redis' in content:
                                databases.add('Redis')
                            if 'elasticsearch' in content:
                                databases.add('Elasticsearch')
                            if 'cassandra' in content:
                                databases.add('Cassandra')
                            if 'dynamodb' in content:
                                databases.add('DynamoDB')
                            if 'sqlite' in content:
                                databases.add('SQLite')
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Error detecting databases: {e}")
        
        return list(databases)
    
    def detect_queues(self) -> List[str]:
        """
        Detect message queue systems
        
        Returns:
            List of detected queue systems
        """
        queues = set()
        
        try:
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                for file in files:
                    if file in ['package.json', 'requirements.txt', 'go.mod']:
                        file_path = Path(root) / file
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                            
                            if 'rabbitmq' in content or 'amqp' in content:
                                queues.add('RabbitMQ')
                            if 'kafka' in content:
                                queues.add('Kafka')
                            if 'celery' in content:
                                queues.add('Celery')
                            if 'bull' in content or 'bullmq' in content:
                                queues.add('Bull')
                            if 'sqs' in content:
                                queues.add('AWS SQS')
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Error detecting queues: {e}")
        
        return list(queues)
    
    def detect_external_integrations(self) -> List[str]:
        """
        Detect external service integrations
        
        Returns:
            List of detected external integrations
        """
        integrations = set()
        
        try:
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.go')):
                        file_path = Path(root) / file
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                            
                            if 'stripe' in content:
                                integrations.add('Stripe')
                            if 'aws' in content or 'boto3' in content:
                                integrations.add('AWS')
                            if 'sendgrid' in content:
                                integrations.add('SendGrid')
                            if 'twilio' in content:
                                integrations.add('Twilio')
                            if 'slack' in content:
                                integrations.add('Slack')
                            if 'github' in content and 'api' in content:
                                integrations.add('GitHub API')
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Error detecting integrations: {e}")
        
        return list(integrations)
    
    def calculate_complexity_score(self, services: List[Dict], databases: List[str], 
                                   queues: List[str], integrations: List[str]) -> int:
        """
        Calculate operational complexity score (0-100)
        
        Args:
            services: List of detected services
            databases: List of detected databases
            queues: List of detected queues
            integrations: List of detected integrations
            
        Returns:
            Complexity score (0-100)
        """
        score = 0
        
        # Base score from service count
        service_count = len(services)
        if service_count == 1:
            score += 10
        elif service_count <= 3:
            score += 30
        elif service_count <= 5:
            score += 50
        elif service_count <= 10:
            score += 70
        else:
            score += 90
        
        # Add complexity for databases
        score += min(len(databases) * 5, 20)
        
        # Add complexity for queues
        score += min(len(queues) * 8, 20)
        
        # Add complexity for external integrations
        score += min(len(integrations) * 3, 15)
        
        return min(score, 100)
    
    def generate_architecture_summary(self) -> str:
        """
        Generate human-readable architecture summary
        
        Returns:
            Architecture summary text
        """
        services = self.detect_microservices()
        databases = self.detect_databases()
        queues = self.detect_queues()
        
        if len(services) <= 1:
            arch_type = "monolithic application"
        elif len(services) <= 3:
            arch_type = "small microservices architecture"
        else:
            arch_type = "distributed microservices architecture"
        
        summary_parts = [f"This is a {arch_type}"]
        
        if services:
            summary_parts.append(f"with {len(services)} service(s)")
        
        if databases:
            db_list = ", ".join(databases)
            summary_parts.append(f"using {db_list} for data persistence")
        
        if queues:
            queue_list = ", ".join(queues)
            summary_parts.append(f"with {queue_list} for async processing")
        
        return " ".join(summary_parts) + "."
    
    def generate_risk_profile(self, services: List[Dict], databases: List[str],
                             queues: List[str], integrations: List[str]) -> Dict:
        """
        Generate engineering risk profile
        
        Returns:
            Risk profile dictionary
        """
        risks = []
        
        # Check for single points of failure
        if len(services) > 3 and not queues:
            risks.append({
                'type': 'No Message Queue',
                'severity': 'medium',
                'description': 'Multiple services without async communication layer increases coupling'
            })
        
        if len(databases) > 2:
            risks.append({
                'type': 'Database Sprawl',
                'severity': 'medium',
                'description': 'Multiple database types increase operational complexity'
            })
        
        if len(integrations) > 5:
            risks.append({
                'type': 'Integration Complexity',
                'severity': 'high',
                'description': 'High number of external dependencies increases failure surface'
            })
        
        if len(services) > 10:
            risks.append({
                'type': 'Microservices Complexity',
                'severity': 'high',
                'description': 'Large number of services may indicate over-fragmentation'
            })
        
        return {
            'total_risks': len(risks),
            'risks': risks,
            'overall_risk_level': 'high' if len(risks) >= 3 else 'medium' if len(risks) >= 1 else 'low'
        }
    
    def generate_topology_overview(self, services: List[Dict]) -> Dict:
        """
        Generate system topology overview
        
        Returns:
            Topology overview dictionary
        """
        service_types = {}
        for service in services:
            stype = service.get('type', 'service')
            service_types[stype] = service_types.get(stype, 0) + 1
        
        return {
            'total_services': len(services),
            'service_types': service_types,
            'architecture_pattern': 'microservices' if len(services) > 1 else 'monolith',
            'service_list': [s['name'] for s in services]
        }
    
    def analyze(self) -> Dict:
        """
        Perform complete repository analysis
        
        Returns:
            Complete analysis results
        """
        logger.info(f"Analyzing repository: {self.repo_path}")
        
        # Detect components
        services = self.detect_microservices()
        databases = self.detect_databases()
        queues = self.detect_queues()
        integrations = self.detect_external_integrations()
        
        # Generate insights
        complexity_score = self.calculate_complexity_score(services, databases, queues, integrations)
        architecture_summary = self.generate_architecture_summary()
        risk_profile = self.generate_risk_profile(services, databases, queues, integrations)
        topology = self.generate_topology_overview(services)
        
        return {
            'repository_path': str(self.repo_path),
            'services': services,
            'databases': databases,
            'queues': queues,
            'external_integrations': integrations,
            'complexity_score': complexity_score,
            'architecture_summary': architecture_summary,
            'risk_profile': risk_profile,
            'topology': topology
        }


def analyze_repository(repo_path: str) -> Dict:
    """
    Main entry point for repository analysis
    
    Args:
        repo_path: Path to repository
        
    Returns:
        Analysis results dictionary
    """
    analyzer = RepositoryAnalyzer(repo_path)
    return analyzer.analyze()


# Made with Bob