"""
Test Pre-Mortem Intelligence System Integration
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

import risk_scanner
import blast_analyzer
import premortem_generator


def test_premortem_integration():
    """Test complete pre-mortem generation flow"""
    print("=" * 60)
    print("Testing Pre-Mortem Intelligence System")
    print("=" * 60)
    
    # Test parameters - use absolute path
    repo_path = os.path.abspath("../demo-repos/payment-system")
    failed_service = "auth-service"
    
    print(f"\n1. Testing with repository: {repo_path}")
    print(f"   Failed service: {failed_service}")
    
    # Step 1: Scan repository
    print("\n2. Scanning repository for risks...")
    try:
        scan_results = risk_scanner.scan_repository(repo_path)
        print(f"   [OK] Scan completed")
        print(f"   - Files scanned: {scan_results['total_files_scanned']}")
        print(f"   - Total risks: {scan_results['total_risks']}")
        print(f"   - Critical: {scan_results['critical_risks']}")
        print(f"   - High: {scan_results['high_risks']}")
    except Exception as e:
        print(f"   [FAIL] Scan failed: {e}")
        return False
    
    # Step 2: Compute blast radius
    print("\n3. Computing blast radius...")
    try:
        blast_results = blast_analyzer.analyze_blast_radius(repo_path, failed_service)
        print(f"   [OK] Blast radius computed")
        print(f"   - Root service: {blast_results['root_failure_service']}")
        print(f"   - Affected services: {len(blast_results['affected_services'])}")
        print(f"   - Criticality score: {blast_results['criticality_score']}")
    except Exception as e:
        print(f"   [FAIL] Blast analysis failed: {e}")
        return False
    
    # Step 3: Generate pre-mortem
    print("\n4. Generating pre-mortem report...")
    try:
        dna_matches = []
        if scan_results.get('matches'):
            for match in scan_results['matches'][:3]:
                if match.get('related_incident_pattern'):
                    dna_matches.append({
                        'pattern': match['related_incident_pattern'],
                        'confidence': match.get('confidence', 0.7),
                        'description': match.get('explanation', '')
                    })
        
        report = premortem_generator.generate_premortem(
            scan_results,
            blast_results,
            dna_matches
        )
        
        print(f"   [OK] Pre-mortem generated")
        print(f"   - Report ID: {report['report_id']}")
        print(f"   - Risk Level: {report['risk_level']}")
        print(f"   - Confidence: {report['confidence_score']}")
        print(f"   - Time to incident: {report['estimated_time_to_incident']}")
        
        # Display key sections
        print(f"\n5. Report Summary:")
        print(f"   Title: {report['incident_title']}")
        print(f"   Revenue at Risk: {report['estimated_revenue_loss']}")
        print(f"   Services Affected: {len(report['affected_services'])}")
        print(f"   Mitigation Steps: {len(report['mitigation_steps'])}")
        
    except Exception as e:
        print(f"   [FAIL] Pre-mortem generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All integration tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_premortem_integration()
    sys.exit(0 if success else 1)

# Made with Bob