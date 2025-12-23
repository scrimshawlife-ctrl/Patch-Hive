def validate_patch(payload: dict) -> dict:
    # Minimal structural checks (real schema enforcement can come next)
    errors = []
    if not isinstance(payload.get("modules"), list):
        errors.append("modules must be an array")
    if not isinstance(payload.get("cables"), list):
        errors.append("cables must be an array")
    ok = len(errors) == 0
    return {"ok": ok, "errors": errors, "warnings": []}

def extract_metrics(payload: dict) -> dict:
    modules = payload.get("modules") or []
    cables = payload.get("cables") or []

    # Minimal starter metrics; expand with your Patch Diagram Schema
    metrics = {
        "module_count": len(modules),
        "cable_count": len(cables),
        "avg_degree": (2 * len(cables) / len(modules)) if modules else 0.0
    }
    return {"metrics": metrics}
