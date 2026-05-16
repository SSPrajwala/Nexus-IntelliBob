"""
Centralized Path Resolution Manager
Single source of truth for ALL path resolution across the Nexus-IntelliBob platform.
Ensures consistent path handling for local repos, GitHub URLs, and temporary repositories.
"""

import os
import re
import time
import shutil
from pathlib import Path
from typing import Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# PROJECT STRUCTURE CONSTANTS
# ============================================================================

# Absolute project root (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Core directories
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEMO_REPOS_DIR = PROJECT_ROOT / "demo-repos"
TEMP_REPOS_DIR = BACKEND_DIR / "temp-repos"

# Ensure temp directory exists
TEMP_REPOS_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"Path Manager initialized:")
logger.info(f"  PROJECT_ROOT: {PROJECT_ROOT}")
logger.info(f"  DEMO_REPOS_DIR: {DEMO_REPOS_DIR}")
logger.info(f"  TEMP_REPOS_DIR: {TEMP_REPOS_DIR}")


# ============================================================================
# PATH RESOLUTION FUNCTIONS
# ============================================================================

def is_github_url(input_path: str) -> bool:
    """
    Check if input is a GitHub repository URL.
    
    Args:
        input_path: Input string to check
        
    Returns:
        True if valid GitHub URL
    """
    if not input_path or not isinstance(input_path, str):
        return False
    
    github_patterns = [
        r'^https?://github\.com/[\w-]+/[\w.-]+/?$',
        r'^git@github\.com:[\w-]+/[\w.-]+\.git$',
        r'^https?://github\.com/[\w-]+/[\w.-]+\.git$'
    ]
    
    return any(re.match(pattern, input_path.strip()) for pattern in github_patterns)


def normalize_repo_input(repo_input: str) -> Tuple[str, str]:
    """
    Normalize repository input to determine type and clean value.
    
    Args:
        repo_input: Raw repository input (path or URL)
        
    Returns:
        Tuple of (input_type, normalized_value)
        input_type: 'github_url', 'relative_path', or 'absolute_path'
    """
    if not repo_input or not repo_input.strip():
        raise ValueError("Repository input cannot be empty")
    
    repo_input = repo_input.strip()
    
    # Check if GitHub URL
    if is_github_url(repo_input):
        return ('github_url', repo_input)
    
    # Convert to Path for analysis
    path = Path(repo_input)
    
    # Check if absolute path
    if path.is_absolute():
        return ('absolute_path', str(path))
    
    # Otherwise it's a relative path
    return ('relative_path', str(path))


