"""
Beneficiary migration service.
Handles migration of beneficiary data from legacy database to new database.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from config.settings import settings
from models.legacy.beneficiary import LegacyBeneficiary
from models.new.beneficiary import NewBeneficiary
from services.database import db_manager
from utils.helpers import (
    normalize_relation,
    parse_dob,
    safe_bool,
    to_unix_ms,
    trim_varchar,
    validate_percentage,
)
from utils.logger import logger


class BeneficiaryMigrationService:
    """Service for migrating beneficiary data."""

    def __init__(self):
        """Initialize beneficiary migration service."""
        self.batch_size = settings.batch_size
        self.dry_run = settings.dry_run
        self.stats = {
            "total_legacy": 0,
            "already_migrated": 0,
            "to_migrate": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }
        self.errors: list[dict[str, Any]] = []

    def get_existing_ids(self, session: Session) -> set:
        """
        Get set of already migrated beneficiary IDs from new database.

        Args:
            session: SQLAlchemy session for new database

        Returns:
            Set of existing beneficiary IDs
        """
        try:
            stmt = select(NewBeneficiary.beneficiary_id)
            result = session.execute(stmt)
            existing_ids = {str(row[0]) for row in result.fetchall()}
            logger.debug(f"Found {len(existing_ids)} existing beneficiaries in new DB")
            return existing_ids
        except Exception as e:
            logger.error(f"Error fetching existing IDs: {e}")
            return set()

    def get_legacy_beneficiaries(self, session: Session) -> list[LegacyBeneficiary]:
        """
        Get all beneficiaries from legacy database.

        Args:
            session: SQLAlchemy session for legacy database

        Returns:
            List of legacy beneficiary records
        """
        try:
            stmt = select(LegacyBeneficiary).order_by(LegacyBeneficiary.id)
            result = session.execute(stmt)
            beneficiaries = result.scalars().all()
            logger.debug(f"Retrieved {len(beneficiaries)} beneficiaries from legacy DB")
            return list(beneficiaries)
        except Exception as e:
            logger.error(f"Error fetching legacy beneficiaries: {e}")
            raise

    def transform_beneficiary(
        self, legacy_record: LegacyBeneficiary
    ) -> NewBeneficiary | None:
        """
        Transform legacy beneficiary record to new format.

        Args:
            legacy_record: Legacy beneficiary record

        Returns:
            New beneficiary record or None if transformation fails
        """
        try:
            # Parse and validate date of birth
            dob = parse_dob(legacy_record.dob)
            if not dob:
                logger.warning(
                    f"Could not parse DOB for beneficiary {legacy_record.id}: '{legacy_record.dob}'"
                )

            # Transform fields with explicit typing matching Column definitions
            beneficiary_id = trim_varchar(str(legacy_record.id), 20) or str(legacy_record.id)[:20]
            party_role_id = None
            if legacy_record.userid is not None:
                party_role_id = trim_varchar(str(legacy_record.userid), 20)
            first_name = trim_varchar(legacy_record.fname, 100)
            last_name = trim_varchar(legacy_record.lname, 100)
            middle_name = trim_varchar(legacy_record.mname, 100)
            relation_str = None
            if legacy_record.relation is not None:
                if isinstance(legacy_record.relation, str):
                    relation_str = legacy_record.relation
                else:
                    relation_str = str(legacy_record.relation)
            lkp_relation_id = trim_varchar(normalize_relation(relation_str), 20)
            ssn = str(legacy_record.ssn) if legacy_record.ssn is not None else None
            # dob: Date, nullable=True
            # (already parsed above)
            # ssn4: String(4), nullable=True
            ssn4 = trim_varchar(legacy_record.ssn4, 4)
            is_primary = safe_bool(legacy_record.is_primary)
            percentage = validate_percentage(legacy_record.ben_percentage)
            is_contigent = safe_bool(legacy_record.is_contigent)
            created_at = to_unix_ms(getattr(legacy_record, 'created_at', None))
            updated_at = to_unix_ms(getattr(legacy_record, 'updated_at', None))
            deleted_at = to_unix_ms(getattr(legacy_record, 'deleted_at', None))

            # Create new beneficiary record
            new_record = NewBeneficiary(
                beneficiary_id=beneficiary_id,
                party_role_id=party_role_id,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                lkp_relation_id=lkp_relation_id,
                ssn=ssn,
                dob=dob,
                ssn4=ssn4,
                is_primary=is_primary,
                percentage=percentage,
                created_at=created_at,
                updated_at=updated_at,
                deleted_at=deleted_at,
                is_contigent=is_contigent,
            )

            return new_record

        except Exception as e:
            logger.error(f"Error transforming beneficiary {legacy_record.id}: {e}")
            self.errors.append({
                "beneficiary_id": legacy_record.id,
                "error": str(e),
                "type": "transformation_error",
            })
            return None

    def migrate_batch(
        self,
        batch: list[LegacyBeneficiary],
        new_session: Session,
        batch_num: int,
        total_batches: int,
    ) -> tuple[int, int]:
        """
        Migrate a batch of beneficiaries.

        Args:
            batch: List of legacy beneficiary records
            new_session: SQLAlchemy session for new database
            batch_num: Current batch number
            total_batches: Total number of batches

        Returns:
            Tuple of (success_count, failed_count)
        """
        success = 0
        failed = 0

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} records)...")

        for legacy_record in batch:
            try:
                # Transform record
                new_record = self.transform_beneficiary(legacy_record)
                if not new_record:
                    failed += 1
                    continue

                if self.dry_run:
                    logger.debug(f"DRY RUN: Would migrate beneficiary {new_record.beneficiary_id}")
                    success += 1
                else:
                    # Insert or update record
                    new_session.merge(new_record)
                    success += 1

            except Exception as e:
                logger.error(f"Error migrating beneficiary {legacy_record.id}: {e}")
                failed += 1
                self.errors.append({
                    "beneficiary_id": legacy_record.id,
                    "error": str(e),
                    "type": "migration_error",
                })

        try:
            if not self.dry_run:
                new_session.commit()
                logger.info(f"✓ Batch {batch_num} committed successfully ({success} records)")
            else:
                logger.info(f"✓ Batch {batch_num} processed (DRY RUN - {success} records)")
        except Exception as e:
            new_session.rollback()
            logger.error(f"✗ Batch {batch_num} FAILED: {e}")
            failed += len(batch)
            success = 0
            self.errors.append({
                "batch": batch_num,
                "error": str(e),
                "type": "batch_commit_error",
            })

        return success, failed

    def migrate(self) -> dict[str, Any]:
        """
        Perform full beneficiary migration.

        Returns:
            Dictionary with migration statistics
        """
        logger.print_header("BENEFICIARY MIGRATION")

        if self.dry_run:
            logger.warning("DRY RUN MODE - No actual changes will be made")

        try:
            # Test database connections
            if not db_manager.test_connection("both"):
                raise Exception("Database connection test failed")

            # Get existing IDs from new database
            with db_manager.new_session() as new_session:
                existing_ids = self.get_existing_ids(new_session)
                self.stats["already_migrated"] = len(existing_ids)

            # Get legacy beneficiaries
            with db_manager.legacy_session() as legacy_session:
                legacy_records = self.get_legacy_beneficiaries(legacy_session)
                self.stats["total_legacy"] = len(legacy_records)

            # Filter out already migrated records
            records_to_migrate = [
                r for r in legacy_records if str(r.id) not in existing_ids
            ]
            self.stats["to_migrate"] = len(records_to_migrate)

            logger.info(f"Found {self.stats['total_legacy']} beneficiaries in legacy DB")
            logger.info(f"Already migrated: {self.stats['already_migrated']}")
            logger.info(f"To migrate: {self.stats['to_migrate']}")

            if self.stats["to_migrate"] == 0:
                logger.success("No new beneficiaries to migrate")
                self._print_summary()
                return self.stats

            # Process in batches
            total_batches = (len(records_to_migrate) + self.batch_size - 1) // self.batch_size

            with db_manager.new_session() as new_session:
                for i in range(0, len(records_to_migrate), self.batch_size):
                    batch = records_to_migrate[i : i + self.batch_size]
                    batch_num = (i // self.batch_size) + 1

                    success, failed = self.migrate_batch(
                        batch, new_session, batch_num, total_batches
                    )

                    self.stats["success"] += success
                    self.stats["failed"] += failed

                    # Stop on batch error if not in dry run mode
                    if failed > 0 and not self.dry_run:
                        logger.warning("Stopping migration due to batch errors")
                        break

            self._print_summary()
            return self.stats

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            logger.exception("Full exception details:")
            raise

    def _print_summary(self) -> None:
        """Print migration summary."""
        summary_data = {
            "Total Legacy Records": self.stats["total_legacy"],
            "Already Migrated": self.stats["already_migrated"],
            "To Migrate": self.stats["to_migrate"],
            "Successfully Migrated": self.stats["success"],
            "Failed": self.stats["failed"],
            "Skipped": self.stats["skipped"],
        }

        success = self.stats["failed"] == 0
        logger.print_summary("BENEFICIARY MIGRATION SUMMARY", summary_data, success)

        if self.errors:
            logger.warning(f"Encountered {len(self.errors)} errors during migration")
            logger.info("Error details saved to log file")
            for error in self.errors[:5]:  # Show first 5 errors
                logger.error(f"  - {error}")


def migrate_beneficiaries() -> dict[str, Any]:
    """
    Convenience function to run beneficiary migration.

    Returns:
        Migration statistics
    """
    service = BeneficiaryMigrationService()
    return service.migrate()
