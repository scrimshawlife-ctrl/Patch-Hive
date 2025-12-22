import hashlib, json, os, time
from typing import Dict

def _sha256_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()

def package_patch(payload: Dict) -> Dict:
    patch = payload.get("patch") or {}
    meta = payload.get("metadata") or {}

    bundle = {
        "patch": patch,
        "metadata": meta,
        "packaged_at_unix": int(time.time())
    }
    blob = json.dumps(bundle, sort_keys=True).encode("utf-8")
    h = _sha256_bytes(blob)

    out_path = f"/tmp/patch_hive_bundle_{h.replace(':','_')}.json"
    with open(out_path, "wb") as f:
        f.write(blob)

    return {"bundle_path": out_path, "bundle_hash": h}

def index_library(payload: Dict) -> Dict:
    lib = payload["library_path"]
    items = []
    if os.path.isdir(lib):
        for fn in sorted(os.listdir(lib)):
            if fn.endswith(".json"):
                items.append({"file": fn})
    return {"count": len(items), "index": items}
