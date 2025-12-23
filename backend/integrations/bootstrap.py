"""
PatchHive First-Run Bootstrap System

Detects empty database and offers guided setup with data population.
ABX-Core v1.3 compliant with full provenance tracking.
"""

import sys
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from cases.models import Case
from core.database import SessionLocal
from integrations.modulargrid_importer import import_all
from modules.models import Module


def check_database_state(db: Session) -> Dict[str, Any]:
    """
    Check if database has been bootstrapped.

    Returns:
        Dict with database state information
    """
    module_count = db.query(Module).count()
    case_count = db.query(Case).count()

    has_modulargrid_data = db.query(Module).filter(Module.source == "ModularGrid").count() > 0

    return {
        "is_empty": module_count == 0 and case_count == 0,
        "has_data": module_count > 0 or case_count > 0,
        "module_count": module_count,
        "case_count": case_count,
        "has_modulargrid_data": has_modulargrid_data,
        "needs_bootstrap": module_count == 0,
    }


def print_bootstrap_banner():
    """Print PatchHive bootstrap welcome banner."""
    print(
        """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🎛️  PATCHHIVE DATABASE BOOTSTRAP  🎛️                ║
║                                                                   ║
║                    ABX-Core v1.3 Compliant                        ║
║                   Eurorack Module Database                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    )


def print_database_status(state: Dict[str, Any]):
    """Print current database status."""
    print("\n📊 Current Database Status:\n")
    print(f"  Modules:  {state['module_count']}")
    print(f"  Cases:    {state['case_count']}")

    if state["has_modulargrid_data"]:
        print(f"  Source:   ModularGrid data present ✓")

    print()


def interactive_bootstrap(db: Session) -> bool:
    """
    Run interactive bootstrap wizard.

    Returns:
        True if bootstrap completed successfully
    """
    print_bootstrap_banner()

    state = check_database_state(db)

    if state["has_data"]:
        print("✓ Database already populated!")
        print_database_status(state)

        response = input("Do you want to re-import or add more data? (y/N): ").strip().lower()
        if response != "y":
            print("\n✓ Keeping existing data. Exiting bootstrap.\n")
            return False
    else:
        print("⚠ Empty database detected - first run!\n")

    print("PatchHive can populate your database with curated Eurorack module data.\n")
    print("📦 Available data sources:\n")
    print("  1. ModularGrid Curated Set (recommended)")
    print("     - 32 real modules from 13 top manufacturers")
    print("     - 7 professional cases")
    print("     - 25 tracked brands")
    print("     - Full provenance tracking")
    print("     - ~2 seconds to import\n")
    print("  2. Skip (leave database empty)")
    print("     - Manually add modules later via API")
    print("     - Or provide your own data files\n")

    response = input("Choose option (1/2) [1]: ").strip() or "1"

    if response == "1":
        print("\n🚀 Starting ModularGrid data import...\n")

        try:
            result = import_all(db, clear_existing=False)

            print("\n✅ Import successful!\n")
            print(f"  Modules imported: {result['modules']['imported']}")
            print(f"  Cases imported:   {result['cases']['imported']}")
            print(f"  Provenance ID:    {result['provenance']['run_id']}\n")

            print("📚 Documentation created:")
            print("  - backend/DATA_SOURCES.md")
            print("  - backend/BOOTSTRAP_LOG.md\n")

            print("🎉 PatchHive is ready to use!")
            print("   Access API docs at: http://localhost:8000/docs\n")

            return True

        except Exception as e:
            print(f"\n❌ Import failed: {str(e)}\n")
            print("You can retry later with:")
            print("  python -m integrations.modulargrid_importer\n")
            return False

    elif response == "2":
        print("\n✓ Skipping automatic import.")
        print("\nTo populate later, use:")
        print("  python -m integrations.modulargrid_importer")
        print("\nOr via API:")
        print("  POST http://localhost:8000/api/modulargrid/import/all\n")
        return False

    else:
        print("\n⚠ Invalid option. Exiting.\n")
        return False


def silent_bootstrap(db: Session, force: bool = False) -> Optional[Dict[str, Any]]:
    """
    Non-interactive bootstrap (for automated environments).

    Args:
        db: Database session
        force: If True, import even if data exists

    Returns:
        Import result dict or None if skipped
    """
    state = check_database_state(db)

    if state["needs_bootstrap"] or force:
        print("🔄 Auto-bootstrapping database with ModularGrid data...")
        result = import_all(db, clear_existing=force)
        print(
            f"✅ Imported {result['modules']['imported']} modules, {result['cases']['imported']} cases"
        )
        return result
    else:
        print(f"✓ Database already populated ({state['module_count']} modules)")
        return None


def main():
    """
    Main entry point for bootstrap script.

    Usage:
        python -m integrations.bootstrap              # Interactive mode
        python -m integrations.bootstrap --auto       # Silent auto-import
        python -m integrations.bootstrap --force      # Force re-import
    """
    import argparse

    parser = argparse.ArgumentParser(description="PatchHive Database Bootstrap Wizard")
    parser.add_argument("--auto", action="store_true", help="Automatic bootstrap (non-interactive)")
    parser.add_argument("--force", action="store_true", help="Force import even if data exists")

    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.auto:
            silent_bootstrap(db, force=args.force)
        else:
            interactive_bootstrap(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
