"""
Repository Ingestor
Handles GitHub repository cloning and ingestion for analysis
"""
import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RepoIngestor:
    """Handles repository ingestion from GitHub"""
    
    def __init__(self, temp_dir: str = "temp-repos"):
        self.temp_dir = temp_dir
        self._ensure_temp_dir()
    
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
    
    def sanitize_repo_name(self, url: str) -> str:
        """
        Extract and sanitize repository name from URL
        
        Args:
            url: GitHub URL
            
        Returns:
            Sanitized repository name
        """
        # Extract repo name from URL
        match = re.search(r'github\.com[:/]([\w-]+)/([\w.-]+)', url)
        if not match:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        owner, repo = match.groups()
        
        # Remove .git suffix if present
        repo = repo.replace('.git', '')
        
        # Sanitize: only alphanumeric, dash, underscore
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
    
    def get_repository_info(self, repo_path: str) -> dict:
        """
        Get basic information about a cloned repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with repository info
        """
        info = {
            "path": repo_path,
            "exists": os.path.exists(repo_path),
            "size_mb": 0,
            "file_count": 0
        }
        
        if info["exists"]:
            try:
                # Calculate size
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(repo_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
                        file_count += 1
                
                info["size_mb"] = round(total_size / (1024 * 1024), 2)
                info["file_count"] = file_count
            except Exception as e:
                logger.warning(f"Error getting repo info: {e}")
        
        return info


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