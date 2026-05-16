"""
System Health Validator
Validates system configuration, paths, and dependencies for Nexus-IntelliBob
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import logging

from core.path_manager import (
    PROJECT_ROOT,
    BACKEND_DIR,
    FRONTEND_DIR,
    DEMO_REPOS_DIR,
    TEMP_REPOS_DIR,
    validate_demo_repos,
    ensure_temp_directories
)

logger = logging.getLogger(__name__)


def check_git_availability() -> Tuple[bool, str]:
    """
    Check if Git is installed and available.
    
    Returns:
        Tuple of (is_available, version_or_error)
    """
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        else:
            return False, "Git command failed"
    except FileNotFoundError:
        return False, "Git not found - please install Git"
    except subprocess.TimeoutExpired:
        return False, "Git command timed out"
    except Exception as e:
        return False, f"Error checking Git: {str(e)}"


def check_directory_permissions(directory: Path) -> Tuple[bool, str]:
    """
    Check if directory exists and has proper permissions.
    
    Args:
        directory: Path to check
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        if not directory.exists():
            return False, f"Directory does not exist: {directory}"
        
        if not directory.is_dir():
            return False, f"Path is not a directory: {directory}"
        
        # Test read permission
        try:
            list(directory.iterdir())
        except PermissionError:
            return False, f"No read permission: {directory}"
        
        # Test write permission
        test_file = directory / ".nexus_write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            return False, f"No write permission: {directory}"
        except Exception as e:
            return False, f"Permission test failed: {str(e)}"
        
        return True, "OK"
        
    except Exception as e:
        return False, f"Error checking permissions: {str(e)}"


def check_demo_repositories() -> Tuple[bool, str, List[str]]:
    """
    Check demo repositories exist and are valid.
    
    Returns:
        Tuple of (is_valid, message, found_repos)
    """
    is_valid, message = validate_demo_repos()
    
    found_repos = []
    if DEMO_REPOS_DIR.exists():
        try:
            for item in DEMO_REPOS_DIR.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    found_repos.append(item.name)
        except Exception as e:
            return False, f"Error scanning demo repos: {str(e)}", []
    
    return is_valid, message, found_repos


def check_python_dependencies() -> Tuple[bool, str, List[str]]:
    """
    Check if required Python packages are installed.
    
    Returns:
        Tuple of (all_installed, message, missing_packages)
    """
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, f"Missing packages: {', '.join(missing)}", missing
    else:
        return True, "All required packages installed", []


def check_temp_directory() -> Tuple[bool, str, Dict]:
    """
    Check temporary directory status.
    
    Returns:
        Tuple of (is_valid, message, stats)
    """
    try:
        ensure_temp_directories()
        
        # Count items in temp directory
        temp_count = 0
        temp_size_mb = 0
        
        if TEMP_REPOS_DIR.exists():
            for item in TEMP_REPOS_DIR.iterdir():
                if item.is_dir():
                    temp_count += 1
                    # Calculate size
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            try:
                                temp_size_mb += os.path.getsize(os.path.join(root, file))
                            except OSError:
                                pass
        
        temp_size_mb = round(temp_size_mb / (1024 * 1024), 2)
        
        stats = {
            "path": str(TEMP_REPOS_DIR),
            "exists": TEMP_REPOS_DIR.exists(),
            "temp_repos_count": temp_count,
            "total_size_mb": temp_size_mb
        }
        
        return True, "Temp directory OK", stats
        
    except Exception as e:
        return False, f"Error checking temp directory: {str(e)}", {}


def validate_system() -> Dict:
    """
    Perform complete system validation.
    
    Returns:
        Dictionary with validation results
    """
    checks = []
    warnings = []
    errors = []
    
    # Check 1: Git availability
    git_ok, git_msg = check_git_availability()
    checks.append({
        "name": "Git Availability",
        "status": "pass" if git_ok else "fail",
        "message": git_msg
    })
    if not git_ok:
        errors.append(f"Git not available: {git_msg}")
    
    # Check 2: Project directories
    for name, directory in [
        ("Project Root", PROJECT_ROOT),
        ("Backend Directory", BACKEND_DIR),
        ("Frontend Directory", FRONTEND_DIR),
        ("Demo Repos Directory", DEMO_REPOS_DIR),
        ("Temp Repos Directory", TEMP_REPOS_DIR)
    ]:
        dir_ok, dir_msg = check_directory_permissions(directory)
        checks.append({
            "name": name,
            "status": "pass" if dir_ok else "fail",
            "message": dir_msg,
            "path": str(directory)
        })
        if not dir_ok:
            errors.append(f"{name}: {dir_msg}")
    
    # Check 3: Demo repositories
    demo_ok, demo_msg, demo_repos = check_demo_repositories()
    checks.append({
        "name": "Demo Repositories",
        "status": "pass" if demo_ok else "fail",
        "message": demo_msg,
        "found_repos": demo_repos
    })
    if not demo_ok:
        errors.append(f"Demo repos: {demo_msg}")
    
    # Check 4: Python dependencies
    deps_ok, deps_msg, missing_deps = check_python_dependencies()
    checks.append({
        "name": "Python Dependencies",
        "status": "pass" if deps_ok else "fail",
        "message": deps_msg,
        "missing": missing_deps
    })
    if not deps_ok:
        errors.append(f"Dependencies: {deps_msg}")
    
    # Check 5: Temp directory
    temp_ok, temp_msg, temp_stats = check_temp_directory()
    checks.append({
        "name": "Temporary Directory",
        "status": "pass" if temp_ok else "fail",
        "message": temp_msg,
        "stats": temp_stats
    })
    if not temp_ok:
        errors.append(f"Temp directory: {temp_msg}")
    
    # Add warnings for temp directory size
    if temp_stats.get("temp_repos_count", 0) > 5:
        warnings.append(f"Many temporary repositories ({temp_stats['temp_repos_count']}) - consider cleanup")
    
    if temp_stats.get("total_size_mb", 0) > 500:
        warnings.append(f"Large temp directory size ({temp_stats['total_size_mb']}MB) - consider cleanup")
    
    # Determine overall status
    if errors:
        status = "unhealthy"
    elif warnings:
        status = "degraded"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "paths": {
            "project_root": str(PROJECT_ROOT),
            "backend_dir": str(BACKEND_DIR),
            "frontend_dir": str(FRONTEND_DIR),
            "demo_repos_dir": str(DEMO_REPOS_DIR),
            "temp_repos_dir": str(TEMP_REPOS_DIR)
        },
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for c in checks if c["status"] == "pass"),
            "failed": sum(1 for c in checks if c["status"] == "fail"),
            "warnings_count": len(warnings),
            "errors_count": len(errors)
        }
    }


# Made with Bob