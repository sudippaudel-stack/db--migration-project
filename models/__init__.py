"""
SQLAlchemy models for legacy and new database schemas.
"""

from models.legacy import (
    LegacyBase,
    LegacyBeneficiary,
    LegacyDependent,
)
from models.new import (
    NewBase,
    NewBeneficiary,
    NewDependent,
)

__all__ = [
    "LegacyBase",
    "LegacyBeneficiary",
    "LegacyDependent",
    "NewBase",
    "NewBeneficiary",
    "NewDependent",
]
