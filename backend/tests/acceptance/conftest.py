import os
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient

from core.security import get_password_hash
from community.models import User
from modules.models import Module
from cases.models import Case

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = REPO_ROOT / "fixtures" / "golden_demo_seed.json"


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container: PostgresContainer) -> str:
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def migrated_db(database_url: str, tmp_path_factory: pytest.TempPathFactory) -> sessionmaker:
    os.environ["DATABASE_URL"] = database_url
    os.environ["TEST_MODE"] = "true"
    os.environ["EXPORT_DIR"] = str(tmp_path_factory.mktemp("exports"))

    import core.config
    import core.database
    import main

    importlib.reload(core.config)
    importlib.reload(core.database)
    importlib.reload(main)

    alembic_cfg = Config(str(Path(__file__).resolve().parents[1] / ".." / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(database_url)
    return sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def _clean_db(migrated_db: sessionmaker) -> None:
    engine = migrated_db.bind
    with engine.begin() as conn:
        tables = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        ).fetchall()
        for (table,) in tables:
            conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))


@pytest.fixture()
def db_session(migrated_db: sessionmaker) -> Generator[Session, None, None]:
    session = migrated_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def api_client(migrated_db: sessionmaker) -> TestClient:
    import main

    return TestClient(main.app)


@pytest.fixture()
def create_user(db_session: Session):
    def _create(username: str, password: str, role: str = "User") -> User:
        user = User(
            username=username,
            email=f"{username}@patchhive.test",
            password_hash=get_password_hash(password),
            display_name=username,
            role=role,
            referral_code=f"{username}-ref",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create


@pytest.fixture()
def login(api_client: TestClient):
    def _login(username: str, password: str) -> str:
        resp = api_client.post(
            "/api/community/auth/login",
            json={"username": username, "password": password},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    return _login


@pytest.fixture()
def admin_user(create_user) -> User:
    return create_user("admin", "admin-pass", role="Admin")


@pytest.fixture()
def seed_minimal_modules(db_session: Session):
    case = Case(
        id=2001,
        brand="Intellijel",
        name="7U Performance Case",
        total_hp=208,
        rows=2,
        hp_per_row=[104, 104],
        power_12v_ma=3000,
        power_neg12v_ma=1500,
        power_5v_ma=500,
        description="Professional 7U case",
        source="Manual",
        source_reference="Seed data",
    )
    db_session.add(case)

    modules = [
        Module(
            id=1001,
            brand="Mutable Instruments",
            name="Plaits",
            hp=12,
            module_type="VCO",
            power_12v_ma=70,
            power_neg12v_ma=5,
            io_ports=[{"name": "Out", "type": "audio_out"}],
            tags=["digital"],
            description="Macro oscillator",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1002,
            brand="Mutable Instruments",
            name="Ripples",
            hp=8,
            module_type="VCF",
            power_12v_ma=50,
            power_neg12v_ma=50,
            io_ports=[{"name": "LP Out", "type": "audio_out"}],
            tags=["analog"],
            description="Filter",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1003,
            brand="Intellijel",
            name="Quad VCA",
            hp=12,
            module_type="VCA",
            power_12v_ma=60,
            power_neg12v_ma=60,
            io_ports=[{"name": "Out 1", "type": "audio_out"}],
            tags=["vca"],
            description="VCA",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1004,
            brand="Make Noise",
            name="Maths",
            hp=20,
            module_type="ENV",
            power_12v_ma=60,
            power_neg12v_ma=60,
            io_ports=[{"name": "Out 1", "type": "cv_out"}],
            tags=["utility"],
            description="Envelope",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1005,
            brand="Mutable Instruments",
            name="Batumi",
            hp=10,
            module_type="LFO",
            power_12v_ma=70,
            power_neg12v_ma=10,
            io_ports=[{"name": "LFO 1 Out", "type": "cv_out"}],
            tags=["lfo"],
            description="LFO",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1006,
            brand="Make Noise",
            name="Rene 2",
            hp=34,
            module_type="SEQ",
            power_12v_ma=150,
            power_neg12v_ma=30,
            io_ports=[{"name": "Gate Out", "type": "gate_out"}],
            tags=["sequencer"],
            description="Sequencer",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1007,
            brand="Intellijel",
            name="Mixup",
            hp=6,
            module_type="MIX",
            power_12v_ma=40,
            power_neg12v_ma=40,
            io_ports=[{"name": "Mix Out", "type": "audio_out"}],
            tags=["utility"],
            description="Mixer",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1008,
            brand="Mutable Instruments",
            name="Clouds",
            hp=18,
            module_type="FX",
            power_12v_ma=100,
            power_neg12v_ma=20,
            io_ports=[{"name": "Out L", "type": "audio_out"}],
            tags=["fx"],
            description="FX",
            source="Manual",
            source_reference="Seed data",
        ),
        Module(
            id=1009,
            brand="Noise Engineering",
            name="Ataraxic Iteritas",
            hp=6,
            module_type="NOISE",
            power_12v_ma=42,
            power_neg12v_ma=22,
            io_ports=[{"name": "Noise Out", "type": "audio_out"}],
            tags=["noise"],
            description="Noise",
            source="Manual",
            source_reference="Seed data",
        ),
    ]
    db_session.add_all(modules)
    db_session.commit()

    return {"case": case, "modules": modules}


@pytest.fixture()
def golden_demo_seed(db_session: Session):
    seed_script = REPO_ROOT / "scripts" / "seed_golden_demo.py"
    spec = importlib.util.spec_from_file_location("seed_golden_demo", seed_script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["seed_golden_demo"] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.seed_golden_demo(db_session)
