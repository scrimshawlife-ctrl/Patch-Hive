"""
Pydantic models for System Pack definitions.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class PatchRef(BaseModel):
    """Reference to a patch in a system pack manifest."""

    id: str
    file: str
    name: str
    sha256: str


class SchemaInfo(BaseModel):
    """Schema information in manifest."""

    file: str
    version: str


class OntologyInfo(BaseModel):
    """Ontology file references."""

    roles: str
    operations: str
    tags: str


class SystemPackStats(BaseModel):
    """Statistics about the system pack."""

    totalPatches: int
    categories: Optional[Dict[str, int]] = None


class SystemPackManifest(BaseModel):
    """System pack manifest structure (pack.manifest.json)."""

    name: str
    system: str
    version: str
    schemaVersion: str
    description: str
    created: Optional[str] = None
    schema_info: SchemaInfo = Field(..., alias="schema")
    ontology: OntologyInfo
    patches: List[PatchRef]
    stats: Optional[SystemPackStats] = None

    class Config:
        populate_by_name = True


class VL2Connection(BaseModel):
    """Connection/wiring definition for VL2 patches."""

    from_: str = Field(..., alias="from")
    to: str
    amount: Optional[float] = None
    type: str
    role: str

    class Config:
        populate_by_name = True


class VL2Patch(BaseModel):
    """
    VL2 patch model matching patchhive.schema.vl2.v1.json.
    This represents a patch loaded from system_packs/vl2/patches/*.yaml
    """

    id: str
    name: str
    system: str
    schemaVersion: str
    intent: Optional[str] = None
    tags: Optional[List[str]] = None
    modules: Dict[str, Any]
    wiring: List[VL2Connection]
    notes: Optional[str] = None


class OntologyData(BaseModel):
    """Loaded ontology data."""

    roles: Dict[str, Any]
    operations: Dict[str, Any]
    tags: Dict[str, Any]


class SystemPackLoaded(BaseModel):
    """Loaded system pack with all data in memory."""

    system_id: str
    schema_version: str
    pack_version: str
    description: str
    ontology: OntologyData
    patches: List[VL2Patch]
    patch_count: int

    class Config:
        from_attributes = True
