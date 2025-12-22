from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.pipeline.run_e2e_to_store import run_e2e_to_store
from patchhive.store.artifact_store import ArtifactStore

from patchhive.vision.gemini_interface import GeminiVisionClient, VisionRigSpec


class GeminiOverlayClient(GeminiVisionClient):
    """
    Production: implement real Gemini call in overlay/service.
    Dev fallback: require that image filename includes a matching *.vision.json next to it.
    """
    def extract_rig(self, image_ref: str, *, rig_id: str) -> VisionRigSpec:
        # DEV behavior: look for "<image_ref>.vision.json"
        p = Path(image_ref)
        vp = p.with_suffix(p.suffix + ".vision.json")
        if not vp.exists():
            raise RuntimeError("GeminiOverlayClient dev mode requires a sidecar .vision.json file.")
        data = json.loads(vp.read_text(encoding="utf-8"))
        data["rig_id"] = rig_id
        data["evidence_ref"] = data.get("evidence_ref", f"image:{image_ref}")
        return VisionRigSpec.model_validate(data)


app = FastAPI(title="PatchHive API", version="0.1.0")

# configure roots (swap for env vars in real deployment)
STORE_ROOT = "./.patchhive_store"
GALLERY_ROOT = "./.patchhive_gallery"

store = ArtifactStore(STORE_ROOT)
gemini = GeminiOverlayClient()


@app.post("/v1/rigs/{rig_id}/ingest-image")
async def ingest_image(
    rig_id: str,
    file: UploadFile = File(...),
    preset: str = "core",
):
    """
    Upload a rack image and run the full pipeline -> returns run_id and summary.
    """
    # save upload
    uploads = Path(STORE_ROOT) / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    img_path = uploads / f"{rig_id}.{file.filename}"
    img_path.write_bytes(await file.read())

    cfg = E2EConfig(
        gallery_root=GALLERY_ROOT,
        out_dir="(overridden by store)",
        preset=preset,
        rows=1,
        row_hp=104,
        max_total=160,
        max_per_category=70,
        drop_runaway=True,
        drop_silence=False,
    )

    try:
        out = run_e2e_to_store(
            store=store,
            gemini=gemini,
            rig_id=rig_id,
            image_ref=str(img_path),
            cfg=cfg,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # return summary (read from disk)
    run_id = out["run_id"]
    summary_path = Path(STORE_ROOT) / "runs" / run_id / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    return JSONResponse({"run_id": run_id, "summary": summary})


@app.get("/v1/runs/{run_id}/summary")
def get_summary(run_id: str):
    p = Path(STORE_ROOT) / "runs" / run_id / "summary.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="run not found")
    return JSONResponse(json.loads(p.read_text(encoding="utf-8")))


@app.get("/v1/runs/{run_id}/manifest")
def get_manifest(run_id: str):
    p = Path(STORE_ROOT) / "runs" / run_id / "manifest.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="manifest not found")
    return JSONResponse(json.loads(p.read_text(encoding="utf-8")))


@app.get("/v1/runs/{run_id}/download/pdf")
def download_pdf(run_id: str):
    p = Path(STORE_ROOT) / "runs" / run_id / "pdf" / "patchbook.pdf"
    if not p.exists():
        raise HTTPException(status_code=404, detail="pdf not found")
    return FileResponse(str(p), media_type="application/pdf", filename=f"patchhive_{run_id}.pdf")


@app.get("/v1/runs/{run_id}/download/library.json")
def download_library(run_id: str):
    p = Path(STORE_ROOT) / "runs" / run_id / "json" / "library.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="library.json not found")
    return FileResponse(str(p), media_type="application/json", filename=f"patchhive_{run_id}_library.json")


@app.get("/v1/runs/{run_id}/svgs/{patch_id}.svg")
def get_patch_svg(run_id: str, patch_id: str):
    p = Path(STORE_ROOT) / "runs" / run_id / "svgs" / f"{patch_id}.svg"
    if not p.exists():
        raise HTTPException(status_code=404, detail="svg not found")
    return FileResponse(str(p), media_type="image/svg+xml", filename=f"{patch_id}.svg")
