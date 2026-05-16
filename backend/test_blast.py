"""Test script for blast radius analyzer"""
from blast_analyzer import analyze_blast_radius

# Test with demo repository
result = analyze_blast_radius('../demo-repos/payment-system', 'auth-service')

print('Blast Radius Analysis Results:')
print('=' * 50)
print(f'Root Failure Service: {result["root_failure_service"]}')
print(f'Affected Services: {result["affected_services"]}')
print(f'Criticality Score: {result["criticality_score"]}/100')
print(f'Failure Type: {result["failure_type"]}')
print(f'Revenue Risk: {result["estimated_revenue_risk"]}')
print(f'Customer Impact: {result["estimated_customer_impact"]}')
print(f'\nPropagation Chain ({len(result["propagation_chain"])} events):')
for event in result["propagation_chain"]:
    print(f'  T+{event["time_offset"]}s: {event["service"]} - {event["impact_type"]}')
print(f'\nGraph: {len(result["graph"]["nodes"])} nodes, {len(result["graph"]["edges"])} edges')
print('\nTest completed successfully!')

# Made with Bob
