from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FieldStatus(str, Enum):
    """Status of a field in the gallery."""
    confirmed = "confirmed"  # Verified by human or authoritative source
    inferred = "inferred"    # Derived from data but not verified
    placeholder = "placeholder"  # Temporary value awaiting update


class ProvenanceType(str, Enum):
    """Source type for gallery data."""
    manual = "manual"        # User-entered
    scraped = "scraped"      # Automated scraping
    derived = "derived"      # Computed from other data
    vision = "vision"        # Extracted from image analysis


class ModuleAttachmentType(str, Enum):
    """Type of module attachment."""
    sketch_svg = "sketch_svg"        # Generated SVG sketch
    photo_front = "photo_front"      # Front panel photo
    photo_rear = "photo_rear"        # Rear panel photo
    manual_pdf = "manual_pdf"        # User manual PDF
    spec_sheet = "spec_sheet"        # Technical specification sheet


class ModuleIdentity(BaseModel):
    """Core identity fields for a module."""
    manufacturer: str
    name: str
    hp: int
    module_key: str  # Stable key: {manufacturer}__{name}__{hp}hp


class ModuleAttachment(BaseModel):
    """Attachment (image, PDF, sketch) associated with a module."""
    attachment_id: str  # e.g., "att.sketch.generated", "att.photo.front.001"
    type: ModuleAttachmentType
    ref: str  # Path or URL to the attachment
    source: str  # e.g., "derived", "uploaded", "scraped"
    meta: Dict[str, Any] = Field(default_factory=dict)


class ModuleJack(BaseModel):
    """Jack definition for a module."""
    jack_id: str
    label: str
    dir: str  # "in", "out", "both"
    signal: str  # "cv", "gate", "audio", "digital"
    x_pos: Optional[float] = None  # Normalized 0..1
    y_pos: Optional[float] = None  # Normalized 0..1


class ModuleGalleryRevision(BaseModel):
    """A revision in the module gallery."""
    module_key: str  # Stable key identifying the module
    revision_id: str  # Content-addressable ID for this revision
    version: int  # Monotonic version number (0, 1, 2, ...)

    identity: ModuleIdentity
    tags: List[str] = Field(default_factory=list)
    jacks: List[ModuleJack] = Field(default_factory=list)
    attachments: List[ModuleAttachment] = Field(default_factory=list)

    meta: Dict[str, Any] = Field(default_factory=dict)  # Provenance, timestamps, etc.
