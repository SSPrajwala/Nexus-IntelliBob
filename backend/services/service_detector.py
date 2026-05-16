"""
Dynamic Service Detection
Automatically detects services, modules, and critical components in any repository.
Works for microservices, monoliths, and any project structure.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)


class ServiceDetector:
    """Detects services and critical components in a repository."""
    
    # Common service/module indicators
    SERVICE_INDICATORS = [
        'service', 'api', 'app', 'server', 'backend', 'frontend',
        'worker', 'job', 'queue', 'processor', 'handler', 'gateway'
    ]
    
    # Entry point files that indicate a service
    ENTRY_POINT_FILES = [
        'main.py', 'app.py', 'server.py', '__main__.py',
        'index.js', 'server.js', 'app.js', 'main.js',
        'main.go', 'server.go',
        'Main.java', 'Application.java',
        'main.rs', 'lib.rs'
    ]
    
    # Configuration files that indicate a deployable component
    CONFIG_FILES = [
        'Dockerfile', 'docker-compose.yml',
        'package.json', 'requirements.txt', 'go.mod',
        'pom.xml', 'build.gradle', 'Cargo.toml'
    ]
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
    def detect_services(self) -> List[Dict]:
        """
        Detect all services/components in the repository.
        
        Returns:
            List of service dictionaries with metadata
        """
        services = []
        
        # Strategy 1: Look for microservice directories
        microservices = self._detect_microservices()
        services.extend(microservices)
        
        # Strategy 2: Look for monolith modules
        if not services:
            modules = self._detect_modules()
            services.extend(modules)
        
        # Strategy 3: Fallback to critical files
        if not services:
            critical_files = self._detect_critical_files()
            services.extend(critical_files)
        
        # Sort by criticality score
        services.sort(key=lambda s: s.get('criticality_score', 0), reverse=True)
        
        logger.info(f"Detected {len(services)} services/components")
        return services
    
    def _detect_microservices(self) -> List[Dict]:
        """Detect microservice-style architecture."""
        services = []
        
        try:
            for item in self.repo_path.iterdir():
                if not item.is_dir():
                    continue
                
                # Skip common non-service directories
                if item.name.startswith('.') or item.name in [
                    'node_modules', 'venv', '__pycache__', 'dist', 'build',
                    'target', 'out', 'vendor', 'docs', 'tests', 'test'
                ]:
                    continue
                
                # Check if directory looks like a service
                is_service = False
                service_type = 'unknown'
                entry_point = None
                
                # Check for service indicators in name
                name_lower = item.name.lower()
                for indicator in self.SERVICE_INDICATORS:
                    if indicator in name_lower:
                        is_service = True
                        service_type = indicator
                        break
                
                # Check for entry point files
                for entry_file in self.ENTRY_POINT_FILES:
                    if (item / entry_file).exists():
                        is_service = True
                        entry_point = entry_file
                        break
                
                # Check for config files
                has_config = any((item / config).exists() for config in self.CONFIG_FILES)
                if has_config:
                    is_service = True
                
                if is_service:
                    criticality = self._calculate_criticality(item, name_lower)
                    
                    services.append({
                        'id': item.name,
                        'name': item.name,
                        'display_name': self._format_display_name(item.name),
                        'type': service_type,
                        'path': str(item.relative_to(self.repo_path)),
                        'entry_point': entry_point,
                        'criticality_score': criticality,
                        'detection_method': 'microservice'
                    })
        
        except Exception as e:
            logger.warning(f"Error detecting microservices: {e}")
        
        return services
    
    def _detect_modules(self) -> List[Dict]:
        """Detect modules in a monolithic structure."""
        modules = []
        
        try:
            # Look for Python packages
            for item in self.repo_path.rglob('__init__.py'):
                parent = item.parent
                if parent == self.repo_path:
                    continue
                
                # Skip test directories
                if 'test' in str(parent).lower():
                    continue
                
                module_name = parent.name
                criticality = self._calculate_criticality(parent, module_name.lower())
                
                modules.append({
                    'id': module_name,
                    'name': module_name,
                    'display_name': self._format_display_name(module_name),
                    'type': 'module',
                    'path': str(parent.relative_to(self.repo_path)),
                    'entry_point': '__init__.py',
                    'criticality_score': criticality,
                    'detection_method': 'module'
                })
            
            # Look for JavaScript/TypeScript modules
            for item in self.repo_path.rglob('index.js'):
                parent = item.parent
                if parent == self.repo_path:
                    continue
                
                if 'node_modules' in str(parent):
                    continue
                
                module_name = parent.name
                criticality = self._calculate_criticality(parent, module_name.lower())
                
                modules.append({
                    'id': module_name,
                    'name': module_name,
                    'display_name': self._format_display_name(module_name),
                    'type': 'module',
                    'path': str(parent.relative_to(self.repo_path)),
                    'entry_point': 'index.js',
                    'criticality_score': criticality,
                    'detection_method': 'module'
                })
        
        except Exception as e:
            logger.warning(f"Error detecting modules: {e}")
        
        return modules
    
    def _detect_critical_files(self) -> List[Dict]:
        """Detect critical files as fallback."""
        files = []
        
        try:
            # Look for main entry points
            for entry_file in self.ENTRY_POINT_FILES:
                for item in self.repo_path.rglob(entry_file):
                    if 'test' in str(item).lower() or 'node_modules' in str(item):
                        continue
                    
                    parent = item.parent
                    name = parent.name if parent != self.repo_path else item.stem
                    
                    files.append({
                        'id': name,
                        'name': name,
                        'display_name': self._format_display_name(name),
                        'type': 'file',
                        'path': str(item.relative_to(self.repo_path)),
                        'entry_point': item.name,
                        'criticality_score': 50,
                        'detection_method': 'file'
                    })
        
        except Exception as e:
            logger.warning(f"Error detecting critical files: {e}")
        
        return files
    
    def _calculate_criticality(self, path: Path, name_lower: str) -> int:
        """Calculate criticality score (0-100) for a component."""
        score = 50  # Base score
        
        # High criticality keywords
        if any(keyword in name_lower for keyword in ['auth', 'payment', 'security', 'user']):
            score += 30
        
        # Medium criticality keywords
        if any(keyword in name_lower for keyword in ['api', 'gateway', 'core', 'main']):
            score += 20
        
        # Check for dependencies (more dependencies = more critical)
        try:
            file_count = sum(1 for _ in path.rglob('*') if _.is_file())
            if file_count > 50:
                score += 15
            elif file_count > 20:
                score += 10
        except:
            pass
        
        # Check for database connections
        try:
            for file in path.rglob('*.py'):
                content = file.read_text(encoding='utf-8', errors='ignore')
                if 'database' in content.lower() or 'db' in content.lower():
                    score += 10
                    break
        except:
            pass
        
        return min(score, 100)
    
    def _format_display_name(self, name: str) -> str:
        """Format service name for display."""
        # Remove common suffixes
        name = re.sub(r'[-_](service|api|app|server)$', '', name, flags=re.IGNORECASE)
        
        # Convert to title case
        name = name.replace('-', ' ').replace('_', ' ').title()
        
        return name
    
    def get_auto_selected_service(self) -> Optional[Dict]:
        """
        Automatically select the most critical service for analysis.
        
        Returns:
            Service dictionary or None
        """
        services = self.detect_services()
        
        if not services:
            return None
        
        # Return highest criticality service
        return services[0]
    
    def get_service_summary(self) -> Dict:
        """
        Get summary of detected services.
        
        Returns:
            Summary dictionary
        """
        services = self.detect_services()
        
        return {
            'total_services': len(services),
            'services': services,
            'architecture_type': self._determine_architecture_type(services),
            'auto_selected': self.get_auto_selected_service()
        }
    
    def _determine_architecture_type(self, services: List[Dict]) -> str:
        """Determine architecture type based on detected services."""
        if not services:
            return 'unknown'
        
        microservices = [s for s in services if s['detection_method'] == 'microservice']
        
        if len(microservices) >= 3:
            return 'microservices'
        elif len(microservices) >= 1:
            return 'hybrid'
        else:
            return 'monolith'


def detect_services(repo_path: str) -> List[Dict]:
    """
    Convenience function to detect services in a repository.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of detected services
    """
    detector = ServiceDetector(repo_path)
    return detector.detect_services()


def get_service_summary(repo_path: str) -> Dict:
    """
    Get service detection summary for a repository.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        Service summary dictionary
    """
    detector = ServiceDetector(repo_path)
    return detector.get_service_summary()


# Made with Bob