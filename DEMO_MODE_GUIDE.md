# 🎬 Nexus Cinematic Demo Mode

## Overview

The Cinematic Demo Mode is a fully automated, judge-friendly demonstration of the complete Nexus intelligence platform. It showcases all major capabilities in a visually stunning, movie-trailer-style presentation.

## Accessing Demo Mode

### Option 1: Direct URL
Navigate to: `http://localhost:3000/demo`

### Option 2: Sidebar Navigation
Click the **"🎬 Cinematic Demo"** button in the sidebar (highlighted with orange gradient)

## Demo Flow

The demo automatically progresses through 11 cinematic stages:

### 1. **Intro Screen** (3s)
- Nexus branding with animated logo
- "Start Cinematic Demo" button

### 2. **Loading** (2s)
- Animated loading spinner
- System initialization

### 3. **Repository Ingestion** (4s)
- Clones FastAPI repository from GitHub
- Shows progress bar and file scanning
- Displays: `https://github.com/tiangolo/fastapi`

### 4. **Architecture Intelligence** (6s)
- Full repository metadata display
- Service topology visualization
- Language distribution charts
- Framework detection
- Complexity scoring

### 5. **Risk Scanning** (5s)
- Animated scanning progress
- Pattern detection visualization
- Shows scanning for:
  - Retry patterns
  - Circuit breakers
  - Database connections
  - Error handling

### 6. **Risk Correlation Results** (7s)
- Displays top 6 identified risks
- Each risk card shows:
  - Severity level
  - Confidence score
  - Code snippets
  - Blast radius score
  - Recommendations

### 7. **Blast Radius Simulation** (8s)
- Interactive D3.js force-directed graph
- Shows cascading failure propagation
- Displays:
  - Services at risk count
  - Criticality score
  - Customer impact estimation

### 8. **Pre-Mortem Intelligence** (10s)
- Comprehensive failure prediction report
- Executive summary
- Timeline of predicted events
- Business impact analysis
- Mitigation recommendations

### 9. **Engineering Timeline** (8s)
- AI-reconstructed evolution of engineering decisions
- Shows how risks accumulated over time
- Confidence scores for each event
- Affected services per decision

### 10. **Executive Intelligence** (10s)
- Strategic insights for leadership
- Reliability maturity score
- Risk posture assessment
- Hidden risk analysis
- Key metrics dashboard

### 11. **Finale Screen** (Manual)
- "Incident Prevented" celebration
- Shows impact metrics:
  - **$2.5M** Revenue Protected
  - **12** Services Secured
  - **4.5hrs** Outage Avoided
  - **99.99%** Reliability Target
- "Replay Demo" button

## Features

### Cinematic Effects
- ✨ Smooth fade-in/fade-out transitions
- 🎨 Gradient backgrounds and glowing borders
- 📊 Animated progress bars and counters
- 🌊 Shimmer effects on loading states
- 💫 Pulsing animations on critical elements
- 🎭 Dramatic typography with text shadows

### User Controls
- **Pause Button**: Pause the demo at any stage
- **Restart Button**: Reset and replay from beginning
- **Progress Bar**: Visual indicator of demo progress

### Technical Highlights
- **Zero User Interaction Required**: Fully automated flow
- **Deterministic**: Same demo every time
- **Offline Capable**: Works without external dependencies
- **TypeScript Strict**: Full type safety
- **Responsive**: Adapts to different screen sizes

## Demo Repository

The demo uses the FastAPI repository as a real-world example:
- **URL**: https://github.com/tiangolo/fastapi
- **Why FastAPI**: Popular, well-structured, production-grade Python framework
- **Service**: `main` (primary application entry point)

## Customization

To use a different repository, modify `DemoModePlayer.tsx`:

```typescript
const DEMO_REPO_URL = "https://github.com/your-org/your-repo";
const DEMO_SERVICE = "your-service-name";
```

## Architecture

### Components Used
- `DemoModePlayer.tsx` - Main orchestration component
- `RepositoryIntelligenceOverview.tsx` - Architecture display
- `RiskMatchCard.tsx` - Risk visualization
- `BlastGraph.tsx` - D3.js graph visualization
- `PreMortemReport.tsx` - Pre-mortem display
- `EngineeringTimeline.tsx` - Timeline visualization
- `ExecutiveIntelCard.tsx` - Executive summary

### API Endpoints Used
- `POST /api/analyze-github-repo` - Complete repository analysis
- `POST /api/engineering-timeline` - Timeline generation

### State Management
- React hooks for stage progression
- Automatic timeout-based transitions
- Error handling with fallback states

## Performance

- **Total Demo Duration**: ~70 seconds (automated stages)
- **API Call**: Single comprehensive analysis
- **Memory Efficient**: Lazy loads components
- **Build Size**: Minimal impact (~50KB gzipped)

## Troubleshooting

### Demo Won't Start
- Ensure backend is running on `http://localhost:8000`
- Check browser console for errors
- Verify FastAPI repository is accessible

### Slow Loading
- Check network connection
- Backend may be processing large repository
- First run takes longer (repository cloning)

### Visual Glitches
- Clear browser cache
- Ensure modern browser (Chrome/Firefox/Edge)
- Check for CSS conflicts

## Best Practices for Judges

1. **Full Screen**: Press F11 for immersive experience
2. **Sound Off**: Demo is visual-only (no audio required)
3. **Let It Play**: Don't interrupt the flow
4. **Replay**: Watch multiple times to catch details
5. **Compare**: Run on different repositories to see adaptability

## Technical Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Custom animations
- **Visualization**: D3.js, Framer Motion
- **API**: FastAPI backend
- **State**: React Hooks

## Future Enhancements

Potential additions (not implemented):
- [ ] Sound effects and background music
- [ ] Voiceover narration
- [ ] Multiple demo scenarios
- [ ] Interactive pause/explore mode
- [ ] Export demo as video
- [ ] Custom repository input

## Credits

Built with ❤️ by the Nexus-IntelliBob team for IBM Hackathon 2026.

**Made with Bob** 🤖

---

For technical support or questions, refer to the main README.md