def resolve_repo_path(repo_input: str, allow_github: bool = False) -> Optional[Path]:
    """
    Resolve repository input to an absolute local path.
    
    This is the SINGLE SOURCE OF TRUTH for path resolution.
    All modules MUST use this function.
    
    Args:
        repo_input: Repository path or URL
        allow_github: If True, returns None for GitHub URLs (caller must clone)
        
    Returns:
        Resolved absolute Path object, or None if GitHub URL and allow_github=True
        
    Raises:
        ValueError: If path is invalid, doesn't exist, or is GitHub URL when not allowed
    """
    input_type, normalized = normalize_repo_input(repo_input)
    
    # Handle GitHub URLs
    if input_type == 'github_url':
        if allow_github:
            # Caller will handle cloning
            return None
        else:
            raise ValueError(
                f"GitHub URL provided but not allowed in this context: {repo_input}\n"
                f"Use allow_github=True if GitHub URLs should be handled by caller."
            )
    
    # Handle absolute paths
    if input_type == 'absolute_path':
        path = Path(normalized)
        if not path.exists():
            raise ValueError(f"Absolute path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        return path.resolve()
    
    # Handle relative paths - try multiple resolution strategies
    relative_path = Path(normalized)
    
    # Strategy 1: Resolve relative to PROJECT_ROOT (most common for demo-repos)
    resolved = (PROJECT_ROOT / relative_path).resolve()
    if resolved.exists() and resolved.is_dir():
        logger.debug(f"Resolved '{repo_input}' relative to PROJECT_ROOT: {resolved}")
        return resolved
    
    # Strategy 2: Resolve relative to DEMO_REPOS_DIR
    resolved = (DEMO_REPOS_DIR / relative_path).resolve()
    if resolved.exists() and resolved.is_dir():
        logger.debug(f"Resolved '{repo_input}' relative to DEMO_REPOS_DIR: {resolved}")
        return resolved
    
    # Strategy 3: Resolve relative to TEMP_REPOS_DIR (for cloned repos)
    resolved = (TEMP_REPOS_DIR / relative_path).resolve()
    if resolved.exists() and resolved.is_dir():
        logger.debug(f"Resolved '{repo_input}' relative to TEMP_REPOS_DIR: {resolved}")
        return resolved
    
    # Strategy 4: Try as-is from current working directory (last resort)
    resolved = relative_path.resolve()
    if resolved.exists() and resolved.is_dir():
        logger.debug(f"Resolved '{repo_input}' from CWD: {resolved}")
        return resolved
    
    # Path not found - provide helpful error
    raise ValueError(
        f"Repository path not found: {repo_input}\n"
        f"Tried:\n"
        f"  - Relative to project root: {PROJECT_ROOT / relative_path}\n"
        f"  - Relative to demo-repos: {DEMO_REPOS_DIR / relative_path}\n"
        f"  - Relative to temp-repos: {TEMP_REPOS_DIR / relative_path}\n"
        f"  - Absolute/CWD: {relative_path.resolve()}\n"
        f"Suggestion: Use 'demo-repos/payment-system' for demo repositories"
    )


def generate_temp_repo_path(github_url: str) -> Path:
    """
    Generate a unique temporary repository path for a GitHub URL.
    
    Args:
        github_url: GitHub repository URL
        
    Returns:
        Path object for temporary repository location
    """
    # Extract repo name from URL
    match = re.search(r'github\.com[:/]([\w-]+)/([\w.-]+)', github_url)
    if not match:
        raise ValueError(f"Invalid GitHub URL: {github_url}")
    
    owner, repo = match.groups()
    repo = repo.replace('.git', '')
    
    # Create unique name with timestamp
    timestamp = int(time.time())
    safe_name = re.sub(r'[^\w-]', '_', f"{owner}_{repo}")
    temp_path = TEMP_REPOS_DIR / f"{safe_name}_{timestamp}"
    
    return temp_path


# ============================================================================
# TEMPORARY REPOSITORY LIFECYCLE MANAGEMENT
# ============================================================================

class TempRepoManager:
    """Manages lifecycle of temporary cloned repositories."""
    
    def __init__(self):
        self._tracked_repos = {}  # path -> creation_time
    
    def track(self, repo_path: Union[str, Path]):
        """Track a temporary repository for lifecycle management."""
        path_str = str(repo_path)
        self._tracked_repos[path_str] = time.time()
        logger.debug(f"Tracking temp repo: {path_str}")
    
    def cleanup(self, repo_path: Union[str, Path], ignore_errors: bool = True) -> bool:
        """
        Clean up a temporary repository.
        
        Args:
            repo_path: Path to repository
            ignore_errors: If True, suppress errors during cleanup
            
        Returns:
            True if cleanup successful
        """
        path = Path(repo_path)
        path_str = str(path)
        
        try:
            # Only cleanup if it's in temp-repos directory
            if not str(path.resolve()).startswith(str(TEMP_REPOS_DIR)):
                logger.warning(f"Refusing to cleanup non-temp path: {path}")
                return False
            
            if path.exists():
                shutil.rmtree(path, ignore_errors=ignore_errors)
                logger.info(f"Cleaned up temp repo: {path}")
            
            # Remove from tracking
            if path_str in self._tracked_repos:
                del self._tracked_repos[path_str]
            
            return True
            
        except Exception as e:
            if ignore_errors:
                logger.warning(f"Error cleaning up {path}: {e}")
                return False
            else:
                raise
    
    def cleanup_stale(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up repositories older than specified age.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour)
            
        Returns:
            Number of repositories cleaned up
        """
        current_time = time.time()
        cleaned = 0
        
        for repo_path, created_time in list(self._tracked_repos.items()):
            if current_time - created_time > max_age_seconds:
                if self.cleanup(repo_path):
                    cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} stale repositories")
        
        return cleaned
    
    def cleanup_all(self) -> int:
        """
        Clean up all tracked temporary repositories.
        
        Returns:
            Number of repositories cleaned up
        """
        cleaned = 0
        for repo_path in list(self._tracked_repos.keys()):
            if self.cleanup(repo_path):
                cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} temporary repositories")
        return cleaned


# Global temp repo manager instance
_temp_manager = TempRepoManager()


def get_temp_manager() -> TempRepoManager:
    """Get the global temporary repository manager."""
    return _temp_manager


# ============================================================================
# DIRECTORY VALIDATION
# ============================================================================

def ensure_temp_directories():
    """Ensure all required temporary directories exist."""
    TEMP_REPOS_DIR.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured temp directory exists: {TEMP_REPOS_DIR}")


def validate_demo_repos() -> Tuple[bool, str]:
    """
    Validate that demo repositories exist and are accessible.
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not DEMO_REPOS_DIR.exists():
        return False, f"Demo repos directory not found: {DEMO_REPOS_DIR}"
    
    if not DEMO_REPOS_DIR.is_dir():
        return False, f"Demo repos path is not a directory: {DEMO_REPOS_DIR}"
    
    # Check for payment-system demo
    payment_system = DEMO_REPOS_DIR / "payment-system"
    if not payment_system.exists():
        return False, f"Payment system demo not found: {payment_system}"
    
    return True, "Demo repositories validated successfully"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_relative_path(absolute_path: Union[str, Path], base: Optional[Path] = None) -> str:
    """
    Get relative path from absolute path.
    
    Args:
        absolute_path: Absolute path to convert
        base: Base path (defaults to PROJECT_ROOT)
        
    Returns:
        Relative path as string
    """
    if base is None:
        base = PROJECT_ROOT
    
    path = Path(absolute_path)
    try:
        return str(path.relative_to(base))
    except ValueError:
        # Path is not relative to base, return as-is
        return str(path)


def is_temp_repo(repo_path: Union[str, Path]) -> bool:
    """
    Check if a repository path is in the temporary repos directory.
    
    Args:
        repo_path: Path to check
        
    Returns:
        True if path is in temp-repos
    """
    path = Path(repo_path).resolve()
    return str(path).startswith(str(TEMP_REPOS_DIR))


# Made with Bob