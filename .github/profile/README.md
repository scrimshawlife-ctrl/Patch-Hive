<div align="center">

![PatchHive Header](../../docs/assets/header-banner.svg)

# **PATCH//HIVE**

### *Modular Synthesis • Deterministic Exploration • Community-Driven Design*

[![License: MIT](https://img.shields.io/badge/License-MIT-7FF7FF.svg?style=for-the-badge)](LICENSE)
[![ABX-Core](https://img.shields.io/badge/ABX--Core-v1.2-FF1EA0.svg?style=for-the-badge)](docs/ABX_CORE_COMPLIANCE.md)
[![Python](https://img.shields.io/badge/Python-3.11+-7FF7FF.svg?style=for-the-badge&logo=python&logoColor=white)](backend/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-FF1EA0.svg?style=for-the-badge&logo=typescript&logoColor=white)](frontend/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-7FF7FF.svg?style=for-the-badge&logo=fastapi&logoColor=white)](backend/)
[![React](https://img.shields.io/badge/React-18.2+-FF1EA0.svg?style=for-the-badge&logo=react&logoColor=white)](frontend/)
[![Docker](https://img.shields.io/badge/Docker-Ready-7FF7FF.svg?style=for-the-badge&logo=docker&logoColor=white)](infra/)

---

## **⬡ THE SYSTEM**

**PatchHive** is a deterministic Eurorack system design and patch exploration platform. Build virtual modular synthesizer racks, generate reproducible patches, and share your discoveries with the community.

```
┌─────────────────────────────────────────────────────────────┐
│  SIGNAL FLOW:                                               │
│  [Module Catalog] → [Rack Design] → [Patch Engine]         │
│         ↓               ↓                ↓                  │
│  [Community Votes] ← [Feed] ← [Visualization & Export]     │
└─────────────────────────────────────────────────────────────┘
```

### **Core Capabilities**

🔷 **Deterministic Patch Generation** — Same rack + same seed = identical patch
🔷 **SEED Provenance Tracking** — Full lineage for every generated artifact
🔷 **Rule-Based Intelligence** — Analyzes module types to create plausible signal paths
🔷 **SVG Visualization** — Pure vector rack layouts and waveform approximations
🔷 **PDF Export** — Professional patch books with full documentation
🔷 **Community Features** — Voting, commenting, user feeds, and discovery

---

## **⬡ ARCHITECTURE**

```
┌──────────────────────┐       ┌──────────────────────┐
│   FRONTEND (React)   │◄─────►│  BACKEND (FastAPI)   │
│  • TypeScript        │  HTTP │  • Python 3.11+      │
│  • Zustand State     │  JSON │  • SQLAlchemy ORM    │
│  • Vite Bundler      │  REST │  • Alembic Migrations│
└──────────────────────┘       └──────────────────────┘
                                         │
                                         ▼
                               ┌──────────────────────┐
                               │  DATABASE (Postgres) │
                               │  • Modules           │
                               │  • Cases & Racks     │
                               │  • Patches & SEEDs   │
                               │  • Users & Community │
                               └──────────────────────┘
```

### **Technology Stack**

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18.2+ • TypeScript 5.0+ • Vite • Zustand • Axios • React Router |
| **Backend** | Python 3.11+ • FastAPI • SQLAlchemy • Pydantic • Alembic • PyJWT |
| **Database** | PostgreSQL 15+ • JSONB for metadata • Full-text search |
| **Visualization** | SVG generation • ReportLab PDF • Custom waveform engine |
| **Infrastructure** | Docker • Docker Compose • NGINX • CORS middleware |
| **Standards** | ABX-Core v1.2 • RESTful API • OpenAPI 3.1 • JWT Auth |

---

## **⬡ FEATURES**

### **🎛️ Module Management**

- **300+ Module Catalog** — Oscillators, filters, envelopes, effects, utilities
- **I/O Port Tracking** — CV inputs, gate triggers, audio outputs
- **Power Specifications** — +12V/-12V/+5V draw validation
- **Manufacturer Metadata** — Model names, HP width, descriptions

### **🗄️ Rack Design**

- **Eurorack Cases** — 84HP, 104HP, 168HP standard formats
- **Row-Based Layout** — 3U row configuration with HP alignment
- **Power Validation** — Real-time power budget checking
- **Visual Placement** — SVG rack visualization

### **🧬 Deterministic Patch Engine**

```python
# Every patch is reproducible
seed = 12345
patches = generate_patches_for_rack(rack, seed)
# Same rack + same seed = identical result, forever
```

- **Seeded Randomness** — Python `random.Random` with explicit seeds
- **Rule-Based Analysis** — Detects VCO, VCF, VCA, ENV, LFO, SEQ, UTIL modules
- **Signal Chain Logic** — Follows Eurorack conventions (VCO → VCF → VCA)
- **Category-Based Waveforms** — Harmonic, percussive, ambient, experimental, rhythmic

### **📊 Visualization & Export**

- **Rack Layout SVG** — Hex-grid visual representation
- **Waveform Approximation** — Deterministic audio visualization
- **PDF Patch Books** — Complete documentation with connection tables
- **JSON Export** — Machine-readable patch specifications

### **👥 Community**

- **User Authentication** — JWT-based secure login
- **Upvote/Downvote** — Reddit-style voting system
- **Comments** — Threaded discussions on patches
- **User Feed** — Browse community patches and racks
- **Discovery** — Trending patches, top-rated designs

---

## **⬡ ABX-CORE v1.2 COMPLIANCE**

PatchHive implements 100% of ABX-Core v1.2 requirements:

✅ **Modular Architecture** — Clean domain separation (modules, cases, racks, patches, community)
✅ **Deterministic Behavior** — All generation uses explicit seeds
✅ **Entropy Minimization** — No untracked randomness, full reproducibility
✅ **SEED Provenance** — Source, timestamps, generation metadata on all entities
✅ **Extendable Design** — Plugin architecture for new module types and analyzers

[View Full Compliance Report →](../../docs/ABX_CORE_COMPLIANCE.md)

---

## **⬡ VISUAL IDENTITY**

![PatchHive Logo](../../docs/assets/logo-primary.svg)

**Design System:** Techno-occult aesthetic with cyan (#7FF7FF) on black (#020407)

- **The Hex Coil** — Primary logo with oscillating core
- **Patch Sigil** — Vertical rune for branding
- **Module Icons** — 10 type indicators (VCO, VCF, VCA, ENV, LFO, SEQ, MIX, FX, UTIL, NOISE)
- **Animated Components** — Loading spinner, logo animation, signal flow

[View Brand Guidelines →](../../docs/BRAND_GUIDELINES.md)

---

## **⬡ QUICK START**

```bash
# Clone the repository
git clone https://github.com/yourusername/Patch-Hive.git
cd Patch-Hive

# Start with Docker Compose
cd infra
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Manual Setup:**

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## **⬡ DOCUMENTATION**

| Document | Description |
|----------|-------------|
| [Architecture Guide](../../docs/ARCHITECTURE.md) | System design and domain organization |
| [Patch Engine Deep Dive](../../docs/PATCH_ENGINE.md) | Algorithm and rule documentation |
| [Data Model](../../docs/DATA_MODEL.md) | Complete database schema |
| [API Reference](../../docs/API.md) | FastAPI endpoint documentation |
| [Component Library](../../docs/COMPONENTS.md) | React component usage |
| [Deployment Guide](../../docs/DEPLOYMENT.md) | Production setup instructions |

---

## **⬡ CONTRIBUTING**

PatchHive is open-source and welcomes contributions!

```
CONTRIBUTION AREAS:
├── Module Catalog Expansion (VCV Rack, Mutable Instruments, etc.)
├── Patch Generation Algorithms (new rules, smarter routing)
├── Visualization Enhancements (3D views, animations)
├── Community Features (collections, playlists, remix chains)
└── Documentation & Tutorials
```

[Read Contributing Guidelines →](../../CONTRIBUTING.md)

---

## **⬡ LICENSE**

MIT License — See [LICENSE](../../LICENSE) for details

---

## **⬡ CONNECT**

🌐 **Website:** [patchhive.io](https://patchhive.io)
📖 **Docs:** [docs.patchhive.io](https://docs.patchhive.io)
💬 **Discord:** [discord.gg/patchhive](https://discord.gg/patchhive)
🐦 **Twitter:** [@patchhive](https://twitter.com/patchhive)

---

<div align="center">

**Built with ⬡ by the modular synthesis community**

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=patchhive.patchhive&left_color=020407&right_color=7FF7FF&left_text=Visitors)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/Patch-Hive?style=social)](https://github.com/yourusername/Patch-Hive)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/Patch-Hive?style=social)](https://github.com/yourusername/Patch-Hive)

</div>

</div>
