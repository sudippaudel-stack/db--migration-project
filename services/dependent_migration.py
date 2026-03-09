"""
Dependent migration service.
Handles migration of dependent data from legacy database to new database.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from config.settings import settings
from models.legacy.dependent import LegacyDependent
from models.new.dependent import NewDependent
from services.database import db_manager
from utils.helpers import (
    normalize_gender,
    normalize_relation,
    parse_dob,
    safe_bool,
    safe_float,
    safe_int,
    to_unix_ms,
    trim_varchar,
)
from utils.logger import logger


class DependentMigrationService:
    """Service for migrating dependent data."""

    def __init__(self):
        """Initialize dependent migration service."""
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
        Get set of already migrated dependent IDs from new database.

        Args:
            session: SQLAlchemy session for new database

        Returns:
            Set of existing dependent IDs
        """
        try:
            stmt = select(NewDependent.dependent_id)
            result = session.execute(stmt)
            existing_ids = {str(row[0]) for row in result.fetchall()}
            logger.debug(f"Found {len(existing_ids)} existing dependents in new DB")
            return existing_ids
        except Exception as e:
            logger.error(f"Error fetching existing IDs: {e}")
            return set()

    def get_legacy_dependents(self, session: Session) -> list[LegacyDependent]:
        """
        Get all dependents from legacy database.

        Args:
            session: SQLAlchemy session for legacy database

        Returns:
            List of legacy dependent records
        """
        try:
            stmt = select(LegacyDependent).order_by(LegacyDependent.did)
            result = session.execute(stmt)
            dependents = result.scalars().all()
            logger.debug(f"Retrieved {len(dependents)} dependents from legacy DB")
            return list(dependents)
        except Exception as e:
            logger.error(f"Error fetching legacy dependents: {e}")
            raise

    def transform_dependent(
        self, legacy_record: LegacyDependent
    ) -> NewDependent | None:
        """
        Transform legacy dependent record to new format.

        Args:
            legacy_record: Legacy dependent record

        Returns:
            New dependent record or None if transformation fails
        """
        try:
            # Parse and validate date of birth
            dob = parse_dob(legacy_record.d_dob)
            if not dob:
                logger.warning(
                    f"Could not parse DOB for dependent {legacy_record.did}: '{legacy_record.d_dob}'"
                )

            # Transform fields with explicit handling matching Column definitions
            dependent_id = trim_varchar(str(legacy_record.did), 20) or str(legacy_record.did)[:20]
            party_role_id = trim_varchar(str(legacy_record.userid), 20) or str(legacy_record.userid)[:20]
            first_name = trim_varchar(legacy_record.d_fname, 100)
            last_name = trim_varchar(legacy_record.d_lname, 100)
            middle_name = trim_varchar(legacy_record.d_mname, 100)
            relation_str = str(legacy_record.d_relate) if legacy_record.d_relate is not None else None
            relation = normalize_relation(relation_str)
            lkp_relation_id = trim_varchar(relation, 20)
            gender_str = str(legacy_record.d_gender) if legacy_record.d_gender is not None else None
            gender = normalize_gender(gender_str)
            lkp_gender_id = trim_varchar(gender, 20)
            ssn = str(legacy_record.d_ssn) if legacy_record.d_ssn is not None else None
            ssn4 = trim_varchar(legacy_record.d_ssn4, 4)
            notes = str(legacy_record.additional_notes) if legacy_record.additional_notes is not None else None
            is_disabled = safe_bool(legacy_record.disabled)
            height_feet = safe_int(legacy_record.dhrq)
            height_inch = safe_int(legacy_record.dhrq2)
            weight = safe_float(legacy_record.dwrq)
            is_approved = safe_bool(legacy_record.is_approved)
            is_legally_disapproved = safe_bool(legacy_record.is_legally_disabled)
            disability_condition = trim_varchar(legacy_record.disability_condition, 255)
            created_at = to_unix_ms(getattr(legacy_record, 'created_at', None))
            updated_at = to_unix_ms(getattr(legacy_record, 'updated_at', None))
            deleted_at = to_unix_ms(getattr(legacy_record, 'deleted_at', None))

            # Create new dependent record
            new_record = NewDependent(
                dependent_id=dependent_id,
                party_role_id=party_role_id,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                lkp_relation_id=lkp_relation_id,
                lkp_gender_id=lkp_gender_id,
                ssn=ssn,
                dob=dob,
                ssn4=ssn4,
                notes=notes,
                is_disabled=is_disabled,
                height_in_feet=height_feet,
                height_in_inch=height_inch,
                weight=weight,
                is_approved=is_approved,
                created_at=created_at,
                updated_at=updated_at,
                deleted_at=deleted_at,
                is_legally_disapproved=is_legally_disapproved,
                disability_condition=disability_condition,
            )

            return new_record

        except Exception as e:
            logger.error(f"Error transforming dependent {legacy_record.did}: {e}")
            self.errors.append({
                "dependent_id": legacy_record.did,
                "error": str(e),
                "type": "transformation_error",
            })
            return None

    def migrate_batch(
        self,
        batch: list[LegacyDependent],
        new_session: Session,
        batch_num: int,
        total_batches: int,
    ) -> tuple[int, int]:
        """
        Migrate a batch of dependents.

        Args:
            batch: List of legacy dependent records
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
                new_record = self.transform_dependent(legacy_record)
                if not new_record:
                    failed += 1
                    continue

                if self.dry_run:
                    logger.debug(f"DRY RUN: Would migrate dependent {new_record.dependent_id}")
                    success += 1
                else:
                    # Insert or update record
                    new_session.merge(new_record)
                    success += 1

            except Exception as e:
                logger.error(f"Error migrating dependent {legacy_record.did}: {e}")
                failed += 1
                self.errors.append({
                    "dependent_id": legacy_record.did,
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
        Perform full dependent migration.

        Returns:
            Dictionary with migration statistics
        """
        logger.print_header("DEPENDENT MIGRATION")

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

            # Get legacy dependents
            with db_manager.legacy_session() as legacy_session:
                legacy_records = self.get_legacy_dependents(legacy_session)
                self.stats["total_legacy"] = len(legacy_records)

            # Filter out already migrated records
            records_to_migrate = [
                r for r in legacy_records if str(r.did) not in existing_ids
            ]
            self.stats["to_migrate"] = len(records_to_migrate)

            logger.info(f"Found {self.stats['total_legacy']} dependents in legacy DB")
            logger.info(f"Already migrated: {self.stats['already_migrated']}")
            logger.info(f"To migrate: {self.stats['to_migrate']}")

            if self.stats["to_migrate"] == 0:
                logger.success("No new dependents to migrate")
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
        logger.print_summary("DEPENDENT MIGRATION SUMMARY", summary_data, success)

        if self.errors:
            logger.warning(f"Encountered {len(self.errors)} errors during migration")
            logger.info("Error details saved to log file")
            for error in self.errors[:5]:  # Show first 5 errors
                logger.error(f"  - {error}")


def migrate_dependents() -> dict[str, Any]:
    """
    Convenience function to run dependent migration.

    Returns:
        Migration statistics
    """
    service = DependentMigrationService()
    return service.migrate()
