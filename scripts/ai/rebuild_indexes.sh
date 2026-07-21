#!/usr/bin/env bash
# Rebuild local AI codebase-memory indexes (ctags, file lists, module graph).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

mkdir -p .codebase-memory/{indexes,embeddings,graph,symbols,summaries}

echo "[index] ctags symbols..."
if command -v ctags >/dev/null 2>&1; then
  ctags -R \
    --languages=Python,JavaScript \
    --langmap=JavaScript:+.ts.tsx \
    --exclude=node_modules --exclude=.git --exclude=dist --exclude=.venv \
    --exclude='*.zip' \
    -f .codebase-memory/symbols/tags \
    backend frontend 2>/dev/null || true
  echo "[index] symbols: $(wc -l < .codebase-memory/symbols/tags | tr -d ' ') lines"
else
  echo "[index] ctags not installed; skip symbols"
fi

echo "[index] file inventories..."
if command -v fd >/dev/null 2>&1; then
  fd -t f -e py . backend > .codebase-memory/indexes/backend_py_files.txt || true
  fd -t f -e ts -e tsx . frontend/src > .codebase-memory/indexes/frontend_ts_files.txt || true
else
  find backend -name '*.py' > .codebase-memory/indexes/backend_py_files.txt || true
  find frontend/src \( -name '*.ts' -o -name '*.tsx' \) > .codebase-memory/indexes/frontend_ts_files.txt || true
fi

if command -v rg >/dev/null 2>&1; then
  rg -n "include_router|prefix=" backend/main.py > .codebase-memory/indexes/api_routers.txt || true
  rg -n "Route path=" frontend/src/App.tsx > .codebase-memory/indexes/fe_routes.txt || true
  rg -n "TODO|FIXME|XXX|HACK" backend frontend \
    --glob '!node_modules' --glob '!.git' --glob '!package-lock.json' \
    > .codebase-memory/indexes/todo_hotspots.txt || true
fi

echo "[index] module graph + hashes..."
python3 <<'PY'
import json, pathlib, re, hashlib
from datetime import datetime, timezone
root = pathlib.Path(".")
backend = root / "backend"
backend_pkgs = sorted(
    p.name
    for p in backend.iterdir()
    if p.is_dir()
    and not p.name.startswith((".", "_"))
    and p.name not in {"tests", "alembic", "__pycache__"}
)
fe_areas = sorted(p.name for p in (root / "frontend/src").iterdir() if p.is_dir())
edges = []
for py in backend.rglob("*.py"):
    if "tests" in py.parts or "__pycache__" in py.parts:
        continue
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    rel = py.relative_to(backend)
    pkg = rel.parts[0] if len(rel.parts) > 1 else py.stem
    for m in re.finditer(r"^(?:from|import)\s+([a-zA-Z0-9_]+)", text, re.M):
        target = m.group(1)
        if target in backend_pkgs and target != pkg:
            edges.append({"from": pkg, "to": target})
seen = set()
uniq = []
for e in edges:
    k = (e["from"], e["to"])
    if k not in seen:
        seen.add(k)
        uniq.append(e)
graph = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "backend_packages": backend_pkgs,
    "frontend_src_areas": fe_areas,
    "backend_import_edges": sorted(uniq, key=lambda x: (x["from"], x["to"])),
    "entry_points": {
        "backend": "backend/main.py",
        "frontend": "frontend/src/App.tsx",
        "docker": "docker-compose.yml",
        "makefile": "Makefile",
        "justfile": "justfile",
    },
    "symbol_index": ".codebase-memory/symbols/tags",
}
(root / ".codebase-memory/graph/module_graph.json").write_text(
    json.dumps(graph, indent=2), encoding="utf-8"
)
summary = {
    "product": "PatchHive",
    "identity": "Deterministic rig-intelligence and Patch Book publishing — no audio DSP/hardware control",
    "stack": {
        "backend": "FastAPI+SQLAlchemy+Alembic",
        "frontend": "React+Vite+TS",
        "db": "PostgreSQL",
    },
    "canonical_domain": "backend/canon",
    "visual_intelligence": "backend/evidence",
    "authority_docs": [
        "CURRENT_STATE.md",
        "docs/CANON.md",
        "docs/CONTINUATION.md",
        "docs/VISUAL_SYSTEM_INTELLIGENCE.md",
        "SYSTEM_CONTEXT.md",
        "AI_CONTEXT.md",
    ],
}
(root / ".codebase-memory/summaries/architecture_summary.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
emb = {"status": "hash_index_only", "files": []}
for rel in [
    "backend/main.py",
    "backend/canon/contracts.py",
    "backend/evidence/vision_provider.py",
    "frontend/src/App.tsx",
    "CURRENT_STATE.md",
    "SYSTEM_CONTEXT.md",
    "AI_CONTEXT.md",
]:
    p = root / rel
    if p.exists():
        emb["files"].append(
            {"path": rel, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        )
(root / ".codebase-memory/embeddings/content_hashes.json").write_text(
    json.dumps(emb, indent=2), encoding="utf-8"
)
print("[index] graph edges:", len(uniq))
print("[index] done")
PY

echo "[index] complete → .codebase-memory/"
