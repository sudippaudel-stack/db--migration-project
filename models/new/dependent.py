"""
SQLAlchemy models for new database tables.
These models represent the schema of the new database with improved data types.
"""


from time import time

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    Float,
    Index,
    Integer,
    String,
    Text,
)

from models.new.base import NewBase


class NewDependent(NewBase):
    """New dependent table model with improved schema."""

    __tablename__ = "dependent"

    dependent_id = Column(String(20), primary_key=True)
    party_role_id = Column(String(20), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    lkp_relation_id = Column(String(20), nullable=True, index=True)
    lkp_gender_id = Column(String(20), nullable=True, index=True)
    ssn = Column(Text, nullable=True)
    dob = Column(Date, nullable=True)  # Proper DATE type
    ssn4 = Column(String(4), nullable=True)
    notes = Column(Text, nullable=True)
    is_disabled = Column(Boolean, default=False)
    height_in_feet = Column(Integer, nullable=True)
    height_in_inch = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(BigInteger, nullable=True, default=lambda: int(time.time() * 1000))
    updated_at = Column(BigInteger, nullable=True, default=lambda: int(time.time() * 1000), onupdate=lambda: int(time.time() * 1000))
    deleted_at = Column(BigInteger, nullable=True, default=None)
    is_legally_disapproved = Column(Boolean, default=False)
    disability_condition = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_dependent_party_role_id", "party_role_id"),
        Index("idx_dependent_deleted_at", "deleted_at"),
        Index("idx_dependent_lkp_relation_id", "lkp_relation_id"),
        Index("idx_dependent_lkp_gender_id", "lkp_gender_id"),
    )

    def __repr__(self) -> str:
        return f"<NewDependent(dependent_id={self.dependent_id}, first_name={self.first_name}, last_name={self.last_name})>"
