# PatchHive

**Eurorack System Design and Patch Exploration Platform**

PatchHive is a modular web application that helps users design, catalog, share, and explore Eurorack modular synthesizer systems and their possible patches. Built following Applied Alchemy Labs (AAL) architecture principles with ABX-Core v1.2 compliance.

---

## Features

### 1. Module & Case Library
- Comprehensive catalog of Eurorack modules with full metadata
- Module specifications: HP width, power draw, I/O ports, tags, descriptions
- Case library with power and layout constraints
- Import from multiple sources:
  - Manual entry via UI
  - CSV upload
  - ModularGrid integration (interface ready, implementation pending)
- Full data provenance tracking (SEED principle)

### 2. Rack Builder
- Interactive rack design with case selection
- Module placement with validation:
  - HP capacity per row
  - Power draw limits (+12V, -12V, +5V)
  - Overlap detection
- Automatic deterministic naming (e.g., "Midnight Swarm", "Solar Lattice")
- Save and share configurations

### 3. Deterministic Patch Generation Engine
- Rule-based patch generation from rack configurations
- Deterministic: same seed + rack = same patches
- Patch categories:
  - Pads, Leads, Basses, Percussion
  - FX/Textures, Generative, Utility/Processing
- Connection graph representation (modules as nodes, cables as edges)
- Full provenance: seed, engine version, config stored with each patch

### 4. Visualization & Export
- **Rack Layout View**: Visual module arrangement with HP positions
- **Patch Diagram**: Schematic showing cable connections between modules
- **Waveform Approximation**: Simplified synthesis model for audio visualization
- **PDF Export**: Generate patch books with diagrams and descriptions
- **SVG Export**: Individual diagrams for rack layouts, patches, and waveforms

### 5. Community Layer
- User authentication and profiles
- Public/private rack and patch sharing
- Community feed with latest creations
- Voting/favoriting system
- Comments on racks and patches

---

## Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL** (SQLite compatible for development)
- **SQLAlchemy** for ORM with Alembic migrations
- **Pydantic** for schema validation
- **JWT** authentication
- **ReportLab** for PDF generation
- **SVG** generation for visualizations

### Frontend
- **TypeScript + React** with Vite
- **React Router** for navigation
- **Zustand** for state management
- **Axios** for API communication

### Infrastructure
- **Docker** with docker-compose
- Monorepo structure for backend, frontend, and shared types

---

## Project Structure

```
patchhive/
├── backend/
│   ├── core/           # Config, database, security, naming
│   ├── modules/        # Module catalog management
│   ├── cases/          # Case catalog management
│   ├── racks/          # Rack builder and validation
│   ├── patches/        # Patch engine, storage, routes
│   ├── community/      # Users, auth, voting, comments
│   ├── export/         # PDF, SVG generation
│   ├── ingest/         # External data import (ModularGrid, CSV)
│   ├── alembic/        # Database migrations
│   ├── main.py         # FastAPI app entry point
│   └── seed_data.py    # Development seed data loader
├── frontend/
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Page components
│   │   ├── lib/        # API client, state management
│   │   ├── types/      # TypeScript type definitions
│   │   └── main.tsx    # React app entry point
│   ├── index.html
│   └── vite.config.ts
├── infra/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
└── docs/
    ├── ARCHITECTURE.md
    ├── PATCH_ENGINE.md
    ├── DATA_MODEL.md
    └── ABX_CORE_COMPLIANCE.md
```

---

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OR: Python 3.11+, Node.js 20+, PostgreSQL 15+

### Using Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd Patch-Hive

# Start all services
cd infra
docker-compose up

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
# API docs at http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Install dependencies
pip install -e .

# Set up database (PostgreSQL)
export DATABASE_URL="postgresql://patchhive:patchhive@localhost:5432/patchhive"

# Run migrations
alembic upgrade head

# Load seed data (optional)
python seed_data.py

# Start server
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## ABX-Core v1.2 Compliance

PatchHive adheres to Applied Alchemy Labs architecture principles:

- **Modularity**: Clean domain separation (modules, cases, racks, patches, community)
- **Determinism**: Patch generation is fully deterministic from seed
- **Entropy Minimization**: No random behavior without explicit seeding
- **Eurorack Mental Model**: Everything modeled as modules, cases, patches, signals
- **SEED Enforcement**: Full provenance tracking:
  - Data source (Manual, CSV, ModularGrid, etc.)
  - Import timestamps and references
  - Generation seeds and engine versions
  - Configuration metadata

See [ABX_CORE_COMPLIANCE.md](docs/ABX_CORE_COMPLIANCE.md) for detailed compliance documentation.

---

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

Key endpoints:
- `/api/modules` - Module catalog CRUD
- `/api/cases` - Case catalog CRUD
- `/api/racks` - Rack builder with validation
- `/api/patches` - Patch storage and generation
- `/api/patches/generate/{rack_id}` - Generate patches for a rack
- `/api/community` - Users, auth, voting, comments, feed
- `/api/export` - PDF and SVG export

---

## Development

### Backend Testing

```bash
cd backend
pytest
```

### Frontend Linting

```bash
cd frontend
npm run lint
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Roadmap

### Phase 1 (Current)
- ✅ Module & Case library management
- ✅ Rack builder with validation
- ✅ Deterministic patch generation engine
- ✅ Waveform approximation visualization
- ✅ PDF export
- ✅ Community features (auth, voting, feed)

### Phase 2 (Future)
- ModularGrid import implementation
- Enhanced rack builder UI with drag-and-drop
- Real-time collaborative rack editing
- Advanced patch filtering and search
- Rack templates and presets
- Audio preview generation (actual DSP)

### Phase 3 (Future)
- Mobile app (React Native)
- AI-assisted patch generation
- Integration with hardware modular systems
- Marketplace for custom patches
- Educational content and tutorials

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow existing code style and ABX-Core principles
4. Add tests for new features
5. Submit a pull request

---

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Patch Engine Deep Dive](docs/PATCH_ENGINE.md)
- [Data Model](docs/DATA_MODEL.md)
- [ABX-Core Compliance](docs/ABX_CORE_COMPLIANCE.md)

---

**Built with ABX-Core v1.2 | SEED-Enforced | Deterministic | Modular**
