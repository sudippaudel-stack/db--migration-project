"""
Beneficiary seeder service for generating fake beneficiary data.
"""

import random
from typing import Any

from faker import Faker

from config.settings import settings
from models.legacy.beneficiary import LegacyBeneficiary
from services.database import db_manager
from utils.logger import logger

# Initialize Faker
fake = Faker()

# Constants
RELATIONS = ['SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER']


class BeneficiarySeeder:
    """Service for generating fake beneficiary data."""

    def __init__(self, count: int | None = None, batch_size: int | None = None):
        """
        Initialize beneficiary seeder service.

        Args:
            count: Number of records to generate (defaults to settings.seed_count)
            batch_size: Batch size for insertions (defaults to settings.batch_size)
        """
        self.count = count or settings.seed_count
        self.batch_size = batch_size or settings.batch_size
        self.stats = {
            "requested": self.count,
            "generated": 0,
            "failed": 0,
        }

    def generate_fake_beneficiary(self) -> LegacyBeneficiary:
        """
        Generate a single fake beneficiary record.

        Returns:
            LegacyBeneficiary instance with fake data
        """
        # Generate date of birth
        dob_date = fake.date_of_birth(minimum_age=18, maximum_age=80)

        # Random date format for variety
        dob_format = random.choice([
            "%Y-%m-%d",    # Most common
            "%Y-%m-%d",    # Weight towards ISO format
            "%Y-%m-%d",
            "%m/%d/%Y",    # US format
            "%d-%m-%Y",    # European format
        ])
        dob_str = dob_date.strftime(dob_format)

        # Generate deleted_at for some records (15% soft deleted)
        deleted_at = None
        if random.random() < 0.15:
            deleted_at = fake.date_time_between(start_date="-1y", end_date="now")

        # Generate SSN
        ssn_full = fake.numerify(text="#########")
        ssn4 = ssn_full[-4:]

        # Generate middle name (70% have middle name)
        mname = fake.first_name() if random.random() > 0.3 else None

        beneficiary = LegacyBeneficiary(
            userid=random.randint(100, 9999),
            fname=fake.first_name(),
            lname=fake.last_name(),
            mname=mname,
            relation=random.choice(RELATIONS),
            ssn=ssn_full,
            dob=dob_str,
            ssn4=ssn4,
            is_primary=random.randint(0, 1),
            ben_percentage=str(random.randint(1, 100)),
            deleted_at=deleted_at,
            is_contigent=random.randint(0, 1),
        )

        return beneficiary

    def seed(self) -> dict[str, Any]:
        """
        Seed fake beneficiary data into legacy database.

        Returns:
            Dictionary with seeding statistics
        """
        logger.print_header(f"SEEDING BENEFICIARIES ({self.count} records, batch size: {self.batch_size})")

        try:
            total_batches = (self.count + self.batch_size - 1) // self.batch_size

            with db_manager.legacy_session() as session:
                for i in range(0, self.count, self.batch_size):
                    batch_size = min(self.batch_size, self.count - i)
                    batch_num = (i // self.batch_size) + 1

                    logger.info(f"Generating batch {batch_num}/{total_batches} ({batch_size} records)...")

                    batch = []
                    for _ in range(batch_size):
                        try:
                            beneficiary = self.generate_fake_beneficiary()
                            batch.append(beneficiary)
                        except Exception as e:
                            logger.error(f"Error generating beneficiary: {e}")
                            self.stats["failed"] += 1

                    try:
                        session.add_all(batch)
                        session.commit()
                        self.stats["generated"] += len(batch)
                        logger.info(f"✓ Batch {batch_num} inserted successfully ({len(batch)} records)")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"✗ Batch {batch_num} FAILED: {e}")
                        self.stats["failed"] += len(batch)
                        logger.error("FATAL: Seeding terminated due to batch failure")
                        break

            self._print_summary()
            return self.stats

        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            logger.exception("Full exception details:")
            raise

    def _print_summary(self) -> None:
        """Print seeding summary."""
        summary_data = {
            "Requested": self.stats["requested"],
            "Generated": self.stats["generated"],
            "Failed": self.stats["failed"],
        }

        success = self.stats["failed"] == 0
        logger.print_summary("BENEFICIARY SEEDING SUMMARY", summary_data, success)


def seed_beneficiaries(count: int | None = None, batch_size: int | None = None) -> dict[str, Any]:
    """
    Convenience function to seed beneficiaries.

    Args:
        count: Number of records to generate
        batch_size: Batch size for insertions

    Returns:
        Seeding statistics
    """
    seeder = BeneficiarySeeder(count, batch_size)
    return seeder.seed()
