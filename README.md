# Nexus-IntelliBob

**AI Incident Intelligence for Living Codebases**

Nexus learns from past production incidents, extracts their architectural failure patterns ("Incident DNA"), scans repositories for similar patterns, computes blast radius if those patterns fail, and generates a pre-mortem report BEFORE incidents occur.

## 🎯 Features

- **Incident DNA Extraction**: Automatically identifies failure patterns from historical incidents
- **Repository Scanning**: Scans codebases for patterns matching known incident DNA
- **Blast Radius Analysis**: Calculates the potential impact of identified risks
- **Pre-Mortem Reports**: Generates detailed failure scenarios before they happen
- **Real-time Dashboard**: Monitor risks, incidents, and repository health
- **Dark Enterprise UI**: Professional, accessible interface built with Next.js 14

## 🏗️ Architecture

### Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Python FastAPI, Pydantic v2
- **Database**: SQLite (sqlite3 stdlib)
- **Vector DB**: ChromaDB
- **Visualization**: D3.js (planned)
- **Font**: Geist Sans & Geist Mono

### Project Structure

```
Nexus-IntelliBob/
├── frontend/              # Next.js 14 frontend application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── types/            # TypeScript type definitions
│
├── backend/              # FastAPI backend application
│   ├── main.py          # FastAPI app entry point
│   ├── models.py        # Pydantic models
│   ├── db.py            # Database operations
│   ├── utils/           # Helper utilities
│   └── requirements.txt # Python dependencies
│
├── demo-repos/          # Demo repositories for testing
├── bob_sessions/        # Bob AI session data
├── start.sh            # Startup script
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Nexus-IntelliBob.git
   cd Nexus-IntelliBob
   ```

2. **Run the startup script** (Linux/macOS)
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   **Or manually start services:**

   **Backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage

### 1. Add Incidents

Navigate to the **Incidents** page and add historical incident data. The system will automatically extract failure patterns (Incident DNA).

### 2. Scan Repositories

Go to the **Scan** page and provide a repository path. Nexus will scan for patterns matching known incident DNA.

### 3. Analyze Blast Radius

View identified risks on the **Blast Radius** page to understand the potential impact if a risk becomes an incident.

### 4. Generate Pre-Mortem Reports

Create detailed **Pre-Mortem** reports that describe what could go wrong and how to prevent it.

## 🔌 API Endpoints

### Health Check
```
GET /health
```

### Dashboard Statistics
```
GET /api/dashboard-stats
```

### Incidents
```
GET  /api/incidents
POST /api/extract-dna
```

### Repository Operations
```
POST /api/ingest-repo
POST /api/scan-repo
```

### Analysis
```
POST /api/blast-radius
POST /api/premortem
```

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py
```

The backend runs on `http://localhost:8000` with auto-reload enabled.

### Frontend Development

```bash
cd frontend
npm run dev
```

The frontend runs on `http://localhost:3000` with hot module replacement.

### Type Checking

```bash
cd frontend
npm run build  # Runs TypeScript type checking
```

## 📦 Dependencies

### Backend
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.3
- ChromaDB 0.4.22

### Frontend
- Next.js 14.1.0
- React 18.2.0
- TypeScript 5.3.3
- Tailwind CSS 3.4.1
- Lucide React (icons)
- Geist (font)

## 🎨 UI/UX

The application features a dark enterprise-grade UI with:
- Responsive design for all screen sizes
- Accessible color contrast ratios
- Smooth animations and transitions
- Loading states and empty states
- Professional data visualization

## 🔒 Security

- No hardcoded credentials
- Environment variable support
- CORS configuration for API security
- Input validation with Pydantic
- SQL injection prevention

## 🧪 Testing

```bash
# Backend tests (to be implemented)
cd backend
pytest

# Frontend tests (to be implemented)
cd frontend
npm test
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Known Issues

- TypeScript errors will resolve after running `npm install` in the frontend directory
- Python dependencies require installation via `pip install -r requirements.txt`

## 📞 Support

For issues and questions, please open an issue on GitHub.

## 🗺️ Roadmap

- [ ] D3.js visualization for blast radius
- [ ] Real-time incident monitoring
- [ ] Integration with CI/CD pipelines
- [ ] Machine learning for pattern detection
- [ ] Multi-repository support
- [ ] Slack/Teams notifications
- [ ] Custom rule engine
- [ ] Historical trend analysis

---

**Built with ❤️ for preventing incidents before they happen**