"""User style recipe library domain + persistence tests."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from canon.style_recipes import (
    StyleRecipeLibraryError,
    create_user_recipe,
    delete_user_recipe,
    get_user_recipe,
    list_user_recipes,
    update_user_recipe,
)
from community.models import User
from export.patchbook.design.recipe import default_request_recipe


def _user(db: Session) -> User:
    user = User(username="recipe-lib", email="recipe-lib@example.com", password_hash="h")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_list_update_delete_recipe(db_session: Session) -> None:
    user = _user(db_session)
    payload = default_request_recipe(seed=99).model_dump(mode="json")
    row = create_user_recipe(
        db_session, user_id=user.id, name="Studio Pro", recipe_payload=payload, notes="n1"
    )
    db_session.commit()
    assert row.id.startswith("srecipe-")
    assert row.recipe_hash
    listed = list_user_recipes(db_session, user.id)
    assert len(listed) == 1
    assert listed[0].name == "Studio Pro"

    payload["seed"] = 100
    updated = update_user_recipe(
        db_session,
        user_id=user.id,
        recipe_id=row.id,
        name="Studio Pro 2",
        recipe_payload=payload,
    )
    db_session.commit()
    assert updated.name == "Studio Pro 2"
    assert updated.recipe_json["seed"] == 100

    delete_user_recipe(db_session, user_id=user.id, recipe_id=row.id)
    db_session.commit()
    assert get_user_recipe(db_session, user.id, row.id) is None


def test_name_conflict_and_invalid_recipe(db_session: Session) -> None:
    user = _user(db_session)
    payload = default_request_recipe().model_dump(mode="json")
    create_user_recipe(db_session, user_id=user.id, name="A", recipe_payload=payload)
    db_session.commit()
    with pytest.raises(StyleRecipeLibraryError) as exc:
        create_user_recipe(db_session, user_id=user.id, name="A", recipe_payload=payload)
    assert exc.value.code == "RECIPE_NAME_CONFLICT"

    with pytest.raises(StyleRecipeLibraryError) as exc2:
        create_user_recipe(
            db_session,
            user_id=user.id,
            name="Bad",
            recipe_payload={"mode": "not-a-mode"},
        )
    assert exc2.value.code == "INVALID_STYLE_RECIPE"
