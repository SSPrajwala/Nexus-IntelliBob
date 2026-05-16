"""
Core utilities for Nexus-IntelliBob backend.
"""

from .path_manager import (
    # Constants
    PROJECT_ROOT,
    BACKEND_DIR,
    FRONTEND_DIR,
    DEMO_REPOS_DIR,
    TEMP_REPOS_DIR,
    
    # Path resolution functions
    is_github_url,
    normalize_repo_input,
    resolve_repo_path,
    generate_temp_repo_path,
    
    # Temp repo management
    TempRepoManager,
    get_temp_manager,
    
    # Validation
    ensure_temp_directories,
    validate_demo_repos,
    
    # Utilities
    get_relative_path,
    is_temp_repo,
)

__all__ = [
    # Constants
    'PROJECT_ROOT',
    'BACKEND_DIR',
    'FRONTEND_DIR',
    'DEMO_REPOS_DIR',
    'TEMP_REPOS_DIR',
    
    # Path resolution
    'is_github_url',
    'normalize_repo_input',
    'resolve_repo_path',
    'generate_temp_repo_path',
    
    # Temp repo management
    'TempRepoManager',
    'get_temp_manager',
    
    # Validation
    'ensure_temp_directories',
    'validate_demo_repos',
    
    # Utilities
    'get_relative_path',
    'is_temp_repo',
]

# Made with Bob
