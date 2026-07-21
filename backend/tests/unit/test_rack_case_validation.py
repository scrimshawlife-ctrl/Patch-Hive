"""Unit tests for case format + power validation (C1/C2)."""

from sqlalchemy.orm import Session

from cases.models import Case
from modules.models import Module
from racks.schemas import RackModuleSpec
from racks.validation import validate_rack_configuration


def _case(db: Session, **kwargs) -> Case:
    defaults = dict(
        brand="Test",
        name="Case",
        total_hp=84,
        rows=1,
        hp_per_row=[84],
        format_family="Eurorack",
        capacity_unit="hp",
        powered=True,
        source="test",
    )
    defaults.update(kwargs)
    row = Case(**defaults)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _mod(db: Session, hp: int = 12, p12: int = 50) -> Module:
    m = Module(
        brand="T",
        name=f"M{hp}",
        hp=hp,
        module_type="VCO",
        power_12v_ma=p12,
        power_neg12v_ma=10,
        source="test",
        source_reference="t",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def test_power_exceeded_hard_error(db_session: Session):
    case = _case(db_session, power_12v_ma=40, power_neg12v_ma=100)
    mod = _mod(db_session, p12=50)
    ok, errors, warnings = validate_rack_configuration(
        db_session, case.id, [RackModuleSpec(module_id=mod.id, row_index=0, start_hp=0)]
    )
    assert not ok
    assert any((e.details or {}).get("code") == "POWER_EXCEEDED_12V" for e in errors)
    assert warnings == []


def test_power_unspecified_warning(db_session: Session):
    case = _case(db_session, power_12v_ma=None, power_neg12v_ma=None, power_5v_ma=None)
    mod = _mod(db_session, p12=50)
    ok, errors, warnings = validate_rack_configuration(
        db_session, case.id, [RackModuleSpec(module_id=mod.id, row_index=0, start_hp=0)]
    )
    assert ok
    assert errors == []
    assert any((w.details or {}).get("code") == "POWER_UNSPECIFIED" for w in warnings)


def test_unpowered_case_hard_error(db_session: Session):
    case = _case(db_session, powered=False, power_12v_ma=None)
    mod = _mod(db_session, p12=50)
    ok, errors, _ = validate_rack_configuration(
        db_session, case.id, [RackModuleSpec(module_id=mod.id, row_index=0, start_hp=0)]
    )
    assert not ok
    assert any((e.details or {}).get("code") == "POWER_ON_UNPOWERED_CASE" for e in errors)


def test_non_eurorack_placement_hard_error(db_session: Session):
    case = _case(
        db_session,
        format_family="Buchla",
        capacity_unit="buchla_panels",
        total_hp=4,
        hp_per_row=[4],
    )
    mod = _mod(db_session)
    ok, errors, _ = validate_rack_configuration(
        db_session, case.id, [RackModuleSpec(module_id=mod.id, row_index=0, start_hp=0)]
    )
    assert not ok
    assert any(
        (e.details or {}).get("code") == "FORMAT_NOT_SUPPORTED_FOR_PLACEMENT" for e in errors
    )


def test_empty_modules_ok(db_session: Session):
    case = _case(db_session)
    ok, errors, warnings = validate_rack_configuration(db_session, case.id, [])
    assert ok
    assert errors == []
    assert warnings == []
