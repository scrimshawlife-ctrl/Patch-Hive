"""FastAPI routes for patch generation runs."""
from core import get_db
from runs.models import Run
from patches.models import Patch
from patches.routes import build_patch_response
from .schemas import RunListResponse, RunPatchesResponse, RunResponse
router = APIRouter()


@router.get("/", response_model=RunListResponse)
def list_runs(
    rack_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    runs = db.query(Run).filter(Run.rack_id == rack_id).order_by(Run.created_at.desc()).all()
    return RunListResponse(total=len(runs), runs=runs)

@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):

@router.get("/{run_id}/patches", response_model=RunPatchesResponse)
def get_run_patches(run_id: int, db: Session = Depends(get_db)):
