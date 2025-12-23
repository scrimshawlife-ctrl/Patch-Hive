from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict

from .normalize import canonicalize_patchbook_payload


def compute_patchbook_content_hash(payload_dict: Dict[str, Any], template_version: str) -> str:
    canonical = canonicalize_patchbook_payload(payload_dict)
    digest = sha256(f"{canonical}|{template_version}".encode("utf-8")).hexdigest()
    return digest
