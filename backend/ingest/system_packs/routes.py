"""
FastAPI routes for System Pack ingestion.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .importer import import_system_pack


router = APIRouter()


class SystemPackImportRequest(BaseModel):
    """Request schema for importing a system pack."""

    pack_path: str = Field(
        ...,
        description="Path to system pack directory",
        examples=["system_packs/vl2"],
    )
    persist: bool = Field(
        default=False, description="If true, persist patches to database"
    )


class SystemPackImportResponse(BaseModel):
    """Response schema for system pack import."""

    system_id: str
    schema_version: str
    patch_count: int
    ontology: dict = Field(
        description="Ontology summary (roles, operations, tags counts)"
    )
    description: str
    pack_version: str


@router.post("/system-pack", response_model=SystemPackImportResponse)
async def ingest_system_pack(request: SystemPackImportRequest):
    """
    Import and validate a system pack.

    Loads patches, verifies SHA-256 hashes, validates against schema.
    By default, operates in read-only mode (persist=False).

    Args:
        request: Import request with pack_path and persist flag

    Returns:
        SystemPackImportResponse with loaded pack metadata

    Raises:
        HTTPException 404: Pack not found
        HTTPException 422: Validation failed
    """
    try:
        loaded_pack = import_system_pack(
            request.pack_path, persist=request.persist
        )

        # Summarize ontology
        ontology_summary = {
            "roles": len(loaded_pack.ontology.roles.get("roles", {})),
            "operations": len(loaded_pack.ontology.operations.get("operations", {})),
            "tags": len(loaded_pack.ontology.tags.get("allowedTags", [])),
        }

        return SystemPackImportResponse(
            system_id=loaded_pack.system_id,
            schema_version=loaded_pack.schema_version,
            patch_count=loaded_pack.patch_count,
            ontology=ontology_summary,
            description=loaded_pack.description,
            pack_version=loaded_pack.pack_version,
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
