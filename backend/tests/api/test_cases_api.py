"""API tests for /api/cases list filters (C0)."""

import pytest

pytest.importorskip("httpx", reason="httpx is required for FastAPI TestClient")

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from cases.models import Case
from core import get_db
from main import app


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def catalog_cases(db_session: Session) -> list[Case]:
    rows = [
        Case(
            brand="Intellijel",
            name="Palette 62",
            total_hp=124,
            rows=2,
            hp_per_row=[62, 62],
            power_12v_ma=1200,
            format_family="Eurorack",
            capacity_unit="hp",
            powered=True,
            source="test",
            meta={"format_family": "Eurorack", "powered": True},
        ),
        Case(
            brand="Buchla",
            name="201e-4",
            total_hp=4,
            rows=1,
            hp_per_row=[4],
            format_family="Buchla",
            capacity_unit="buchla_panels",
            powered=True,
            source="test",
            meta={"format_family": "Buchla", "capacity_unit": "buchla_panels", "powered": True},
        ),
        Case(
            brand="Make Noise",
            name="Skiff No Power",
            total_hp=104,
            rows=1,
            hp_per_row=[104],
            format_family="Eurorack",
            capacity_unit="hp",
            powered=False,
            source="test",
            meta={"format_family": "Eurorack", "powered": False},
        ),
    ]
    for row in rows:
        db_session.add(row)
    db_session.commit()
    for row in rows:
        db_session.refresh(row)
    return rows


class TestCasesAPI:
    def test_list_format_eurorack(self, client: TestClient, catalog_cases: list[Case]):
        res = client.get("/api/cases/", params={"format_family": "Eurorack"})
        assert res.status_code == 200
        data = res.json()
        names = {c["name"] for c in data["cases"]}
        assert "Palette 62" in names
        assert "Skiff No Power" in names
        assert "201e-4" not in names

    def test_list_powered_false(self, client: TestClient, catalog_cases: list[Case]):
        res = client.get("/api/cases/", params={"powered": False})
        assert res.status_code == 200
        names = {c["name"] for c in res.json()["cases"]}
        assert names == {"Skiff No Power"}

    def test_list_search_q(self, client: TestClient, catalog_cases: list[Case]):
        res = client.get("/api/cases/", params={"q": "Buchla"})
        assert res.status_code == 200
        assert res.json()["total"] == 1
        assert res.json()["cases"][0]["brand"] == "Buchla"
