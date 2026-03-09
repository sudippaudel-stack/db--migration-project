"""
SQLAlchemy models for legacy database tables.
These models represent the schema of the legacy database.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    String,
    Text,
)

from models.legacy.base import LegacyBase


class LegacyDependent(LegacyBase):
    """Legacy dependents table model."""

    __tablename__ = "dependents"

    did = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, nullable=False, index=True)
    d_fname = Column(String(225), nullable=True)
    d_lname = Column(String(225), nullable=True)
    d_mname = Column(String(10), nullable=True)
    d_relate = Column(String(10), nullable=True)
    d_gender = Column(String(1), nullable=True)
    d_ssn = Column(String(100), nullable=True)
    d_dob = Column(String(225), nullable=True)  # Stored as string in legacy DB
    d_ssn4 = Column(String(10), nullable=True)
    additional_notes = Column(Text, nullable=True)
    disabled = Column(String(1), default="0")
    dhrq = Column(String(10), nullable=True)  # Height in feet
    dhrq2 = Column(String(10), nullable=True)  # Height in inches
    dwrq = Column(String(10), nullable=True)  # Weight
    is_approved = Column(String(1), default="0")
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at = Column(TIMESTAMP, nullable=True, index=True)
    is_legally_disabled = Column(Boolean, default=False)
    disability_condition = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<LegacyDependent(did={self.did}, d_fname={self.d_fname}, d_lname={self.d_lname})>"
