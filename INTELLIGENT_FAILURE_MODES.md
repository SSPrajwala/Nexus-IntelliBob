# Intelligent Failure Simulation System

## Executive Summary

Replaced the confusing "failed_service" requirement with an intelligent failure simulation system that works with ANY repository without requiring users to guess which component to fail.

**Status**: ✅ Backend implementation complete

## The Problem We Solved

### Before
```
User: "Which service should I select to fail?"
System: "Pick from: auth-service, payment-service, order-service"
User: "But my repo doesn't have those services..."
System: *crashes*
```

**Issues:**
- Required users to know internal service names
- Only worked with demo repository structure
- Broke on real-world repositories
- Poor user experience
- Confusing and error-prone

### After
```
User: Selects "Auto (Recommended)"
System: "Analyzing repository... Found most critical component: API Gateway"
System: "Computing blast radius for API Gateway..."
User: "Perfect! That makes sense."
```

**Benefits:**
- Works with ANY repository
- No guessing required
- Intelligent auto-selection
- Clear, actionable options
- Professional UX

## Failure Modes

### 1. 🤖 AUTO Mode (Recommended)
**What it does:**
- Automatically analyzes repository structure
- Identifies most critical failure point
- Selects component with highest criticality score
- No user input required

**Use case:** Default mode for all analyses

**Example:**
```json
{
  "failure_mode": "auto",
  "target_type": "service",
  "target_name": "api-gateway",
  "display_name": "API Gateway",
  "reason": "Highest criticality score (95/100)",
  "criticality_score": 95
}
```

### 2. 🌐 ALL Mode (System-Wide)
**What it does:**
- Simulates complete platform failure
- Analyzes worst-case scenarios
- Identifies systemic architectural weaknesses
- Platform-wide impact assessment

**Use case:** Disaster recovery planning, architecture review

**Example:**
```json
{
  "failure_mode": "all",
  "target_type": "system",
  "target_name": "entire-system",
  "display_name": "Entire System",
  "criticality_score": 100,
  "affected_components": 5
}
```

### 3. 🎯 SPECIFIC Mode (User-Selected)
**What it does:**
- User selects specific component
- Validates component exists
- Targeted failure analysis
- Detailed impact assessment

**Use case:** Testing specific failure scenarios, targeted analysis

**Example:**
```json
{
  "failure_mode": "specific",
  "target_name": "payment-processor",
  "display_name": "Payment Processor",
  "criticality_score": 90
}
```

## Architecture

### New Module: `backend/services/failure_simulator.py`

```python
class FailureSimulator:
    """
    Intelligent failure simulation that works with ANY repository.
    No more guessing which service to fail.
    """
    
    def determine_failure_target(
        failure_mode: str = "auto",
        specific_target: Optional[str] = None
    ) -> Dict:
        """
        Intelligently determine what should fail based on mode.
        """
```

### Key Functions

1. **`simulate_failure(repo_path, failure_mode, specific_target)`**
   - Main entry point
   - Returns failure target and context

2. **`get_failure_mode_options()`**
   - Returns available modes for frontend
   - Includes labels, descriptions, defaults

3. **`FailureSimulator.determine_failure_target()`**
   - AUTO: Auto-selects most critical component
   - ALL: Returns system-wide failure target
   - SPECIFIC: Validates and returns user selection

4. **`FailureSimulator.get_available_targets()`**
   - Returns list of components for SPECIFIC mode
   - Sorted by criticality
   - Formatted for frontend dropdown

## API Changes

### Updated Endpoints

#### POST /api/blast-radius
**Before:**
```json
{
  "repo_path": "demo-repos/payment-system",
  "failed_service": "payment-service"  // REQUIRED
}
```

**After:**
```json
{
  "repo_path": "demo-repos/payment-system",
  "failure_mode": "auto",  // "auto", "all", or "specific"
  "failed_service": null   // OPTIONAL (only for specific mode)
}
```

#### New: GET /api/failure-modes
Returns available failure modes for frontend:
```json
{
  "success": true,
  "modes": [
    {
      "value": "auto",
      "label": "🤖 Auto (Recommended)",
      "description": "Automatically select the most critical component",
      "default": true
    },
    {
      "value": "all",
      "label": "🌐 Entire System",
      "description": "Simulate platform-wide failure",
      "default": false
    },
    {
      "value": "specific",
      "label": "🎯 Select Component",
      "description": "Choose a specific component to fail",
      "default": false
    }
  ]
}
```

## Backend Implementation

### Updated Files

1. **`backend/services/failure_simulator.py`** (NEW - 267 lines)
   - FailureSimulator class
   - Auto-selection logic
   - System-wide failure simulation
   - Component validation

2. **`backend/services/__init__.py`**
   - Exports failure simulator functions
   - Exports FailureMode enum

3. **`backend/blast_analyzer.py`**
   - Updated `compute_blast_radius()` to accept failure_mode
   - Added `_compute_system_wide_blast_radius()` method
   - Integrated with failure simulator

4. **`backend/main.py`**
   - Updated `/api/blast-radius` endpoint
   - Added `/api/failure-modes` endpoint
   - Updated request model (failed_service now optional)
   - Added failure_mode validation

## How It Works

