"""External integrations for PatchHive.

Integration CLIs may query models that retain string-based relationships to
legacy entities. Import the dependency models here so standalone ``python -m
integrations.<tool>`` commands configure SQLAlchemy mappers deterministically,
matching the registration behavior used by the backend test harness.
"""

from community.models import Comment, User, Vote  # noqa: F401
from modules.models import Module  # noqa: F401
from patches.models import Patch  # noqa: F401
from racks.models import Rack, RackModule  # noqa: F401

__all__: list[str] = []
