"""
PatchHive Backend API
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core import settings, init_db

# Import all models to register them with SQLAlchemy before init_db()
from modules.models import Module  # noqa: F401
from modules.catalog import ModuleCatalog  # noqa: F401
from cases.models import Case  # noqa: F401
from racks.models import Rack, RackModule  # noqa: F401
from patches.models import Patch  # noqa: F401
from community.models import User, Vote, Comment  # noqa: F401
from monetization.models import CreditsLedger, Export, License, Referral  # noqa: F401
from admin.models import AdminAuditLog  # noqa: F401
from gallery.models import GalleryRevision  # noqa: F401
from runs.models import Run  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"ABX-Core version: {settings.abx_core_version}")
    init_db()
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Eurorack system design and patch exploration platform",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "abx_core_version": settings.abx_core_version,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "description": "Eurorack system design and patch exploration platform",
        "docs_url": "/docs",
        "abx_core_version": settings.abx_core_version,
        "seed_enforcement": settings.enforce_seed_traceability,
    }


# Import and register routers  # noqa: E402
from modules.routes import router as modules_router  # noqa: E402
from modules.catalog_routes import router as catalog_router  # noqa: E402
from cases.routes import router as cases_router  # noqa: E402
from racks.routes import router as racks_router  # noqa: E402
from patches.routes import router as patches_router  # noqa: E402
from community.routes import router as community_router  # noqa: E402
from export.routes import router as export_router  # noqa: E402
from integrations.router import router as integrations_router  # noqa: E402
from monetization.routes import router as monetization_router  # noqa: E402
from admin.routes import router as admin_router  # noqa: E402
from runs.routes import router as runs_router  # noqa: E402
from ingest.system_packs.routes import router as system_packs_router  # noqa: E402

app.include_router(catalog_router, prefix="/api/modules", tags=["catalog"])
app.include_router(modules_router, prefix="/api/modules", tags=["modules"])
app.include_router(cases_router, prefix="/api/cases", tags=["cases"])
app.include_router(racks_router, prefix="/api/racks", tags=["racks"])
app.include_router(patches_router, prefix="/api/patches", tags=["patches"])
app.include_router(community_router, prefix="/api/community", tags=["community"])
app.include_router(export_router, prefix="/api/export", tags=["export"])
app.include_router(integrations_router, prefix="/api", tags=["integrations"])
app.include_router(monetization_router, prefix="/api/monetization", tags=["monetization"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(runs_router, prefix="/api/runs", tags=["runs"])
app.include_router(system_packs_router, prefix="/api/ingest", tags=["ingest"])
