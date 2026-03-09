
from time import time

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    Float,
    String,
    Text,
)

from models.new.base import NewBase


class NewBeneficiary(NewBase):
    """New beneficiary table model with improved schema."""

    __tablename__ = "beneficiary"

    beneficiary_id = Column(String(20), primary_key=True)
    party_role_id = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    lkp_relation_id = Column(String(20), nullable=True)
    ssn = Column(Text, nullable=True)
    dob = Column(Date, nullable=True)  # Proper DATE type
    ssn4 = Column(String(4), nullable=True)
    middle_name = Column(String(100), nullable=True)
    is_primary = Column(Boolean, nullable=True)
    percentage = Column(Float, nullable=True, default=0.0)
    created_at = Column(BigInteger, nullable=True, default=lambda: int(time.time() * 1000))
    updated_at = Column(BigInteger, nullable=True, default=lambda: int(time.time() * 1000), onupdate=lambda: int(time.time() * 1000))
    deleted_at = Column(BigInteger, nullable=True, default=None)
    is_contigent = Column(Boolean, nullable=True)

    def __repr__(self) -> str:
        return f"<NewBeneficiary(beneficiary_id={self.beneficiary_id}, first_name={self.first_name}, last_name={self.last_name})>"
