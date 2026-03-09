from datetime import datetime, timezone

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    String,
)

from models.legacy.base import LegacyBase


class LegacyBeneficiary(LegacyBase):
    """Legacy beneficiary table model."""

    __tablename__ = "beneficiary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, nullable=True)
    fname = Column(String(255), nullable=True)
    lname = Column(String(255), nullable=True)
    relation = Column(String(255), nullable=True)
    ssn = Column(String(255), nullable=True)
    dob = Column(String(255), nullable=True)  # Stored as string in legacy DB
    ssn4 = Column(String(5), nullable=True)
    mname = Column(String(255), nullable=True)
    is_primary = Column(Integer, default=0)
    ben_percentage = Column(String(3), nullable=True)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at = Column(TIMESTAMP, nullable=True)
    is_contigent = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<LegacyBeneficiary(id={self.id}, fname={self.fname}, lname={self.lname})>"
