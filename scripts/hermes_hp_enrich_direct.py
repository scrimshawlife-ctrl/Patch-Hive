#!/usr/bin/env python3
"""HP enrichment via direct HTTP (no Firecrawl) — official + Perfect Circuit pages.

Used when Firecrawl credits are exhausted. Never invents HP. OBSERVED only.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

HP_PATTERNS = [
    re.compile(r"\b(\d{1,2})\s*(?:TE\s*/\s*)?[Hh][Pp]\b"),
    re.compile(r"\b[Ww]idth\s*[:\-]?\s*(\d{1,2})\s*[Hh][Pp]\b"),
    re.compile(r"\b[Hh][Pp]\s*[:\-/]?\s*(\d{1,2})\b"),
    re.compile(r"\b(\d{1,2})\s*TE\b"),  # Doepfer German TE = HP
    re.compile(r"Breite/Width:\s*(\d+)\s*TE", re.I),
]


def fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            # try encodings
            for enc in ("utf-8", "latin-1", "iso-8859-1"):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  fetch fail {url}: {e}")
        return ""


def extract_hp(text: str) -> int | None:
    """Extract module width HP; skip false positives like '2hp Power consumption'."""
    text = text or ""
    # Strong patterns first
    strong = [
        re.compile(r"Breite/Width:\s*(\d+)\s*TE\s*/\s*(\d+)\s*HP", re.I),
        re.compile(r"Width:\s*(\d+)\s*HP", re.I),
        re.compile(r"Eurorack\s*Width:\s*(\d+)\s*HP", re.I),
        re.compile(r"Occupies\s*(\d+)\s*HP", re.I),
        re.compile(r"\bHP\s+(\d+)\b"),
        re.compile(r"\b(\d+)\s*HP\s+\d+\s*mm\s+deep", re.I),
        re.compile(r"Dimensions\s+(\d+)\s*HP", re.I),
        re.compile(r"Breite/Width:\s*(\d+)\s*TE", re.I),
    ]
    for pat in strong:
        m = pat.search(text)
        if not m:
            continue
        # last group is usually HP when two groups
        try:
            hp = int(m.group(m.lastindex or 1))
        except ValueError:
            continue
        if 1 <= hp <= 42:
            return hp

    for pat in HP_PATTERNS:
        for m in pat.finditer(text):
            try:
                hp = int(m.group(1))
            except ValueError:
                continue
            if not (1 <= hp <= 42):
                continue
            ctx = text[max(0, m.start() - 25) : m.end() + 40].lower()
            # reject power-draw false positives
            if "power" in ctx or "consumption" in ctx or "ma " in ctx or "ma+" in ctx:
                continue
            if "pulse width" in ctx or "pulsewidth" in ctx:
                continue
            return hp
    return None


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def candidate_urls(brand: str, name: str) -> list[tuple[str, str]]:
    n = slugify(name)
    urls: list[tuple[str, str]] = []

    if brand == "Doepfer":
        # A-101-1 → a1011.htm ; A-110 → a110.htm ; A-118-2 → a1182.htm
        m = re.match(r"A-?(\d+)(?:-(\d+))?", name.strip(), re.I)
        if m:
            a, b = m.group(1), m.group(2)
            if b:
                code = f"a{a}{b}"
            else:
                code = f"a{a}"
            urls.append((f"https://doepfer.de/{code}.htm", "official"))
            urls.append((f"https://www.doepfer.de/{code}.htm", "official"))
            # alt with underscore
            if b:
                urls.append((f"https://doepfer.de/a{a}_{b}.htm", "official"))
        urls.append((f"https://www.perfectcircuit.com/doepfer-{n}.html", "retailer"))
        # PC often uses a101-1 style
        if m:
            a, b = m.group(1), m.group(2)
            if b:
                urls.append(
                    (f"https://www.perfectcircuit.com/doepfer-a{a}-{b}.html", "retailer")
                )
                urls.append(
                    (f"https://www.perfectcircuit.com/doepfer-a{a}{b}.html", "retailer")
                )
            else:
                urls.append(
                    (f"https://www.perfectcircuit.com/doepfer-a{a}.html", "retailer")
                )
        urls.append((f"https://www.thomann.de/intl/doepfer_{n.replace('-', '_')}.htm", "retailer"))
        urls.append((f"https://www.thomannmusic.com/doepfer_{n.replace('-', '_')}.htm", "retailer"))

    elif brand == "ADDAC System":
        m = re.search(r"ADDAC\s*(\d+)", name, re.I)
        if m:
            code = m.group(1)
            urls.append(
                (
                    f"https://www.addacsystem.com/en/products/modules/addac{code[0]}00-series/addac{code}",
                    "official",
                )
            )
            # try series buckets 100, 200, 300, 500, 600, 800
            series = f"addac{code[0]}00-series" if code else "addac100-series"
            urls.append(
                (
                    f"https://www.addacsystem.com/en/products/modules/{series}/addac{code}",
                    "official",
                )
            )
            for s in ("100", "200", "300", "500", "600", "700", "800"):
                urls.append(
                    (
                        f"https://www.addacsystem.com/en/products/modules/addac{s}-series/addac{code}",
                        "official",
                    )
                )
            urls.append(
                (f"https://www.perfectcircuit.com/addac-{code}.html", "retailer")
            )
            urls.append(
                (f"https://www.perfectcircuit.com/addac-system-addac{code}.html", "retailer")
            )
            urls.append(
                (f"https://www.perfectcircuit.com/addac{code}.html", "retailer")
            )

    elif brand == "Cwejman":
        # cwejmanmusic.com product pages
        urls.append((f"https://www.cwejmanmusic.com/{n}", "official"))
        urls.append((f"https://cwejmanmusic.com/{n}", "official"))
        urls.append((f"https://www.perfectcircuit.com/cwejman-{n}.html", "retailer"))
        urls.append((f"https://schneidersladen.de/en/cwejman-music-{n}", "retailer"))
        urls.append((f"https://schneidersladen.de/en/cwejman-{n}", "retailer"))

    elif brand == "Dreadbox":
        # strip version suffixes for slug
        base = re.sub(r"-?\d+\.\d+$", "", n)
        base = re.sub(r"-1u.*$", "", base)
        base = re.sub(r"-silver.*$|-black.*$", "", base)
        base = base.strip("-")
        urls.append((f"https://www.dreadbox-fx.com/product/{base}/", "official"))
        urls.append((f"https://www.dreadbox-fx.com/product/{n}/", "official"))
        urls.append((f"https://www.dreadbox-fx.com/{base}/", "official"))
        # Schneidersladen often works when PC 403s
        urls.append((f"https://schneidersladen.de/en/dreadbox-{base}", "retailer"))
        urls.append((f"https://schneidersladen.de/en/dreadbox-{n}", "retailer"))
        urls.append((f"https://www.thomann.de/intl/dreadbox_{base.replace('-', '_')}.htm", "retailer"))
        urls.append((f"https://www.perfectcircuit.com/dreadbox-{base}.html", "retailer"))
        urls.append((f"https://www.perfectcircuit.com/dreadbox-{n}.html", "retailer"))

    # ModularGrid product pages as last resort (community catalog dimensions)
    # Prefer exact module page patterns used by MG slugs
    mg_brand = {
        "Doepfer": "doepfer",
        "ADDAC System": "addac-system",
        "Cwejman": "cwejman",
        "Dreadbox": "dreadbox",
    }.get(brand)
    if mg_brand:
        if brand == "Doepfer":
            m = re.match(r"A-?(\d+)(?:-(\d+))?", name.strip(), re.I)
            if m:
                a, b = m.group(1), m.group(2)
                if b:
                    urls.append(
                        (f"https://modulargrid.net/e/doepfer-a-{a}-{b}-", "modulargrid")
                    )
                    urls.append(
                        (f"https://modulargrid.net/e/doepfer-a-{a}-{b}", "modulargrid")
                    )
                urls.append((f"https://modulargrid.net/e/doepfer-a-{a}", "modulargrid"))
                urls.append((f"https://modulargrid.net/e/doepfer-a-{a}-", "modulargrid"))
        elif brand == "ADDAC System":
            m = re.search(r"ADDAC\s*(\d+)", name, re.I)
            if m:
                code = m.group(1)
                urls.append(
                    (
                        f"https://modulargrid.net/e/addac-system-addac{code}-wav-player",
                        "modulargrid",
                    )
                )
                urls.append(
                    (f"https://modulargrid.net/e/addac-system-addac{code}", "modulargrid")
                )
                urls.append(
                    (
                        f"https://modulargrid.net/e/addac-system-addac{code}-",
                        "modulargrid",
                    )
                )
        elif brand == "Cwejman":
            urls.append((f"https://modulargrid.net/e/cwejman-{n}", "modulargrid"))
            urls.append((f"https://modulargrid.net/e/cwejman-{n}-", "modulargrid"))
        elif brand == "Dreadbox":
            base = re.sub(r"-?\d+\.\d+$", "", n)
            base = re.sub(r"-1u.*$|-silver.*$|-black.*$", "", base).strip("-")
            urls.append((f"https://modulargrid.net/e/dreadbox-{base}", "modulargrid"))
            urls.append((f"https://modulargrid.net/e/dreadbox-{n}", "modulargrid"))

    # de-dupe
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for u, k in urls:
        if u not in seen:
            seen.add(u)
            out.append((u, k))
    return out


def process_one(target: dict, sleep_s: float) -> dict:
    brand = target["brand"]
    name = target["name"]
    slug = target["slug"]
    print(f"→ {brand} / {name}", flush=True)

    for url, kind in candidate_urls(brand, name)[:10]:
        html = fetch(url)
        time.sleep(sleep_s)
        if not html or len(html) < 200:
            continue
        low_head = html[:800].lower()
        if "404" in low_head and "not found" in low_head:
            continue
        if "page not found" in low_head or "could not find" in low_head:
            continue
        # light name check for retailer / modulargrid pages
        token = re.sub(r"[^a-z0-9]+", "", name.lower())[:6]
        html_norm = re.sub(r"[^a-z0-9]+", "", html.lower())
        if kind in ("retailer", "modulargrid") and token and token not in html_norm:
            if brand == "Doepfer":
                m = re.match(r"A-?(\d+)", name, re.I)
                if m and m.group(1) not in html_norm:
                    continue
            elif brand == "ADDAC System":
                m = re.search(r"(\d{3})", name)
                if m and m.group(1) not in html:
                    continue
            else:
                continue
        hp = extract_hp(html)
        if hp is None:
            continue
        # Cwejman squarespace often shows a bogus "2hp" power chip — skip weak 2HP
        if brand == "Cwejman" and hp == 2 and kind == "official":
            if not re.search(r"Dimensions\s+2\s*HP|Width:\s*2\s*HP|Occupies\s*2\s*HP", html, re.I):
                continue
        # ModularGrid: require Dimensions / depth pattern
        if kind == "modulargrid":
            if not (
                re.search(rf"Dimensions\s+{hp}\s*HP", html, re.I)
                or re.search(rf"{hp}\s*HP\s+\d+\s*mm\s+deep", html, re.I)
            ):
                continue
        return {
            "brand": brand,
            "name": name,
            "slug": slug,
            "hp": hp,
            "source_url": url,
            "provenance": "OBSERVED",
            "status": "found",
            "notes": f"source_class={kind};method=direct_http",
        }

    return {
        "brand": brand,
        "name": name,
        "slug": slug,
        "hp": None,
        "source_url": None,
        "provenance": "NOT_COMPUTABLE",
        "status": "not_found",
        "notes": "no HP via direct HTTP candidates",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)

    payload = json.loads(args.targets.read_text(encoding="utf-8"))
    targets = list(payload.get("targets") or [])
    if args.limit:
        targets = targets[: args.limit]

    done: dict[str, dict] = {}
    if args.resume and args.out.is_file():
        prev = json.loads(args.out.read_text(encoding="utf-8"))
        for r in prev.get("results") or []:
            if r.get("slug"):
                done[r["slug"]] = r
        print(f"resume: {len(done)} already done")

    results: list[dict[str, Any]] = []
    for t in targets:
        slug = t.get("slug")
        if slug in done:
            results.append(done[slug])
            continue
        r = process_one(t, args.sleep)
        results.append(r)
        print(f"  {r['status']} hp={r.get('hp')} {r.get('source_url')}", flush=True)
        found = sum(1 for x in results if x.get("status") == "found" and x.get("hp"))
        out = {
            "batch": payload.get("batch", 3),
            "generated_by": "hermes-direct-http-pipeline",
            "results": results,
            "summary": {
                "targets": len(targets),
                "processed": len(results),
                "found": found,
                "not_found": len(results) - found,
            },
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    found = sum(1 for r in results if r.get("status") == "found" and r.get("hp"))
    print(json.dumps({"targets": len(results), "found": found, "not_found": len(results) - found}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
