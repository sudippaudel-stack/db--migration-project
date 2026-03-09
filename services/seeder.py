"""
Seeder service for generating fake data.
Handles generation of fake beneficiary and dependent records for testing.
"""

import random
from typing import Any

from faker import Faker

from config.settings import settings
from models.legacy.beneficiary import LegacyBeneficiary
from models.legacy.dependent import LegacyDependent
from services.database import db_manager
from utils.logger import logger

# Initialize Faker
fake = Faker()

# Constants
RELATIONS = ['SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'OTHER']
GENDERS = ['M', 'F']


class SeederService:
    """Service for generating fake data."""

    def __init__(self, count: int | None = None):
        """
        Initialize seeder service.

        Args:
            count: Number of records to generate (defaults to settings.seed_count)
        """
        self.count = count or settings.seed_count
        self.batch_size = settings.batch_size
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

    def generate_fake_dependent(self) -> LegacyDependent:
        """
        Generate a single fake dependent record.

        Returns:
            LegacyDependent instance with fake data
        """
        # Generate date of birth
        dob_date = fake.date_of_birth(minimum_age=0, maximum_age=25)

        # Random date format for variety
        dob_format = random.choice([
            "%Y-%m-%d",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d-%m-%Y",
        ])
        dob_str = dob_date.strftime(dob_format)

        # Generate deleted_at for some records (10% soft deleted)
        deleted_at = None
        if random.random() < 0.10:
            deleted_at = fake.date_time_between(start_date="-1y", end_date="now")

        # Generate SSN
        ssn_full = fake.numerify(text="#########")
        ssn4 = ssn_full[-4:]

        # Generate middle name (60% have middle name)
        mname = fake.first_name()[:1] if random.random() > 0.4 else None

        # Generate disability info (10% disabled)
        is_disabled = random.random() < 0.10
        disability_condition = fake.sentence(nb_words=6) if is_disabled else None

        # Generate height and weight
        height_feet = random.randint(3, 6) if random.random() > 0.2 else None
        height_inch = random.randint(0, 11) if height_feet else None
        weight = round(random.uniform(20, 200), 1) if random.random() > 0.2 else None

        # Additional notes (30% have notes)
        notes = fake.text(max_nb_chars=200) if random.random() < 0.30 else None

        dependent = LegacyDependent(
            userid=random.randint(100, 9999),
            d_fname=fake.first_name(),
            d_lname=fake.last_name(),
            d_mname=mname,
            d_relate=random.choice(['CHILD', 'SPOUSE', 'OTHER']),
            d_gender=random.choice(GENDERS),
            d_ssn=ssn_full,
            d_dob=dob_str,
            d_ssn4=ssn4,
            additional_notes=notes,
            disabled='1' if is_disabled else '0',
            dhrq=str(height_feet) if height_feet else None,
            dhrq2=str(height_inch) if height_inch else None,
            dwrq=str(weight) if weight else None,
            is_approved=str(random.randint(0, 1)),
            deleted_at=deleted_at,
            is_legally_disabled=is_disabled and random.random() < 0.5,
            disability_condition=disability_condition,
        )

        return dependent

    def seed_beneficiaries(self) -> dict[str, Any]:
        """
        Seed fake beneficiary data into legacy database.

        Returns:
            Dictionary with seeding statistics
        """
        logger.print_header(f"SEEDING BENEFICIARIES ({self.count} records)")

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

            self._print_summary("BENEFICIARY")
            return self.stats

        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            logger.exception("Full exception details:")
            raise

    def seed_dependents(self) -> dict[str, Any]:
        """
        Seed fake dependent data into legacy database.

        Returns:
            Dictionary with seeding statistics
        """
        logger.print_header(f"SEEDING DEPENDENTS ({self.count} records)")

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
                            dependent = self.generate_fake_dependent()
                            batch.append(dependent)
                        except Exception as e:
                            logger.error(f"Error generating dependent: {e}")
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

            self._print_summary("DEPENDENT")
            return self.stats

        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            logger.exception("Full exception details:")
            raise

    def _print_summary(self, entity_type: str) -> None:
        """
        Print seeding summary.

        Args:
            entity_type: Type of entity seeded
        """
        summary_data = {
            "Requested": self.stats["requested"],
            "Generated": self.stats["generated"],
            "Failed": self.stats["failed"],
        }

        success = self.stats["failed"] == 0
        logger.print_summary(f"{entity_type} SEEDING SUMMARY", summary_data, success)


def seed_beneficiaries(count: int | None = None) -> dict[str, Any]:
    """
    Convenience function to seed beneficiaries.

    Args:
        count: Number of records to generate

    Returns:
        Seeding statistics
    """
    service = SeederService(count)
    return service.seed_beneficiaries()


def seed_dependents(count: int | None = None) -> dict[str, Any]:
    """
    Convenience function to seed dependents.

    Args:
        count: Number of records to generate

    Returns:
        Seeding statistics
    """
    service = SeederService(count)
    return service.seed_dependents()
