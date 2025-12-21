# PatchHive — Explicit Function Exports (Canonical)

EXPORTS = [
  {
    "id": "patchhive.op.validate_patch.v1",
    "name": "Validate Patch Diagram",
    "kind": "overlay_op",
    "version": "1.0.0",
    "owner": "patchhive",
    "rune": "ᛈᚺ",
    "entrypoint": "patchhive.logic:validate_patch",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "schema_version": {"type": "string"},
        "modules": {"type": "array"},
        "cables": {"type": "array"}
      },
      "required": ["schema_version", "modules", "cables"],
      "additionalProperties": true
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "ok": {"type": "boolean"},
        "errors": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["ok"]
    },
    "capabilities": ["cpu", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 4, "ms_p95": 20},
    "provenance": {
      "repo": "patchhive",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  },
  {
    "id": "patchhive.op.extract_metrics.v1",
    "name": "Extract Patch Metrics",
    "kind": "overlay_op",
    "version": "1.0.0",
    "owner": "patchhive",
    "rune": "ᛗᛖᛏ",
    "entrypoint": "patchhive.logic:extract_metrics",
    "inputs_schema": {
      "type": "object",
      "properties": {
        "schema_version": {"type": "string"},
        "modules": {"type": "array"},
        "cables": {"type": "array"}
      },
      "required": ["schema_version", "modules", "cables"],
      "additionalProperties": true
    },
    "outputs_schema": {
      "type": "object",
      "properties": {
        "metrics": {"type": "object"}
      },
      "required": ["metrics"]
    },
    "capabilities": ["cpu", "no_net", "read_only"],
    "cost_hint": {"ms_p50": 6, "ms_p95": 25},
    "provenance": {
      "repo": "patchhive",
      "commit": "PINNED",
      "artifact_hash": "PINNED",
      "generated_at": 0
    }
  }
]
