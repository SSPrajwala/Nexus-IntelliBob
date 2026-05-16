"""Quick test of the risk scanner"""
import risk_scanner

# Test the scanner
result = risk_scanner.scan_repository('../demo-repos/payment-system')

print(f"\n{'='*60}")
print(f"SCAN RESULTS")
print(f"{'='*60}")
print(f"Repository: {result['repository']}")
print(f"Files Scanned: {result['total_files_scanned']}")
print(f"Total Risks: {result['total_risks']}")
print(f"  - Critical: {result['critical_risks']}")
print(f"  - High: {result['high_risks']}")
print(f"  - Medium: {result['medium_risks']}")
print(f"  - Low: {result['low_risks']}")
print(f"{'='*60}\n")

# Show first 3 risks
if result['matches']:
    print("Sample Risks Found:")
    for i, risk in enumerate(result['matches'][:3], 1):
        print(f"\n{i}. [{risk['severity'].upper()}] {risk['risk_type']}")
        print(f"   File: {risk['file_path']}:{risk['line_number']}")
        print(f"   Confidence: {risk['confidence']*100:.0f}%")
        print(f"   Pattern: {risk['related_incident_pattern']}")

# Made with Bob
