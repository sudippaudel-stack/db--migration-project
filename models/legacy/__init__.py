"""
Legacy database models.
"""

from models.legacy.base import LegacyBase
from models.legacy.beneficiary import LegacyBeneficiary
from models.legacy.dependent import LegacyDependent

__all__ = [
    "LegacyBase",
    "LegacyBeneficiary",
    "LegacyDependent",
]