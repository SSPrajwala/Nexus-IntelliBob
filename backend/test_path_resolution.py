"""Test path resolution for both relative and absolute paths"""
import risk_scanner
from pathlib import Path

print("="*70)
print("TESTING PATH RESOLUTION")
print("="*70)

# Test 1: Relative path from project root
print("\n1. Testing relative path: 'demo-repos/payment-system'")
try:
    result = risk_scanner.scan_repository('demo-repos/payment-system')
    print(f"   [OK] SUCCESS: Found {result['total_risks']} risks in {result['total_files_scanned']} files")
    print(f"   Resolved to: {result['repository']}")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 2: Relative path with backslashes (Windows style)
print("\n2. Testing Windows-style path: 'demo-repos\\payment-system'")
try:
    result = risk_scanner.scan_repository('demo-repos\\payment-system')
    print(f"   [OK] SUCCESS: Found {result['total_risks']} risks in {result['total_files_scanned']} files")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 3: Absolute path
print("\n3. Testing absolute path")
abs_path = Path(__file__).resolve().parent.parent / 'demo-repos' / 'payment-system'
try:
    result = risk_scanner.scan_repository(str(abs_path))
    print(f"   [OK] SUCCESS: Found {result['total_risks']} risks in {result['total_files_scanned']} files")
except Exception as e:
    print(f"   [FAIL] FAILED: {e}")

# Test 4: Invalid path
print("\n4. Testing invalid path: 'nonexistent/repo'")
try:
    result = risk_scanner.scan_repository('nonexistent/repo')
    print(f"   [FAIL] UNEXPECTED: Should have failed but didn't")
except ValueError as e:
    print(f"   [OK] EXPECTED ERROR: {str(e)[:100]}...")

# Test 5: Empty path
print("\n5. Testing empty path")
try:
    result = risk_scanner.scan_repository('')
    print(f"   [FAIL] UNEXPECTED: Should have failed but didn't")
except ValueError as e:
    print(f"   [OK] EXPECTED ERROR: {str(e)[:100]}...")

print("\n" + "="*70)
print("PATH RESOLUTION TESTS COMPLETE")
print("="*70)

# Made with Bob
