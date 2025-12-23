"""Utilities for publishing layer."""
import re
import uuid


def slugify_title(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return base or "publication"


def unique_slug(base: str) -> str:
    suffix = uuid.uuid4().hex[:8]
    return f"{base}-{suffix}"

