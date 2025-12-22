from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PatchExportItem(BaseModel):
    patch_id: str
    name: str
    category: str
    difficulty: str
    cable_count: int
    stability_score: float
    warnings: List[str] = Field(default_factory=list)

    svg_path: Optional[str] = None
    pdf_page: Optional[int] = None  # if you compute page map
    tags: List[str] = Field(default_factory=list)


class PatchLibraryUX(BaseModel):
    run_id: str
    rig_id: str
    patch_count: int
    categories: Dict[str, int]
    difficulty: Dict[str, int]

    items: List[PatchExportItem]

    download_pdf_url: str
    download_bundle_url: str