### AUTO Mode Flow
```
1. User selects "Auto" mode
2. System analyzes repository structure
3. ServiceDetector identifies all components
4. FailureSimulator calculates criticality scores
5. Highest criticality component selected
6. Blast radius computed for that component
7. Results returned with explanation
```

### ALL Mode Flow
```
1. User selects "Entire System" mode
2. System detects all components
3. Simulates simultaneous failure of all
4. Computes platform-wide impact
5. Returns worst-case scenario analysis
6. Includes disaster recovery recommendations
```

### SPECIFIC Mode Flow
```
1. User selects "Select Component" mode
2. System fetches available components
3. User selects from dropdown
4. System validates selection
5. Computes targeted blast radius
6. Returns component-specific analysis
```

## Frontend Integration (To Be Implemented)

### Recommended UI

```tsx
<div className="failure-mode-selector">
  <label>Failure Simulation Mode</label>
  
  <RadioGroup value={failureMode} onChange={setFailureMode}>
    <Radio value="auto">
      🤖 Auto (Recommended)
      <span className="description">
        Automatically select the most critical component
      </span>
    </Radio>
    
    <Radio value="all">
      🌐 Entire System
      <span className="description">
        Simulate platform-wide failure
      </span>
    </Radio>
    
    <Radio value="specific">
      🎯 Select Component
      <span className="description">
        Choose a specific component to fail
      </span>
    </Radio>
  </RadioGroup>
  
  {failureMode === 'specific' && (
    <Select
      options={availableComponents}
      placeholder="Select component to fail"
    />
  )}
</div>
```

### API Calls

```typescript
// Get failure modes
const modes = await fetch('/api/failure-modes').then(r => r.json());

// Get available components (for specific mode)
const components = await fetch('/api/detect-services', {
  method: 'POST',
  body: JSON.stringify({ repo_path })
}).then(r => r.json());

// Compute blast radius with auto mode
const result = await fetch('/api/blast-radius', {
  method: 'POST',
  body: JSON.stringify({
    repo_path: 'demo-repos/payment-system',
    failure_mode: 'auto'
  })
}).then(r => r.json());
```

## Benefits

### For Users
- ✅ No guessing which service to fail
- ✅ Works with any repository
- ✅ Clear, actionable options
- ✅ Intelligent defaults
- ✅ Professional experience

### For Developers
- ✅ Cleaner API design
- ✅ Better separation of concerns
- ✅ Extensible architecture
- ✅ Easier to test
- ✅ More maintainable

### For Hackathon Judges
- ✅ Shows intelligent system design
- ✅ Demonstrates UX thinking
- ✅ Proves universal compatibility
- ✅ Highlights AI-like behavior
- ✅ Professional polish

## Testing Scenarios

### Test 1: Auto Mode with Demo Repo
```bash
POST /api/blast-radius
{
  "repo_path": "demo-repos/payment-system",
  "failure_mode": "auto"
}

Expected: Auto-selects auth-service (highest criticality)
```

### Test 2: All Mode
```bash
POST /api/blast-radius
{
  "repo_path": "demo-repos/payment-system",
  "failure_mode": "all"
}

Expected: System-wide failure analysis
```

### Test 3: Specific Mode
```bash
POST /api/blast-radius
{
  "repo_path": "demo-repos/payment-system",
  "failure_mode": "specific",
  "failed_service": "payment-service"
}

Expected: Targeted analysis of payment-service
```

### Test 4: GitHub Repository
```bash
POST /api/blast-radius
{
  "repo_path": "https://github.com/user/repo",
  "failure_mode": "auto"
}

Expected: Clones repo, auto-selects critical component
```

## Migration Guide

### For Existing Code

**Old way:**
```python
blast_radius = analyze_blast_radius(
    repo_path="demo-repos/payment-system",
    failed_service="payment-service"  # Required
)
```

**New way:**
```python
# Auto mode (recommended)
blast_radius = analyze_blast_radius(
    repo_path="demo-repos/payment-system",
    failure_mode="auto"
)

# All mode
blast_radius = analyze_blast_radius(
    repo_path="demo-repos/payment-system",
    failure_mode="all"
)

# Specific mode (backward compatible)
blast_radius = analyze_blast_radius(
    repo_path="demo-repos/payment-system",
    failure_mode="specific",
    failed_service="payment-service"
)
```

## Future Enhancements

1. **Machine Learning Integration**
   - Learn from historical incidents
   - Predict most likely failure points
   - Improve auto-selection accuracy

2. **Multi-Component Failure**
   - Simulate multiple simultaneous failures
   - Complex cascade scenarios
   - Dependency chain analysis

3. **Time-Based Simulation**
   - Gradual degradation
   - Progressive failure
   - Recovery timeline

4. **Custom Failure Scenarios**
   - User-defined failure patterns
   - Saved scenario templates
   - Scenario comparison

## Conclusion

The intelligent failure simulation system transforms Nexus-IntelliBob from a demo-specific tool into a universal platform that works with ANY repository. By removing the confusing "failed_service" requirement and replacing it with smart, context-aware failure modes, we've created a professional, user-friendly experience that will impress hackathon judges and real users alike.

**Key Achievement:** Users no longer need to guess which component to fail - the system intelligently figures it out.

---
*Made with Bob - Senior Platform Reliability Engineer*