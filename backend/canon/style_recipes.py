"""User style recipe library domain helpers."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from canon.models import UserStyleRecipeRecord
from export.patchbook.design.recipe import RequestStyleRecipe, recipe_hash

_MAX_RECIPES_PER_USER = 40
_NAME_RE = re.compile(r"^[\w \-.'/&+]{1,120}$", re.UNICODE)


class StyleRecipeLibraryError(ValueError):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code
        self.message = message or code


def _stable_id(user_id: int, name: str, when: datetime) -> str:
    material = f"{user_id}:{name}:{when.isoformat()}"
    return f"srecipe-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:24]}"


def _validate_name(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned or not _NAME_RE.match(cleaned):
        raise StyleRecipeLibraryError("INVALID_RECIPE_NAME", "Recipe name invalid or empty")
    return cleaned


def _parse_recipe(payload: dict) -> RequestStyleRecipe:
    try:
        return RequestStyleRecipe.model_validate(payload)
    except Exception as exc:
        raise StyleRecipeLibraryError("INVALID_STYLE_RECIPE", str(exc)) from exc


def list_user_recipes(session: Session, user_id: int) -> list[UserStyleRecipeRecord]:
    return list(
        session.scalars(
            select(UserStyleRecipeRecord)
            .where(UserStyleRecipeRecord.user_id == user_id)
            .order_by(UserStyleRecipeRecord.updated_at.desc())
            .limit(_MAX_RECIPES_PER_USER)
        )
    )


def get_user_recipe(session: Session, user_id: int, recipe_id: str) -> UserStyleRecipeRecord | None:
    row = session.get(UserStyleRecipeRecord, recipe_id)
    if row is None or row.user_id != user_id:
        return None
    return row


def create_user_recipe(
    session: Session,
    *,
    user_id: int,
    name: str,
    recipe_payload: dict,
    notes: str | None = None,
    is_shared: bool = False,
) -> UserStyleRecipeRecord:
    name = _validate_name(name)
    recipe = _parse_recipe(recipe_payload)
    count = len(list_user_recipes(session, user_id))
    if count >= _MAX_RECIPES_PER_USER:
        raise StyleRecipeLibraryError(
            "RECIPE_LIBRARY_FULL",
            f"Maximum {_MAX_RECIPES_PER_USER} saved recipes per user",
        )
    existing = session.scalar(
        select(UserStyleRecipeRecord).where(
            UserStyleRecipeRecord.user_id == user_id,
            UserStyleRecipeRecord.name == name,
        )
    )
    if existing is not None:
        raise StyleRecipeLibraryError("RECIPE_NAME_CONFLICT", "Recipe name already exists")

    now = datetime.now(timezone.utc)
    row = UserStyleRecipeRecord(
        id=_stable_id(user_id, name, now),
        user_id=user_id,
        name=name,
        notes=(notes or "")[:500] or None,
        recipe_json=recipe.model_dump(mode="json"),
        recipe_hash=recipe_hash(recipe),
        is_shared=bool(is_shared),
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.flush()
    return row


def update_user_recipe(
    session: Session,
    *,
    user_id: int,
    recipe_id: str,
    name: str | None = None,
    recipe_payload: dict | None = None,
    notes: str | None = None,
    is_shared: bool | None = None,
) -> UserStyleRecipeRecord:
    row = get_user_recipe(session, user_id, recipe_id)
    if row is None:
        raise StyleRecipeLibraryError("RECIPE_NOT_FOUND", "Recipe not found")
    if name is not None:
        new_name = _validate_name(name)
        if new_name != row.name:
            clash = session.scalar(
                select(UserStyleRecipeRecord).where(
                    UserStyleRecipeRecord.user_id == user_id,
                    UserStyleRecipeRecord.name == new_name,
                )
            )
            if clash is not None:
                raise StyleRecipeLibraryError("RECIPE_NAME_CONFLICT", "Recipe name already exists")
            row.name = new_name
    if recipe_payload is not None:
        recipe = _parse_recipe(recipe_payload)
        row.recipe_json = recipe.model_dump(mode="json")
        row.recipe_hash = recipe_hash(recipe)
    if notes is not None:
        row.notes = notes[:500] or None
    if is_shared is not None:
        row.is_shared = bool(is_shared)
    row.updated_at = datetime.now(timezone.utc)
    session.flush()
    return row


def delete_user_recipe(session: Session, *, user_id: int, recipe_id: str) -> None:
    row = get_user_recipe(session, user_id, recipe_id)
    if row is None:
        raise StyleRecipeLibraryError("RECIPE_NOT_FOUND", "Recipe not found")
    session.delete(row)
    session.flush()
