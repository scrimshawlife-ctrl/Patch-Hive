import re

from core.naming import name_patch_v2


class DummyModule:
    def __init__(self, module_type: str, name: str = ""):
        self.module_type = module_type
        self.name = name


def test_patch_name_is_deterministic():
    modules = {1: DummyModule("VCO"), 2: DummyModule("VCA")}
    connections = [
        {
            "from_module_id": 1,
            "from_port": "Audio Out",
            "to_module_id": 2,
            "to_port": "Audio In",
            "cable_type": "audio",
        }
    ]

    name_a = name_patch_v2(123, modules, connections)
    name_b = name_patch_v2(123, modules, connections)

    assert name_a == name_b


def test_patch_name_humor_gate():
    modules = {
        1: DummyModule("VCO"),
        2: DummyModule("ENV"),
    }
    connections = [
        {
            "from_module_id": 1,
            "from_port": "Audio Out",
            "to_module_id": 2,
            "to_port": "CV In",
            "cable_type": "cv",
        },
        {
            "from_module_id": 2,
            "from_port": "Env Out",
            "to_module_id": 1,
            "to_port": "FM In",
            "cable_type": "cv",
        },
    ]

    name = name_patch_v2(777, modules, connections)

    assert re.search(r"\(.+\)$", name)
