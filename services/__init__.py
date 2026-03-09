"""
Services module for legacy migration tool.
Contains business logic for migrations, seeding, and database operations.
"""

from services.beneficiary_migration import (
    BeneficiaryMigrationService,
    migrate_beneficiaries,
)
from services.beneficiary_seeder import (
    BeneficiarySeeder,
    seed_beneficiaries,
)
from services.database import db_manager, get_db_manager
from services.dependent_migration import (
    DependentMigrationService,
    migrate_dependents,
)
from services.dependent_seeder import (
    DependentSeeder,
    seed_dependents,
)

__all__ = [
    "BeneficiaryMigrationService",
    "DependentMigrationService",
    "db_manager",
    "get_db_manager",
    "migrate_beneficiaries",
    "migrate_dependents",
    "seed_beneficiaries",
    "seed_dependents",
]
