"""
API endpoints for ModularGrid integration.

ABX-Core v1.3: Full provenance tracking for all import operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from core.database import get_db
from integrations.modulargrid_importer import (
    import_modules,
    import_cases,
    import_all,
    get_manufacturers_list,
)

router = APIRouter(prefix="/modulargrid", tags=["modulargrid"])


@router.post("/import/modules")
def import_modulargrid_modules(
    clear_existing: bool = False,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import modules from ModularGrid database.

    Args:
        clear_existing: If True, clear existing ModularGrid-sourced modules first
        db: Database session

    Returns:
        Import statistics with provenance
    """
    try:
        result = import_modules(db, clear_existing)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/cases")
def import_modulargrid_cases(
    clear_existing: bool = False,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import cases from ModularGrid database.

    Args:
        clear_existing: If True, clear existing ModularGrid-sourced cases first
        db: Database session

    Returns:
        Import statistics with provenance
    """
    try:
        result = import_cases(db, clear_existing)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/all")
def import_all_modulargrid_data(
    clear_existing: bool = False,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import all ModularGrid data (modules and cases).

    Args:
        clear_existing: If True, clear existing ModularGrid data first
        db: Database session

    Returns:
        Combined import statistics with provenance
    """
    try:
        result = import_all(db, clear_existing)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/manufacturers")
def list_manufacturers() -> Dict[str, Any]:
    """
    Get list of all manufacturers in the ModularGrid database.

    Returns:
        List of manufacturer names
    """
    return {
        "manufacturers": get_manufacturers_list(),
        "count": len(get_manufacturers_list()),
    }
