"""API endpoint tests for leaderboards."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app


@pytest.fixture
def client(db_session: Session):
    """Create a test client with database override."""
    from core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_leaderboards_no_user_ids(client: TestClient, db_session: Session, sample_rack_basic):
    """Leaderboards should not include user IDs."""
    sample_rack_basic.is_public = True
    db_session.commit()
    response = client.get("/api/leaderboards/modules/popular")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        entry = data[0]
        assert "user_id" not in entry
        assert set(entry.keys()) == {"rank", "module_name", "manufacturer", "count"}
