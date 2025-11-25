"""
Rack validation logic - ensures modules fit in case and power constraints are met.
"""
from typing import List, Tuple
from sqlalchemy.orm import Session

from cases.models import Case
from modules.models import Module
from .schemas import RackModuleSpec, RackValidationError


def validate_rack_configuration(
    db: Session, case_id: int, modules: List[RackModuleSpec]
) -> Tuple[bool, List[RackValidationError]]:
    """
    Validate a rack configuration against case constraints.

    Returns:
        (is_valid, errors)
    """
    errors: List[RackValidationError] = []

    # Get case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        errors.append(
            RackValidationError(field="case_id", message=f"Case with id {case_id} not found")
        )
        return False, errors

    # Track HP usage per row
    hp_usage = {i: [False] * case.hp_per_row[i] for i in range(case.rows)}

    # Track power consumption
    total_power_12v = 0
    total_power_neg12v = 0
    total_power_5v = 0

    # Validate each module placement
    for idx, module_spec in enumerate(modules):
        # Get module
        module = db.query(Module).filter(Module.id == module_spec.module_id).first()
        if not module:
            errors.append(
                RackValidationError(
                    field=f"modules[{idx}].module_id",
                    message=f"Module with id {module_spec.module_id} not found",
                )
            )
            continue

        # Validate row index
        if module_spec.row_index >= case.rows:
            errors.append(
                RackValidationError(
                    field=f"modules[{idx}].row_index",
                    message=f"Row index {module_spec.row_index} exceeds case rows ({case.rows})",
                    details={"module_id": module.id, "module_name": module.name},
                )
            )
            continue

        # Validate HP fit
        row_hp = case.hp_per_row[module_spec.row_index]
        if module_spec.start_hp + module.hp > row_hp:
            errors.append(
                RackValidationError(
                    field=f"modules[{idx}].start_hp",
                    message=f"Module {module.name} ({module.hp}HP) at position {module_spec.start_hp} exceeds row capacity ({row_hp}HP)",
                    details={
                        "module_id": module.id,
                        "module_name": module.name,
                        "module_hp": module.hp,
                        "start_hp": module_spec.start_hp,
                        "row_hp": row_hp,
                    },
                )
            )
            continue

        # Check for overlap
        for hp in range(module_spec.start_hp, module_spec.start_hp + module.hp):
            if hp_usage[module_spec.row_index][hp]:
                errors.append(
                    RackValidationError(
                        field=f"modules[{idx}].start_hp",
                        message=f"Module {module.name} overlaps with another module at HP {hp}",
                        details={
                            "module_id": module.id,
                            "module_name": module.name,
                            "overlapping_hp": hp,
                        },
                    )
                )
                break
            hp_usage[module_spec.row_index][hp] = True

        # Accumulate power consumption
        if module.power_12v_ma:
            total_power_12v += module.power_12v_ma
        if module.power_neg12v_ma:
            total_power_neg12v += module.power_neg12v_ma
        if module.power_5v_ma:
            total_power_5v += module.power_5v_ma

    # Validate power constraints
    if case.power_12v_ma and total_power_12v > case.power_12v_ma:
        errors.append(
            RackValidationError(
                field="power",
                message=f"+12V power draw ({total_power_12v}mA) exceeds case capacity ({case.power_12v_ma}mA)",
                details={
                    "total_power_12v": total_power_12v,
                    "case_power_12v": case.power_12v_ma,
                },
            )
        )

    if case.power_neg12v_ma and total_power_neg12v > case.power_neg12v_ma:
        errors.append(
            RackValidationError(
                field="power",
                message=f"-12V power draw ({total_power_neg12v}mA) exceeds case capacity ({case.power_neg12v_ma}mA)",
                details={
                    "total_power_neg12v": total_power_neg12v,
                    "case_power_neg12v": case.power_neg12v_ma,
                },
            )
        )

    if case.power_5v_ma and total_power_5v > case.power_5v_ma:
        errors.append(
            RackValidationError(
                field="power",
                message=f"+5V power draw ({total_power_5v}mA) exceeds case capacity ({case.power_5v_ma}mA)",
                details={
                    "total_power_5v": total_power_5v,
                    "case_power_5v": case.power_5v_ma,
                },
            )
        )

    return len(errors) == 0, errors
