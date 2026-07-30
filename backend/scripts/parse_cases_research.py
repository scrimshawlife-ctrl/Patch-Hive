#!/usr/bin/env python3
"""
Parse Cases4PatchHive research markdown into Case-schema JSON.

Schema fields (cases.models.Case / CaseCreate):
  brand, name, total_hp, rows, hp_per_row,
  power_12v_ma, power_neg12v_ma, power_5v_ma (optional),
  description, manufacturer_url, meta,
  source, source_reference

Non-Eurorack formats store capacity in total_hp/hp_per_row with
meta.capacity_unit (buchla_panels | mu_spaces | serge_* | frac_widths).
Unspecified rails stay null (fail-closed — never invented).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MD = REPO_ROOT / "fixtures" / "Cases4PatchHive.md"
DEFAULT_OUT = REPO_ROOT / "fixtures" / "cases_research_2026.json"

SOURCE_LABEL = "ResearchCSV"
SOURCE_REF = "fixtures/Cases4PatchHive.md master table (research 2026; unspecified → null)"


def _table_rows(md: str) -> list[dict[str, str]]:
    start = md.index("| Manufacturer")
    power_hdr = md.index("## Power specification table")
    table_block = md[start:power_hdr]
    lines = [ln.strip() for ln in table_block.splitlines() if ln.strip().startswith("|")]
    rows: list[dict[str, str]] = []
    for ln in lines[2:]:
        parts = [p.strip() for p in ln.strip("|").split("|")]
        if len(parts) < 7:
            continue
        rows.append(
            {
                "manufacturer": parts[0],
                "model": parts[1],
                "formats": parts[2],
                "size_and_depth": parts[3],
                "power_and_bus": parts[4],
                "mounting": parts[5],
                "build_price_year": parts[6],
                "sources_raw": parts[7] if len(parts) > 7 else "",
            }
        )
    return rows


def parse_amps_to_ma(text: str) -> dict[str, int | None]:
    out: dict[str, int | None] = {
        "power_12v_ma": None,
        "power_neg12v_ma": None,
        "power_5v_ma": None,
    }
    for rail, key in [
        (r"\+12\s*(\d+(?:\.\d+)?)\s*mA", "power_12v_ma"),
        (r"-12\s*(\d+(?:\.\d+)?)\s*mA", "power_neg12v_ma"),
        (r"\+5\s*(\d+(?:\.\d+)?)\s*mA", "power_5v_ma"),
    ]:
        m = re.search(rail, text, re.I)
        if m:
            out[key] = int(float(m.group(1)))
    for rail, key in [
        (r"\+12\s*(\d+(?:\.\d+)?)\s*A\b", "power_12v_ma"),
        (r"-12\s*(\d+(?:\.\d+)?)\s*A\b", "power_neg12v_ma"),
        (r"\+5\s*(\d+(?:\.\d+)?)\s*A\b", "power_5v_ma"),
    ]:
        if out[key] is None:
            m = re.search(rail, text, re.I)
            if m:
                out[key] = int(round(float(m.group(1)) * 1000))
    m = re.search(r"(\d+)\s*mA\s+per\s+rail", text, re.I)
    if m:
        ma = int(m.group(1))
        out["power_12v_ma"] = out["power_12v_ma"] or ma
        out["power_neg12v_ma"] = out["power_neg12v_ma"] or ma
    m = re.search(r"\+/-?\s*15\s*V\s*@\s*(\d+)\s*mA", text, re.I)
    if m:
        ma = int(m.group(1))
        out["power_12v_ma"] = out["power_12v_ma"] or ma
        out["power_neg12v_ma"] = out["power_neg12v_ma"] or ma
    return out


def parse_layout(size: str, formats: str) -> dict[str, Any]:
    meta: dict[str, Any] = {"format_raw": formats, "size_raw": size}
    fmt_l = formats.lower()
    size_part = size.split(";")[0].strip()
    meta["size_summary"] = size_part
    for key, pat in [
        ("depth_raw", r"depth\s+([^;]+)"),
        ("usable_depth_raw", r"usable\s+([^;]+)"),
        ("outer_dims_raw", r"dims\s+([^;]+)"),
    ]:
        m = re.search(pat, size, re.I)
        if m:
            meta[key] = m.group(1).strip()

    if "buchla" in fmt_l:
        m = re.search(r"(\d+)\s+Buchla\s+panels", size, re.I)
        m2 = re.search(r"(\d+)\s+modules", size, re.I)
        n = int(m.group(1)) if m else (int(m2.group(1)) if m2 else 1)
        meta.update(capacity_unit="buchla_panels", capacity=n, format_family="Buchla")
        return {"total_hp": n, "rows": 1, "hp_per_row": [n], "meta": meta}

    if "5u" in fmt_l or re.search(r"\bMU\b", formats):
        m = re.search(r"(\d+)\s*MU", size, re.I)
        n = int(m.group(1)) if m else 1
        mrow = re.search(r"(\d+)\s*×\s*(\d+)", size)
        meta.update(capacity_unit="mu_spaces", capacity=n, format_family="5U MU")
        if mrow and "MU" in size:
            rows, per = int(mrow.group(1)), int(mrow.group(2))
            return {"total_hp": n, "rows": rows, "hp_per_row": [per] * rows, "meta": meta}
        return {"total_hp": n, "rows": 1, "hp_per_row": [n], "meta": meta}

    if "frac" in fmt_l:
        m = re.search(r"(\d+)\s+Frac\s+widths", size, re.I)
        n = int(m.group(1)) if m else 20
        rows = 2 if re.search(r"6U|2\s+rows", size, re.I) else 1
        per = n // rows
        meta.update(
            capacity_unit="frac_widths",
            capacity=n,
            format_family="Frac",
            rail_voltage_nominal="±15V",
        )
        return {"total_hp": n, "rows": rows, "hp_per_row": [per] * rows, "meta": meta}

    if "serge" in fmt_l:
        m6 = re.search(r"(\d+)\s+Random\*Source\s+4×4", size, re.I)
        if m6:
            n = int(m6.group(1))
            meta.update(capacity_unit="serge_4x4_modules", capacity=n, format_family="Serge 4U")
            return {"total_hp": n, "rows": 1, "hp_per_row": [n], "meta": meta}
        meta.update(capacity_unit="serge_panels", capacity=1, format_family="Serge 4U")
        return {"total_hp": 1, "rows": 1, "hp_per_row": [1], "meta": meta}

    meta["format_family"] = "Eurorack"
    meta["capacity_unit"] = "hp"
    hp_rows: list[int] = []

    if re.search(r"(\d+)\s*[×x]\s*(\d+)\s*HP\s*3U\s*\+\s*(\d+)\s*HP", size_part, re.I) and (
        "utility" in size_part.lower() or "1U" in size_part
    ):
        m = re.search(r"(\d+)\s*[×x]\s*(\d+)\s*HP\s*3U\s*\+\s*(\d+)\s*HP", size_part, re.I)
        assert m
        hp_rows = [int(m.group(2))] * int(m.group(1)) + [int(m.group(3))]
    elif re.search(r"(\d+)\s*HP\s*3U\s*\+\s*(\d+)\s*HP\s*1U", size_part, re.I):
        m = re.search(r"(\d+)\s*HP\s*3U\s*\+\s*(\d+)\s*HP\s*1U", size_part, re.I)
        assert m
        hp_rows = [int(m.group(1)), int(m.group(2))]
    elif re.search(r"(\d+)\s*[×x]\s*(\d+)\s*HP", size_part, re.I):
        m = re.search(r"(\d+)\s*[×x]\s*(\d+)\s*HP", size_part, re.I)
        assert m
        hp_rows = [int(m.group(2))] * int(m.group(1))
    elif re.search(r"\((\d+)\s*[×x]\s*(\d+)\s*HP\)", size_part, re.I):
        m = re.search(r"\((\d+)\s*[×x]\s*(\d+)\s*HP\)", size_part, re.I)
        assert m
        hp_rows = [int(m.group(2))] * int(m.group(1))
    elif re.search(r"(\d+)\s*HP\s*(3U|6U|9U)\b", size_part, re.I):
        m = re.search(r"(\d+)\s*HP\s*(3U|6U|9U)\b", size_part, re.I)
        assert m
        hp, unit = int(m.group(1)), m.group(2).upper()
        if unit == "3U":
            hp_rows = [hp]
        elif unit == "6U":
            # Small HP → per-row (Doepfer 84HP 6U). Large even HP → total (Arturia 176HP 6U).
            if hp >= 140 and hp % 2 == 0:
                half = hp // 2
                hp_rows = [half, half]
                meta["layout_note"] = "6U total_hp split evenly across 2 rows"
            else:
                hp_rows = [hp, hp]
        else:  # 9U
            if hp >= 140 and hp % 3 == 0:
                third = hp // 3
                hp_rows = [third, third, third]
                meta["layout_note"] = "9U total_hp split evenly across 3 rows"
            else:
                hp_rows = [hp, hp, hp]
    elif re.search(r"(\d+)\s*HP-ready", size_part, re.I):
        m = re.search(r"(\d+)\s*HP-ready", size_part, re.I)
        assert m
        hp_rows = [int(m.group(1))]
        meta["kind"] = "diy_power_kit"
    elif re.search(r"(\d+)\s*HP", size_part, re.I):
        m = re.search(r"(\d+)\s*HP", size_part, re.I)
        assert m
        hp_rows = [int(m.group(1))]
        meta["layout_explicit"] = False
    else:
        hp_rows = [1]
        meta["layout_unknown"] = True

    total = sum(hp_rows)
    meta["capacity"] = total
    return {"total_hp": total, "rows": len(hp_rows), "hp_per_row": hp_rows, "meta": meta}


def parse_year(build: str) -> int | None:
    m = re.search(r"\b((?:19|20)\d{2})\b", build)
    return int(m.group(1)) if m else None


def parse_price(build: str) -> dict[str, int]:
    prices: dict[str, int] = {}
    for pat, key in [
        (r"\$(\d[\d,]*)\s*official", "official_usd"),
        (r"\$(\d[\d,]*)\s*street", "street_usd"),
        (r"€(\d[\d,]*)", "official_eur"),
        (r"£(\d[\d,]*)", "official_gbp"),
    ]:
        m = re.search(pat, build, re.I)
        if m:
            prices[key] = int(m.group(1).replace(",", ""))
    return prices


def row_to_case(r: dict[str, str]) -> dict[str, Any]:
    layout = parse_layout(r["size_and_depth"], r["formats"])
    power = parse_amps_to_ma(r["power_and_bus"])
    meta = layout["meta"]
    meta["mounting"] = r["mounting"]
    meta["power_raw"] = r["power_and_bus"]
    meta["build_raw"] = r["build_price_year"]
    year = parse_year(r["build_price_year"])
    if year:
        meta["release_year"] = year
    prices = parse_price(r["build_price_year"])
    if prices:
        meta["pricing"] = prices
    powered = not bool(
        re.search(
            r"^None;|unpowered|no power",
            f"{r['power_and_bus']} {r['model']} {r['mounting']}",
            re.I,
        )
    )
    meta["powered"] = powered
    if re.search(r"diy|kit", r["model"], re.I):
        meta["kind"] = meta.get("kind", "kit")
    if re.search(r"\+/-?\s*15\s*V", r["power_and_bus"], re.I):
        meta["rail_voltage_nominal"] = "±15V"

    rec: dict[str, Any] = {
        "brand": r["manufacturer"].strip(),
        "name": r["model"].strip(),
        "total_hp": layout["total_hp"],
        "rows": layout["rows"],
        "hp_per_row": layout["hp_per_row"],
        "format_family": meta.get("format_family") or "Eurorack",
        "capacity_unit": meta.get("capacity_unit") or "hp",
        "powered": bool(meta.get("powered", True)),
        "power_12v_ma": power["power_12v_ma"],
        "power_neg12v_ma": power["power_neg12v_ma"],
        "power_5v_ma": power["power_5v_ma"],
        "description": f"{r['mounting']} · {meta.get('size_summary', '')}"[:2000],
        "manufacturer_url": None,
        "meta": meta,
        "source": SOURCE_LABEL,
        "source_reference": SOURCE_REF,
    }
    if rec["total_hp"] <= 0 or rec["rows"] <= 0:
        raise ValueError(f"invalid layout for {rec['brand']} {rec['name']}: {rec}")
    if len(rec["hp_per_row"]) != rec["rows"]:
        raise ValueError(f"hp_per_row/rows mismatch: {rec}")
    if sum(rec["hp_per_row"]) != rec["total_hp"]:
        raise ValueError(f"hp sum mismatch: {rec}")
    return rec


def parse_markdown(md: str) -> list[dict[str, Any]]:
    return [row_to_case(r) for r in _table_rows(md)]


def build_fixture(md_path: Path) -> dict[str, Any]:
    md = md_path.read_text(encoding="utf-8")
    cases = parse_markdown(md)
    return {
        "fixture_version": "1.0",
        "name": "Modular cases research ingest — Cases4PatchHive",
        "source_document": str(md_path.as_posix()),
        "source_note": (
            "Parsed from research master table. Eurorack HP is primary; non-Eurorack "
            "formats store capacity in total_hp/hp_per_row with meta.capacity_unit. "
            "Unspecified rails remain null."
        ),
        "case_count": len(cases),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=DEFAULT_MD)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)
    if not args.input.is_file():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1
    fixture = build_fixture(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {fixture['case_count']} cases → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
