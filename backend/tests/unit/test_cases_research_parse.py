"""Unit tests for Cases4PatchHive research → Case schema parser."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from parse_cases_research import build_fixture, parse_markdown  # noqa: E402

FIXTURE_MD = REPO / "fixtures" / "Cases4PatchHive.md"
FIXTURE_JSON = REPO / "fixtures" / "cases_research_2026.json"


@pytest.mark.skipif(not FIXTURE_MD.is_file(), reason="research markdown fixture missing")
def test_parse_yields_fifty_cases():
    cases = parse_markdown(FIXTURE_MD.read_text(encoding="utf-8"))
    assert len(cases) == 50


@pytest.mark.skipif(not FIXTURE_MD.is_file(), reason="research markdown fixture missing")
def test_known_layouts_and_power():
    cases = parse_markdown(FIXTURE_MD.read_text(encoding="utf-8"))
    by_key = {(c["brand"], c["name"]): c for c in cases}

    art6 = by_key[("Arturia", "RackBrute 6U")]
    assert art6["total_hp"] == 176
    assert art6["hp_per_row"] == [88, 88]
    assert art6["power_12v_ma"] == 1600
    assert art6["power_neg12v_ma"] == 800
    assert art6["power_5v_ma"] == 500

    ij = by_key[("Intellijel", "7U Performance Case Gen-2 104HP")]
    assert ij["hp_per_row"] == [104, 104, 104]
    assert ij["power_12v_ma"] == 6000

    skiff = by_key[("Make Noise", "Skiff No Power")]
    assert skiff["power_12v_ma"] is None
    assert skiff["meta"]["powered"] is False

    buchla = by_key[("Buchla", "201e-4 Powered Boat")]
    assert buchla["meta"]["capacity_unit"] == "buchla_panels"
    assert buchla["total_hp"] == 4

    mantis = by_key[("Tiptop Audio", "Mantis")]
    assert mantis["total_hp"] == 208
    assert mantis["power_12v_ma"] == 3000


@pytest.mark.skipif(not FIXTURE_MD.is_file(), reason="research markdown fixture missing")
def test_case_create_schema_accepts_all():
    sys.path.insert(0, str(REPO / "backend"))
    from cases.schemas import CaseCreate

    fixture = build_fixture(FIXTURE_MD)
    for raw in fixture["cases"]:
        CaseCreate.model_validate(raw)


@pytest.mark.skipif(not FIXTURE_JSON.is_file(), reason="json fixture missing")
def test_checked_in_json_matches_parser():
    disk = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    fresh = build_fixture(FIXTURE_MD)
    assert disk["case_count"] == fresh["case_count"] == 50
    assert {(c["brand"], c["name"]) for c in disk["cases"]} == {
        (c["brand"], c["name"]) for c in fresh["cases"]
    }
