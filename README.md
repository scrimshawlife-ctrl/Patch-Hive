<div align="center">
  <img src="docs/assets/header-banner.svg" alt="PatchHive Header" width="100%">
</div>

# PatchHive

**Eurorack System Design and Patch Exploration Platform**

<div align="center">
  <img src="docs/assets/logo-primary.svg" alt="PatchHive Logo" width="200">
</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-7FF7FF?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-7FF7FF?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-7FF7FF?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-7FF7FF?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-7FF7FF?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

[![ABX-Core](https://img.shields.io/badge/ABX--Core-v1.2-EBAF38?style=flat-square)](docs/ABX_CORE_COMPLIANCE.md)
[![Backend Tests](https://img.shields.io/badge/Backend_Tests-88_passing-00FF88?style=flat-square)](backend/tests/README.md)
[![Code Quality](https://img.shields.io/badge/Code_Quality-Automated-00FF88?style=flat-square)](.github/workflows/README.md)

[![License](https://img.shields.io/badge/License-MIT-2E7CEB?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-2E7CEB?style=flat-square)](https://github.com/scrimshawlife-ctrl/Patch-Hive/pulls)

</div>

<br>

<p align="center">
PatchHive is a modular web application that helps users design, catalog, share, and explore Eurorack modular synthesizer systems and their possible patches. Built following Applied Alchemy Labs (AAL) architecture principles with ABX-Core v1.2 compliance.
</p>

<div align="center">

**[🎛️ Live Demo](https://patchhive-frontend.onrender.com) • [📖 Documentation](docs/) • [🐛 Report Bug](../../issues) • [✨ Request Feature](../../issues)**

</div>

---

## 🔍 What PatchHive Is (and Is Not)

- **PatchHive is a deterministic patch data platform.** It outputs patch plans, wiring, and Patch Book exports.
- **Patch Book export is the primary paid feature.** Everything else supports clear, repeatable patch documentation.
- **PatchHive never generates audio.** No DSP, no audio preview, no synthesis rendering.
- **BeatOven integration is future and external.** Any audio workflows belong to BeatOven, not PatchHive.

---

## 📑 Table of Contents

- [✨ Key Highlights](#-key-highlights)
- [🎬 Demo](#-demo)
- [📸 Screenshots](#-screenshots)
- [🎯 Features](#-features)
- [🏗️ Technology Stack](#️-technology-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
- [☁️ Deployment](#️-deployment)
- [🧪 Development](#-development)
- [📚 Documentation](#-documentation)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Key Highlights

<table>
<tr>
<td width="50%">

### 🔧 **Modular Architecture**
Clean domain separation following ABX-Core v1.2 principles. Every component is composable and deterministic.

</td>
<td width="50%">

### 🎲 **Deterministic Generation**
Same rack + same seed = identical patches every time. Full reproducibility guaranteed.

</td>
</tr>
<tr>
<td width="50%">

### 🔗 **Signal Flow Engine**
Rule-based patch generation analyzing VCOs, VCFs, VCAs, and modulation sources.

</td>
<td width="50%">

### 📊 **Full Provenance**
SEED enforcement: every module, rack, and patch tracks its source and generation metadata.

</td>
</tr>
</table>

---

## 🎬 Demo

<div align="center">

**Explore the live build:** https://patchhive-frontend.onrender.com  
**API docs:** https://patchhive-api.onrender.com/docs

Preview below in [Screenshots](#-screenshots).

</div>

---

## 📸 Screenshots

<div align="center">

![PatchHive interface preview](docs/assets/social-preview.svg)

</div>

---

## 🎯 Features

### 📚 Module & Case Library

<details>
<summary><b>Click to expand</b></summary>

- **Comprehensive Catalog** - Eurorack modules with full metadata
- **Detailed Specifications**
  - HP width and physical dimensions
  - Power draw (+12V, -12V, +5V)
  - I/O ports and connectivity
  - Tags and categorization
  - Manufacturer details
- **Case Management**
  - Power supply constraints
  - Layout configurations
  - Row and HP capacity tracking
- **Multiple Import Methods**
  - Manual entry via UI
  - CSV bulk upload
  - ModularGrid integration (interface ready)
- **Full Data Provenance**
  - Source tracking (Manual, CSV, ModularGrid)
  - Import timestamps and references
  - SEED principle compliance
</details>

### 🎛️ Rack Builder

<details>
<summary><b>Click to expand</b></summary>

- **Interactive Design Interface**
  - Visual module placement
  - Drag-and-drop support
  - Real-time validation feedback
- **Smart Validation Engine**
  - HP capacity verification per row
  - Power draw limits enforcement
  - Overlap detection
  - Cable reach analysis
- **Automatic Features**
  - Deterministic naming (e.g., "Midnight Swarm", "Solar Lattice")
  - Layout optimization suggestions
  - Power consumption summaries
- **Save & Share**
  - Public/private rack configurations
  - Community sharing and discovery
  - Version history tracking

</details>
### ⚡ Deterministic Patch Generation

<details>
<summary><b>Click to expand</b></summary>

- **Rule-Based Engine**
  - Analyzes module capabilities and connections
  - Signal flow validation
  - Category-aware patch generation
- **Deterministic Behavior**
  - Same seed + rack configuration = identical patches
  - Full reproducibility guaranteed
  - Version-locked engine behavior
- **Patch Categories**
  - **Tonal**: Pads, Leads, Basses
  - **Rhythmic**: Percussion, Drums, Sequences
  - **Textural**: FX, Ambient, Generative
  - **Utility**: Processing, Mixing, Routing
- **Connection Graph**
  - Modules as nodes
  - Cables as directed edges
  - Signal type tracking (CV, Gate, Audio)
- **Full Provenance**
  - Generation seed stored with each patch
  - Engine version tracking
  - Configuration snapshots
  - Timestamp metadata

</details>

### 🎨 Visualization & Export

<details>
<summary><b>Click to expand</b></summary>

- **Rack Layout View**
  - Visual module arrangement
  - HP position indicators
  - Power consumption overlay
  - Cable routing visualization
- **Patch Diagrams**
  - Schematic-style connection views
  - Color-coded signal types
  - Port labeling
  - Flow direction indicators
- **Export Formats**
  - **Patch Book PDF (Paid)**: Branded patch books with diagrams, wiring, and patching order
  - **SVG**: Individual scalable vector graphics
  - **JSON**: Raw data for external tools
  - **CSV**: Module and patch lists

</details>

### 👥 Community Features

<details>
<summary><b>Click to expand</b></summary>

- **User Management**
  - Authentication and profiles
  - Portfolio of racks and patches
  - Activity history
- **Sharing & Discovery**
  - Public/private visibility controls
  - Community feed with latest creations
  - Search and filter by tags, modules, categories
- **Social Engagement**
  - Voting and favoriting system
  - Comments on racks and patches
  - User following and notifications
- **Collaboration**
  - Rack forking and remixing
  - Patch variation exploration
  - Community challenges and contests

</details>

---

## 🏗️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.104+ | Web framework |
| **PostgreSQL** | 15+ | Primary database |
| **SQLAlchemy** | 2.0+ | ORM and migrations |
| **Pydantic** | 2.0+ | Schema validation |
| **JWT** | Latest | Authentication |
| **ReportLab** | Latest | PDF generation |
| **Alembic** | Latest | Database migrations |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **TypeScript** | 5.2+ | Type-safe JavaScript |
| **React** | 18.2+ | UI framework |
| **Vite** | 5.0+ | Build tool |
| **React Router** | 6.0+ | Navigation |
| **Zustand** | 4.0+ | State management |
| **Axios** | Latest | HTTP client |

### Infrastructure

- **Docker & Docker Compose** - Containerization and orchestration
- **GitHub Actions** - CI/CD pipeline
- **Monorepo Structure** - Unified codebase management

---

## 📁 Project Structure

```
patchhive/
│
├── 🔧 backend/
│   ├── core/              # Configuration, database, security
│   ├── modules/           # Module catalog management
│   ├── cases/             # Case catalog management
│   ├── racks/             # Rack builder and validation
│   ├── patches/           # Patch generation engine
│   ├── community/         # Users, auth, social features
│   ├── export/            # PDF and SVG generation
│   ├── ingest/            # External data import
│   ├── alembic/           # Database migrations
│   ├── main.py            # FastAPI application entry
│   └── seed_data.py       # Development seed data
│
├── 🎨 frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── lib/           # API client, utilities
│   │   ├── types/         # TypeScript definitions
│   │   └── main.tsx       # React application entry
│   ├── index.html
│   └── vite.config.ts
│
├── 🐳 infra/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
└── 📖 docs/
    ├── ARCHITECTURE.md           # System architecture
    ├── PATCH_ENGINE.md           # Patch generation details
    ├── DATA_MODEL.md             # Database schema
    ├── ABX_CORE_COMPLIANCE.md    # Architecture compliance
    ├── DEPLOYMENT_OPTIONS.md     # Deployment guides
    └── ...
```

---

## 🚀 Quick Start

### Prerequisites

Choose one of the following:

**Option A (Recommended):**
- Docker Desktop or Docker Engine + Docker Compose

**Option B (Manual):**
- Python 3.11 or higher
- Node.js 20 or higher
- PostgreSQL 15 or higher

---

### ⚡ Option A: Docker Setup (Recommended)

The fastest way to get PatchHive running:

```bash
# 1. Clone the repository
git clone https://github.com/scrimshawlife-ctrl/Patch-Hive.git
cd Patch-Hive

# 2. Start all services
docker compose up -d

# Alternative: Use the Makefile
make dev
```

**Access the application:**

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React UI |
| Backend API | http://localhost:8000/docs | Interactive API docs |
| Database | localhost:5432 | PostgreSQL |

**Useful commands:**

```bash
make help          # Show all available commands
make logs          # Follow service logs
make test          # Run all tests
make db-backup     # Backup database
make restart       # Restart all services
make clean         # Stop and remove containers
```

📖 **[Complete Docker Guide →](docs/DOCKER_DEPLOYMENT.md)**

---

### 🛠️ Option B: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -e .

# Configure database connection
export DATABASE_URL="postgresql://patchhive:patchhive@localhost:5432/patchhive"

# Run database migrations
alembic upgrade head

# (Optional) Load seed data for development
python seed_data.py

# Start the development server
uvicorn main:app --reload
```

Backend will be available at: **http://localhost:8000/docs**

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## ☁️ Deployment

PatchHive supports deployment to **7+ platforms**. Choose based on your needs.

> **Status:** Azure and Render deployments are currently **paused** pending canon-aligned rollout.

### 🎯 Quick Deploy Options

<table>
<tr>
<td width="50%">

#### Azure (Production-Ready — Paused)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fscrimshawlife-ctrl%2FPatch-Hive%2Fmain%2Finfra%2Fmain.bicep)

**Quick Deploy:**
```bash
azd up
```

**Includes:**
- PostgreSQL Flexible Server (15)
- App Service (Python 3.11)
- Static Web Apps (Frontend)
- Auto SSL certificates
- Application Insights

**Cost:** ~$25-30/month (production)

📖 [Azure Guide](docs/AZURE_DEPLOYMENT.md)

</td>
<td width="50%">

#### Render (Free Tier — Paused)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/scrimshawlife-ctrl/Patch-Hive)

**One-Click Deploy:**
1. Click the button above
2. Connect GitHub repository
3. Services deploy automatically
4. Live in ~10 minutes

**Includes:**
- PostgreSQL database (free tier)
- FastAPI backend (free tier)
- React frontend (free tier)

**Cost:** Free (with limitations)

📖 [Render Guide](docs/RENDER_DEPLOYMENT.md)

</td>
</tr>
</table>

### 📊 Platform Comparison

| Platform | Free Tier | Production Cost | Auto-scaling | Custom Domains | Best For |
|----------|-----------|-----------------|--------------|----------------|----------|
| **Azure** | $200 credit | ~$25-30/mo | ✅ Yes | ✅ Free SSL | Production, Enterprise |
| **Render** | ✅ Forever | ~$25/mo | Limited | ✅ Free SSL | Prototypes, Free hosting |
| **Railway** | $5 credit | $5-50/mo | ✅ Yes | ✅ Free SSL | MVPs, Startups |
| **DigitalOcean** | $200 credit | $12-50/mo | ✅ Yes | ✅ Free SSL | Simple production |
| **Fly.io** | Free tier | $0-30/mo | ✅ Yes | ✅ Free SSL | Edge deployment |
| **Vercel** | ✅ Generous | Free-$20/mo | ✅ Yes | ✅ Free SSL | Frontend only |

### 🐳 Self-Hosted with Docker

Perfect for on-premise or custom VPS:

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d

# Or use the deployment script
make prod
```

📖 **[Full Deployment Comparison & Guides →](docs/DEPLOYMENT_OPTIONS.md)**

---

## 🧪 Development

### Running Tests

**Backend tests:**
```bash
cd backend
pytest                     # Run all tests
pytest -v                  # Verbose output
pytest tests/test_racks/   # Specific test directory
pytest -k "test_name"      # Specific test pattern
```

**Frontend linting:**
```bash
cd frontend
npm run lint              # Check for issues
npm run lint:fix          # Auto-fix issues
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Code Quality Tools

```bash
# Backend
cd backend
black .                   # Format code
ruff check .              # Lint code
mypy .                    # Type checking

# Frontend
cd frontend
npm run format            # Format with Prettier
npm run type-check        # TypeScript validation
```

---

## 🔒 ABX-Core v1.2 Compliance

PatchHive adheres to Applied Alchemy Labs architecture principles:

| Principle | Implementation |
|-----------|----------------|
| **Modularity** | Clean domain separation (modules, cases, racks, patches, community) |
| **Determinism** | Patch generation is fully deterministic from seed |
| **Entropy Minimization** | No random behavior without explicit seeding |
| **Mental Model** | Everything modeled as modules, cases, patches, and signals |
| **SEED Enforcement** | Full provenance tracking of all data sources and transformations |

**Provenance Tracking includes:**
- Data source identification (Manual, CSV, ModularGrid)
- Import timestamps and references
- Generation seeds and engine versions
- Configuration snapshots and metadata
- Transformation history

📖 **[Detailed Compliance Documentation →](docs/ABX_CORE_COMPLIANCE.md)**

---

## 📚 Documentation

### Core Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and component interactions
- **[Patch Engine Deep Dive](docs/PATCH_ENGINE.md)** - Patch generation algorithm details
- **[Data Model](docs/DATA_MODEL.md)** - Database schema and relationships
- **[ABX-Core Compliance](docs/ABX_CORE_COMPLIANCE.md)** - Architecture principles adherence

### Deployment Guides

- **[Deployment Options Comparison](docs/DEPLOYMENT_OPTIONS.md)** - Platform comparison and recommendations
- **[Azure Deployment](docs/AZURE_DEPLOYMENT.md)** - Production deployment to Azure
- **[Render Deployment](docs/RENDER_DEPLOYMENT.md)** - Free tier deployment to Render
- **[Docker Deployment](docs/DOCKER_DEPLOYMENT.md)** - Self-hosted Docker setup

### API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

**Key API Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `/api/modules` | Module catalog CRUD operations |
| `/api/cases` | Case catalog management |
| `/api/racks` | Rack builder with validation |
| `/api/patches` | Patch storage and retrieval |
| `/api/patches/generate/{rack_id}` | Generate patches for a rack |
| `/api/community` | Users, auth, voting, comments |
| `/api/export` | PDF and SVG export services |

---

## 🗺️ Roadmap (Canon v0.5)

### ✅ Phase 0 — Complete (Architecture)

- ABX-Core compliant architecture
- Deterministic patch engine foundations
- System pack ingestion + Patch Book scaffolding

### 🚧 Phase 1 — Active (Paid Beta)

- Patch Book export as primary paid feature
- VL2 system pack reference library
- Deterministic rack recommendations

### 🔮 Phase 2 — Future (UX)

- UX refinement for patch exploration
- Library navigation improvements
- Template-driven patch browsing

### 🌌 Phase 3 — Future (Ecosystem)

- External integrations (BeatOven and partners)
- Community distribution workflows
- Expanded system packs

---

## 📎 Canon Traceability

Canon decisions live in Notion. This repo aligns with **Canon v0.5**.

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following our code style
4. **Write or update tests** for your changes
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to your branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Guidelines

- Follow existing code style and conventions
- Adhere to ABX-Core v1.2 principles
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and well-described
- Be respectful and constructive in discussions

### Development Standards

- **Backend**: Follow PEP 8, use type hints, maintain test coverage
- **Frontend**: Follow ESLint rules, use TypeScript, document components
- **Documentation**: Update relevant docs with feature changes
- **Testing**: Maintain or improve test coverage

📖 **[More details in CONTRIBUTING.md](CONTRIBUTING.md)** *(coming soon)*

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Applied Alchemy Labs** for ABX-Core architecture principles
- **ModularGrid** for module database inspiration
- **Eurorack community** for endless creativity and inspiration

---

<div align="center">

**Built with ABX-Core v1.2 | SEED-Enforced | Deterministic | Modular**

---

**[⬆ Back to Top](#patchhive)**

</div>
