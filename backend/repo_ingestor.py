"""
Repository Ingestor
Handles GitHub repository cloning and ingestion for analysis with metadata extraction
"""
import os
import re
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import logging

logger = logging.getLogger(__name__)

# Maximum repository size in MB
MAX_REPO_SIZE_MB = 500

# Directories to exclude from scanning
EXCLUDED_DIRS = {
    'node_modules', '.git', 'dist', 'build', 'venv', '__pycache__',
    '.next', 'out', 'target', 'bin', 'obj', '.vscode', '.idea',
    'coverage', '.pytest_cache', '.mypy_cache', 'vendor'
}


class RepoIngestor:
    """Handles repository ingestion from GitHub with enhanced metadata extraction"""
    
    def __init__(self, temp_dir: str = "temp-repos"):
        self.temp_dir = temp_dir
        self._ensure_temp_dir()
        self._tracked_repos: Dict[str, float] = {}
    
    def _ensure_temp_dir(self):
        """Ensure temp directory exists"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            logger.info(f"Created temp directory: {self.temp_dir}")
    
    def is_github_url(self, url: str) -> bool:
        """
        Check if URL is a GitHub repository URL
        
        Args:
            url: URL to check
            
        Returns:
            True if valid GitHub URL
        """
        github_patterns = [
            r'^https?://github\.com/[\w-]+/[\w.-]+/?$',
            r'^git@github\.com:[\w-]+/[\w.-]+\.git$',
            r'^https?://github\.com/[\w-]+/[\w.-]+\.git$'
        ]
        
        return any(re.match(pattern, url.strip()) for pattern in github_patterns)
    
    def extract_repo_metadata(self, url: str) -> Tuple[str, str]:
        """
        Extract owner and repo name from GitHub URL
        
        Args:
            url: GitHub URL
            
        Returns:
            Tuple of (owner, repo_name)
        """
        match = re.search(r'github\.com[:/]([\w-]+)/([\w.-]+)', url)
        if not match:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        owner, repo = match.groups()
        repo = repo.replace('.git', '')
        
        return owner, repo
    
    def sanitize_repo_name(self, url: str) -> str:
        """
        Extract and sanitize repository name from URL
        
        Args:
            url: GitHub URL
            
        Returns:
            Sanitized repository name
        """
        owner, repo = self.extract_repo_metadata(url)
        sanitized = re.sub(r'[^\w-]', '_', f"{owner}_{repo}")
        return sanitized
    
    def clone_repository(self, github_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Clone a GitHub repository using shallow clone
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Tuple of (success, local_path, error_message)
        """
        if not self.is_github_url(github_url):
            return False, "", "Invalid GitHub URL format"
        
        try:
            # Sanitize repo name
            repo_name = self.sanitize_repo_name(github_url)
            local_path = os.path.join(self.temp_dir, repo_name)
            
            # Check if already cloned
            if os.path.exists(local_path):
                logger.info(f"Repository already exists at {local_path}")
                return True, local_path, None
            
            logger.info(f"Cloning repository: {github_url}")
            
            # Perform shallow clone (depth 1)
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', github_url, local_path],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned to {local_path}")
                return True, local_path, None
            else:
                error_msg = result.stderr or "Clone failed"
                logger.error(f"Clone failed: {error_msg}")
                return False, "", error_msg
        
        except subprocess.TimeoutExpired:
            error_msg = "Clone operation timed out"
            logger.error(error_msg)
            return False, "", error_msg
        
        except FileNotFoundError:
            error_msg = "Git command not found. Please ensure Git is installed."
            logger.error(error_msg)
            return False, "", error_msg
        
        except Exception as e:
            error_msg = f"Clone failed: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def cleanup_repository(self, repo_path: str) -> bool:
        """
        Clean up a cloned repository
        
        Args:
            repo_path: Path to repository to clean up
            
        Returns:
            True if cleanup successful
        """
        try:
            if os.path.exists(repo_path) and repo_path.startswith(self.temp_dir):
                shutil.rmtree(repo_path)
                logger.info(f"Cleaned up repository: {repo_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False
    
    def cleanup_all(self) -> int:
        """
        Clean up all temporary repositories
        
        Returns:
            Number of repositories cleaned up
        """
        count = 0
        try:
            if os.path.exists(self.temp_dir):
                for item in os.listdir(self.temp_dir):
                    item_path = os.path.join(self.temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        count += 1
                logger.info(f"Cleaned up {count} repositories")
        except Exception as e:
            logger.error(f"Cleanup all failed: {e}")
        
        return count
    
    def detect_languages(self, repo_path: str) -> Dict[str, int]:
        """
        Detect programming languages in repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary mapping language to file count
        """
        language_extensions = {
            'Python': ['.py'],
            'JavaScript': ['.js', '.jsx'],
            'TypeScript': ['.ts', '.tsx'],
            'Java': ['.java'],
            'Go': ['.go'],
            'Rust': ['.rs'],
            'C++': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
            'C': ['.c', '.h'],
            'Ruby': ['.rb'],
            'PHP': ['.php'],
            'Swift': ['.swift'],
            'Kotlin': ['.kt'],
            'C#': ['.cs'],
            'Shell': ['.sh', '.bash'],
            'SQL': ['.sql'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass'],
        }
        
        language_counts: Dict[str, int] = {}
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                for file in files:
                    ext = Path(file).suffix.lower()
                    for lang, extensions in language_extensions.items():
                        if ext in extensions:
                            language_counts[lang] = language_counts.get(lang, 0) + 1
                            break
        except Exception as e:
            logger.warning(f"Error detecting languages: {e}")
        
        return language_counts
    
    def detect_frameworks(self, repo_path: str) -> List[str]:
        """
        Detect frameworks and technologies used in repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of detected frameworks
        """
        frameworks = []
        path_obj = Path(repo_path)
        
        try:
            # Check for package.json (Node.js/JavaScript)
            package_json = path_obj / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                        
                        if 'next' in deps:
                            frameworks.append('Next.js')
                        if 'react' in deps:
                            frameworks.append('React')
                        if 'vue' in deps:
                            frameworks.append('Vue.js')
                        if 'express' in deps:
                            frameworks.append('Express')
                        if 'angular' in deps or '@angular/core' in deps:
                            frameworks.append('Angular')
                except Exception as e:
                    logger.warning(f"Error parsing package.json: {e}")
            
            # Check for requirements.txt (Python)
            requirements = path_obj / 'requirements.txt'
            if requirements.exists():
                try:
                    with open(requirements, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if 'fastapi' in content:
                            frameworks.append('FastAPI')
                        if 'django' in content:
                            frameworks.append('Django')
                        if 'flask' in content:
                            frameworks.append('Flask')
                except Exception as e:
                    logger.warning(f"Error parsing requirements.txt: {e}")
            
            # Check for go.mod (Go)
            if (path_obj / 'go.mod').exists():
                frameworks.append('Go')
            
            # Check for Cargo.toml (Rust)
            if (path_obj / 'Cargo.toml').exists():
                frameworks.append('Rust')
            
            # Check for pom.xml or build.gradle (Java)
            if (path_obj / 'pom.xml').exists():
                frameworks.append('Maven')
            if (path_obj / 'build.gradle').exists() or (path_obj / 'build.gradle.kts').exists():
                frameworks.append('Gradle')
            
        except Exception as e:
            logger.warning(f"Error detecting frameworks: {e}")
        
        return frameworks
    
    def estimate_service_count(self, repo_path: str) -> int:
        """
        Estimate number of services/microservices in repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Estimated service count
        """
        service_indicators = 0
        path_obj = Path(repo_path)
        
        try:
            # Look for common service patterns
            for item in path_obj.iterdir():
                if item.is_dir() and item.name not in EXCLUDED_DIRS:
                    # Check if directory contains service indicators
                    if any((item / f).exists() for f in ['main.py', 'app.py', 'server.js', 'index.js', 'main.go']):
                        service_indicators += 1
            
            # If no clear services found, assume monolith
            return max(1, service_indicators)
        except Exception as e:
            logger.warning(f"Error estimating service count: {e}")
            return 1
    
    def get_repository_info(self, repo_path: str) -> Dict:
        """
        Get comprehensive information about a cloned repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with repository info including metadata
        """
        info = {
            "path": repo_path,
            "exists": os.path.exists(repo_path),
            "size_mb": 0,
            "file_count": 0,
            "detected_languages": {},
            "frameworks": [],
            "estimated_service_count": 1
        }
        
        if info["exists"]:
            try:
                # Calculate size
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(repo_path):
                    # Skip excluded directories
                    dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
                    
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                            file_count += 1
                        except OSError:
                            pass
                
                info["size_mb"] = round(total_size / (1024 * 1024), 2)
                info["file_count"] = file_count
                
                # Check size limit
                if info["size_mb"] > MAX_REPO_SIZE_MB:
                    logger.warning(f"Repository size ({info['size_mb']}MB) exceeds limit ({MAX_REPO_SIZE_MB}MB)")
                
                # Detect languages
                info["detected_languages"] = self.detect_languages(repo_path)
                
                # Detect frameworks
                info["frameworks"] = self.detect_frameworks(repo_path)
                
                # Estimate service count
                info["estimated_service_count"] = self.estimate_service_count(repo_path)
                
            except Exception as e:
                logger.warning(f"Error getting repo info: {e}")
        
        return info
    
    def track_repository(self, repo_path: str):
        """Track a repository for lifecycle management"""
        import time
        self._tracked_repos[repo_path] = time.time()
    
    def cleanup_old_repositories(self, max_age_seconds: int = 3600):
        """
        Cleanup repositories older than specified age
        
        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour)
            
        Returns:
            Number of repositories cleaned up
        """
        import time
        current_time = time.time()
        cleaned = 0
        
        for repo_path, created_time in list(self._tracked_repos.items()):
            if current_time - created_time > max_age_seconds:
                if self.cleanup_repository(repo_path):
                    del self._tracked_repos[repo_path]
                    cleaned += 1
        
        return cleaned


def ingest_repository(github_url: str) -> Tuple[bool, str, Optional[str]]:
    """
    Main entry point for repository ingestion
    
    Args:
        github_url: GitHub repository URL
        
    Returns:
        Tuple of (success, local_path, error_message)
    """
    ingestor = RepoIngestor()
    return ingestor.clone_repository(github_url)


# Made with Bob