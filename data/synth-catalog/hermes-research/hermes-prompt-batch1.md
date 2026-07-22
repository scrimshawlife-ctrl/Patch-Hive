# Mission: PatchHive module_catalog HP enrichment (Batch 1)

You are filling **missing HP (Eurorack width)** for PatchHive's module catalog.
Targets file (read it): `/Users/appliedalchemylabs/Patch-Hive/data/synth-catalog/hermes-research/hp-enrichment-batch1.json`

## Hard rules
1. **Never invent** HP. Only record values you OBSERVE from:
   - Official manufacturer product pages / manuals
   - Perfect Circuit / Thomann product pages (retailer OBSERVED)
2. **Do not bulk-scrape ModularGrid** (ToS). Use it only as last-resort INFERRED and label provenance accordingly — prefer official/retailer.
3. Multi-source rotation: official → Perfect Circuit/Thomann → next brand.
4. If HP not found, include the row with `"hp": null, "status": "not_found"`.
5. Output **only** a JSON file written to:
   `/Users/appliedalchemylabs/Patch-Hive/data/synth-catalog/hermes-research/hp-enrichment-batch1-results.json`

## JSON schema (array under "results")
```json
{
  "batch": 1,
  "generated_by": "hermes",
  "results": [
    {
      "brand": "Make Noise",
      "name": "Maths",
      "slug": "make-noise-maths",
      "hp": 20,
      "source_url": "https://...",
      "provenance": "OBSERVED",
      "status": "found",
      "notes": "official product page"
    }
  ],
  "summary": {
    "targets": 0,
    "found": 0,
    "not_found": 0
  }
}
```

## Scope
Process **all targets** in the batch1 JSON (Acid Rain Technology, Mutable Instruments, Make Noise, Intellijel, Instruo, Noise Engineering — whichever appear).

## Skill
Use modular-synth-catalog-research protocol + web/firecrawl tools.

## Done criteria
- Results file exists and is valid JSON
- Each target has a result row (found or not_found)
- summary.found + summary.not_found == targets count
- Print a short summary of found counts by brand when finished
