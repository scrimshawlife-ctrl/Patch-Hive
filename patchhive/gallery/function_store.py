from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from patchhive.schemas_gallery import (
    FunctionRegistry,
    FunctionDef,
    FieldMeta,
    FieldStatus,
    Provenance,
    ProvenanceType,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta(method: str, evidence_ref: str, ptype: ProvenanceType) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(type=ptype, timestamp=_now_utc(), evidence_ref=evidence_ref, method=method)
        ],
        confidence=0.85,
        status=FieldStatus.inferred,
    )


class FunctionRegistryStore:
    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.path = self.root / "function_registry.json"
        self.root.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            self._reg = FunctionRegistry.model_validate_json(
                self.path.read_text(encoding="utf-8")
            )
        else:
            self._reg = FunctionRegistry(meta=_meta("init", "local", ProvenanceType.derived))
            self._flush()

    def _flush(self) -> None:
        self.path.write_text(
            json.dumps(self._reg.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def get(self) -> FunctionRegistry:
        return self._reg

    def lookup_alias(self, label: str) -> str | None:
        if not label:
            return None
        key = label.strip().lower()
        return self._reg.alias_index.get(key)

    def upsert_function(self, fn: FunctionDef) -> None:
        self._reg.functions[fn.function_id] = fn
        for a in fn.aliases + [fn.display_name]:
            if a:
                self._reg.alias_index[a.strip().lower()] = fn.function_id
        self._flush()

    def ensure_unknown(self, label: str, direction: str, signal_kind: str, *, evidence_ref: str) -> str:
        """
        If a proprietary jack name appears, create a normalized placeholder function id.
        Deterministic ID: fn.unknown.<hash8>
        """
        existing = self.lookup_alias(label)
        if existing:
            return existing

        import hashlib

        h = hashlib.sha256(f"{label}|{direction}|{signal_kind}".encode("utf-8")).hexdigest()[:8]
        fid = f"fn.unknown.{h}"

        fn = FunctionDef(
            function_id=fid,
            display_name=label.strip()[:48] or f"Unknown {h}",
            aliases=[label.strip()[:64]],
            signal_kind=signal_kind,
            direction=direction,
            notes="Auto-added unknown/proprietary jack. Needs review to map to a known function.",
            meta=_meta("ensure_unknown", evidence_ref, ProvenanceType.vision),
        )
        self.upsert_function(fn)
        return fid
