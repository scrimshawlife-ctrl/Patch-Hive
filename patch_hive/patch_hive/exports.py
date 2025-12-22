# Patch-Hive — Explicit Function Exports (Canonical)
# Role: preset/patch library operations + sharing mechanics (non-networked by default)

EXPORTS = [
  {
    "id": "patch_hive.op.package_patch.v1",
    "name": "Package Patch Preset",
    "kind": "overlay_op",
    "version": "1.0.0",
    "owner": "patch_hive",
    "rune": "ᛈᚻ",
    "entrypoint": "patch_hive.logic:package_patch",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "patch": {"type": "object"},
        "metadata": {"type": "object"},
        "seed": {"type": "integer"}
      },
      "required": ["patch", "metadata"],
      "additionalProperties": true
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "bundle_path": {"type": "string"},
        "bundle_hash": {"type": "string"}
      },
      "required": ["bundle_path", "bundle_hash"]
    },
    "capabilities": ["cpu", "disk_write", "no_net"],
    "cost_hint": {"ms_p50": 20, "ms_p95": 80},
    "provenance": {
      "repo": "patch_hive",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  },
  {
    "id": "patch_hive.op.index_library.v1",
    "name": "Index Patch Library",
    "kind": "overlay_op",
    "version": "1.0.0",
    "owner": "patch_hive",
    "rune": "ᛁᚾᛞ",
    "entrypoint": "patch_hive.logic:index_library",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "library_path": {"type": "string"}
      },
      "required": ["library_path"],
      "additionalProperties": false
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "count": {"type": "number"},
        "index": {"type": "array"}
      },
      "required": ["count", "index"]
    },
    "capabilities": ["cpu", "disk_read", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 30, "ms_p95": 140},
    "provenance": {
      "repo": "patch_hive",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  }
]
