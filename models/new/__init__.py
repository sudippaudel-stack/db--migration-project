"""
New database models.
"""

from models.new.base import NewBase
from models.new.beneficiary import NewBeneficiary
from models.new.dependent import NewDependent

__all__ = [
    "NewBase",
    "NewBeneficiary",
    "NewDependent",
]