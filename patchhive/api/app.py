from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.pipeline.run_e2e_to_store import run_e2e_to_store
from patchhive.pipeline.run_e2e_with_progress import run_e2e_with_progress
from patchhive.store.artifact_store import ArtifactStore
from patchhive.store.job_store import JobStore, JobState, JobStatus, _now_utc
from patchhive.export.export_bundle_zip import build_bundle_zip
from patchhive.ops.build_ux_view import build_ux_view

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


app = FastAPI(title="PatchHive API", version="0.2.0")

# configure roots (swap for env vars in real deployment)
STORE_ROOT = "./.patchhive_store"
GALLERY_ROOT = "./.patchhive_gallery"

store = ArtifactStore(STORE_ROOT)
jobs = JobStore(STORE_ROOT)
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


# ============================================================
# V2 Endpoints: Jobs + Progress + Bundle Download
# ============================================================


@app.post("/v2/rigs/{rig_id}/ingest-image")
async def ingest_image_v2(
    rig_id: str,
    file: UploadFile = File(...),
    preset: str = "core",
):
    """
    Upload a rack image and run the full pipeline with job tracking.
    Returns run_id, job state, and summary. Idempotent: returns cached result if already built.
    """
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
        interactive_pdf=True,
    )

    refs = store.alloc_run(rig_id=rig_id, image_ref=str(img_path), preset=preset)

    # Idempotency: if already built, return immediately
    if store.exists(refs):
        st = jobs.read(refs.run_id) or JobState(
            run_id=refs.run_id, status=JobStatus.succeeded, stage="cached", progress=1.0
        )
        jobs.write(st)
        summary_path = refs.root / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
        return JSONResponse({"run_id": refs.run_id, "cached": True, "job": st.to_dict(), "summary": summary})

    # Create job record
    st = JobState(run_id=refs.run_id, status=JobStatus.running, stage="start", progress=0.0, started_at=_now_utc())
    jobs.write(st)

    def on_progress(stage: str, p: float):
        st2 = JobState(
            run_id=refs.run_id, status=JobStatus.running, stage=stage, progress=p, started_at=st.started_at
        )
        jobs.write(st2)

    # Run synchronously (v1). Later: push into a worker queue.
    try:
        store.write_input(refs, {"rig_id": rig_id, "image_ref": str(img_path), "config": cfg.model_dump()})
        cfg2 = cfg.model_copy(update={"out_dir": str(refs.root)})

        on_progress("running_pipeline", 0.05)
        _ = run_e2e_with_progress(
            image_ref=str(img_path),
            rig_id=rig_id,
            config=cfg2,
            gemini=gemini,
            on_progress=on_progress,
        )

        st_ok = JobState(
            run_id=refs.run_id,
            status=JobStatus.succeeded,
            stage="done",
            progress=1.0,
            started_at=st.started_at,
            finished_at=_now_utc(),
        )
        jobs.write(st_ok)

        summary_path = refs.root / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
        return JSONResponse({"run_id": refs.run_id, "cached": False, "job": st_ok.to_dict(), "summary": summary})
    except Exception as e:
        st_fail = JobState(
            run_id=refs.run_id,
            status=JobStatus.failed,
            stage="failed",
            progress=st.progress,
            started_at=st.started_at,
            finished_at=_now_utc(),
            error=str(e),
        )
        jobs.write(st_fail)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/runs/{run_id}/job")
def get_job(run_id: str):
    """
    Get the current job state (status, stage, progress).
    """
    st = jobs.read(run_id)
    if not st:
        raise HTTPException(status_code=404, detail="job not found")
    return JSONResponse(st.to_dict())


@app.get("/v2/runs/{run_id}/download/bundle.zip")
def download_bundle(run_id: str):
    """
    Download a ZIP bundle containing all artifacts:
    - rigspec.json
    - library.json
    - manifest.json
    - summary.json
    - pdf/patchbook.pdf
    - svgs/*.svg
    """
    run_root = Path(STORE_ROOT) / "runs" / run_id
    if not run_root.exists():
        raise HTTPException(status_code=404, detail="run not found")

    zdir = run_root / "bundle"
    zdir.mkdir(parents=True, exist_ok=True)
    zpath = zdir / "patchhive_bundle.zip"

    build_bundle_zip(str(run_root), str(zpath))

    return FileResponse(str(zpath), media_type="application/zip", filename=f"patchhive_{run_id}_bundle.zip")


# ============================================================
# V3 Endpoints: UX Library View
# ============================================================


@app.get("/v3/runs/{run_id}/library")
def get_library_view(run_id: str):
    """
    Get a UX-friendly view of the patch library with sorting, categorization, and download links.
    Returns structured data for frontend consumption with filters and exports.
    """
    run_root = Path(STORE_ROOT) / "runs" / run_id
    if not run_root.exists():
        raise HTTPException(status_code=404, detail="run not found")

    ux = build_ux_view(run_root=str(run_root), run_id=run_id)
    return JSONResponse(ux.model_dump())
