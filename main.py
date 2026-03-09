"""
Legacy Migration Tool CLI
Main entry point for the command-line interface.
"""

import sys

import click
from rich.console import Console
from rich.table import Table

from config.settings import settings
from services.beneficiary_migration import migrate_beneficiaries
from services.beneficiary_seeder import seed_beneficiaries
from services.database import db_manager
from services.dependent_migration import migrate_dependents
from services.dependent_seeder import seed_dependents
from utils.logger import logger

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="legacy-migration-tool")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Run in dry-run mode (no actual changes)",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set logging level",
)
@click.option(
    "--batch-size",
    type=int,
    help="Batch size for migrations (default: 100)",
)
def cli(dry_run: bool, log_level: str, batch_size: int):
    """
    Legacy Migration Tool - Migrate data from legacy database to new schema.

    A comprehensive tool for migrating beneficiary and dependent data with
    data validation, transformation, and seeding capabilities.

    \b
    Examples:
        # Show help for all commands
        $ python main.py --help

        # Migrate all data from legacy to new database
        $ python main.py migrate all

        # Seed 1000 beneficiaries in legacy database
        $ python main.py seed beneficiary --count 1000

        # Test database connections
        $ python main.py db test

        # Show current configuration
        $ python main.py config
    """
    # Override settings if flags are provided
    if dry_run:
        settings.dry_run = True
        logger.warning("Running in DRY RUN mode - no actual changes will be made")

    if log_level:
        settings.log_level = log_level
        logger.logger.setLevel(log_level)

    if batch_size:
        settings.batch_size = batch_size


@cli.group()
def migrate():
    """
    Migrate data from legacy database to new database.

    \b
    Examples:
        $ python main.py migrate beneficiary
        $ python main.py migrate dependent
        $ python main.py migrate all
    """
    pass


@migrate.command("beneficiary")
def migrate_beneficiary_cmd():
    """
    Migrate beneficiary records from legacy to new database.

    Transforms and migrates all beneficiary records with data validation,
    error handling, and detailed statistics reporting.

    \b
    Example:
        $ python main.py migrate beneficiary
        $ python main.py --dry-run migrate beneficiary
    """
    try:
        logger.info("Starting beneficiary migration...")
        stats = migrate_beneficiaries()

        if stats["failed"] == 0:
            logger.success("Beneficiary migration completed successfully!")
            sys.exit(0)
        else:
            logger.error("Beneficiary migration completed with errors")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Beneficiary migration failed: {e}")
        sys.exit(1)


@migrate.command("dependent")
def migrate_dependent_cmd():
    """
    Migrate dependent records from legacy to new database.

    Transforms and migrates all dependent records with data validation,
    error handling, and detailed statistics reporting.

    \b
    Example:
        $ python main.py migrate dependent
        $ python main.py --dry-run migrate dependent
    """
    try:
        logger.info("Starting dependent migration...")
        stats = migrate_dependents()

        if stats["failed"] == 0:
            logger.success("Dependent migration completed successfully!")
            sys.exit(0)
        else:
            logger.error("Dependent migration completed with errors")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Dependent migration failed: {e}")
        sys.exit(1)


@migrate.command("all")
def migrate_all_cmd():
    """
    Migrate all data (beneficiary and dependent) from legacy to new database.

    Runs both beneficiary and dependent migrations in sequence with
    comprehensive summary statistics.

    \b
    Example:
        $ python main.py migrate all
        $ python main.py --batch-size 500 migrate all
    """
    try:
        logger.print_header("MIGRATING ALL DATA")

        # Migrate beneficiaries
        logger.info("Step 1/2: Migrating beneficiaries...")
        ben_stats = migrate_beneficiaries()

        # Migrate dependents
        logger.info("Step 2/2: Migrating dependents...")
        dep_stats = migrate_dependents()

        # Print overall summary
        total_success = ben_stats["success"] + dep_stats["success"]
        total_failed = ben_stats["failed"] + dep_stats["failed"]

        summary_data = {
            "Beneficiaries Migrated": ben_stats["success"],
            "Dependents Migrated": dep_stats["success"],
            "Total Migrated": total_success,
            "Total Failed": total_failed,
        }

        logger.print_summary("OVERALL MIGRATION SUMMARY", summary_data, total_failed == 0)

        if total_failed == 0:
            logger.success("All migrations completed successfully!")
            sys.exit(0)
        else:
            logger.error("Migrations completed with errors")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


@cli.group()
def seed():
    """
    Generate fake data for testing.

    Creates realistic fake data in the legacy database for testing
    the migration process.

    \b
    Examples:
        $ python main.py seed beneficiary --count 1000
        $ python main.py seed dependent --count 5000
    """
    pass


@seed.command("beneficiary")
@click.option(
    "--count",
    type=int,
    help=f"Number of records to generate (default: {settings.seed_count})",
)
@click.option(
    "--batch-size",
    type=int,
    help=f"Batch size for insertions (default: {settings.batch_size})",
)
def seed_beneficiary_cmd(count: int, batch_size: int):
    """
    Generate fake beneficiary records in legacy database.

    Creates realistic beneficiary records with random but valid data
    for testing purposes.

    \b
    Examples:
        $ python main.py seed beneficiary --count 1000
        $ python main.py seed beneficiary --count 5000 --batch-size 200
    """
    try:
        logger.info("Starting beneficiary seeding...")
        stats = seed_beneficiaries(count, batch_size)

        if stats["failed"] == 0:
            logger.success("Beneficiary seeding completed successfully!")
            sys.exit(0)
        else:
            logger.error("Beneficiary seeding completed with errors")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Beneficiary seeding failed: {e}")
        sys.exit(1)


@seed.command("dependent")
@click.option(
    "--count",
    type=int,
    help=f"Number of records to generate (default: {settings.seed_count})",
)
@click.option(
    "--batch-size",
    type=int,
    help=f"Batch size for insertions (default: {settings.batch_size})",
)
def seed_dependent_cmd(count: int, batch_size: int):
    """
    Generate fake dependent records in legacy database.

    Creates realistic dependent records with random but valid data
    for testing purposes.

    \b
    Examples:
        $ python main.py seed dependent --count 2000
        $ python main.py seed dependent --count 10000 --batch-size 500
    """
    try:
        logger.info("Starting dependent seeding...")
        stats = seed_dependents(count, batch_size)

        if stats["failed"] == 0:
            logger.success("Dependent seeding completed successfully!")
            sys.exit(0)
        else:
            logger.error("Dependent seeding completed with errors")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Dependent seeding failed: {e}")
        sys.exit(1)


@cli.group()
def db():
    """
    Database management commands.

    Manage database connections, tables, and data.

    \b
    Examples:
        $ python main.py db test
        $ python main.py db status
        $ python main.py db create-tables
        $ python main.py db count --database legacy --table beneficiary
    """
    pass


@db.command("test")
def db_test_cmd():
    """
    Test database connections.

    Verifies connectivity to both legacy and new databases.

    \b
    Example:
        $ python main.py db test
    """
    try:
        logger.print_header("DATABASE CONNECTION TEST")

        success = db_manager.test_connection("both")

        if success:
            logger.success("All database connections successful!")
            sys.exit(0)
        else:
            logger.error("Database connection test failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        sys.exit(1)


@db.command("create-tables")
@click.option(
    "--database",
    type=click.Choice(["legacy", "new", "both"]),
    default="both",
    help="Which database to create tables in",
)
def db_create_tables_cmd(database: str):
    """
    Create database tables.

    Creates the necessary tables in the specified database(s).

    \b
    Examples:
        $ python main.py db create-tables
        $ python main.py db create-tables --database legacy
        $ python main.py db create-tables --database new
    """
    try:
        logger.print_header(f"CREATING TABLES IN {database.upper()} DATABASE")
        db_manager.create_tables(database)
        logger.success("Tables created successfully!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        sys.exit(1)


@db.command("count")
@click.option(
    "--database",
    type=click.Choice(["legacy", "new"]),
    required=True,
    help="Which database to query",
)
@click.option(
    "--table",
    type=click.Choice(["beneficiary", "dependent", "dependents"]),
    required=True,
    help="Which table to count",
)
def db_count_cmd(database: str, table: str):
    """
    Get row count for a table.

    Returns the number of rows in the specified table.

    \b
    Examples:
        $ python main.py db count --database legacy --table beneficiary
        $ python main.py db count --database new --table dependent
    """
    try:
        count = db_manager.get_table_count(database, table)
        logger.info(f"Table '{table}' in '{database}' database has {count} rows")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to count rows: {e}")
        sys.exit(1)


@db.command("truncate")
@click.option(
    "--database",
    type=click.Choice(["legacy", "new"]),
    required=True,
    help="Which database",
)
@click.option(
    "--table",
    type=click.Choice(["beneficiary", "dependent", "dependents"]),
    required=True,
    help="Which table to truncate",
)
@click.confirmation_option(
    prompt="Are you sure you want to truncate this table? This cannot be undone!"
)
def db_truncate_cmd(database: str, table: str):
    """
    Truncate a table (delete all rows).

    WARNING: This permanently deletes all data in the table!
    You will be prompted for confirmation.

    \b
    Examples:
        $ python main.py db truncate --database legacy --table beneficiary
        $ python main.py db truncate --database new --table dependent
    """
    try:
        db_manager.truncate_table(database, table, confirm=True)
        logger.success(f"Table '{table}' in '{database}' database truncated successfully!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to truncate table: {e}")
        sys.exit(1)


@db.command("status")
def db_status_cmd():  # noqa: PLR0915
    """
    Show database status and record counts.

    Displays connection status and row counts for all tables in both
    legacy and new databases.

    \b
    Example:
        $ python main.py db status
    """
    try:
        logger.print_header("DATABASE STATUS")

        # Test connections
        legacy_connected = False
        new_connected = False

        try:
            db_manager.test_connection("legacy")
            legacy_connected = True
        except Exception:
            pass

        try:
            db_manager.test_connection("new")
            new_connected = True
        except Exception:
            pass

        # Create status table
        table = Table(title="Database Connection Status", show_header=True, header_style="bold cyan")
        table.add_column("Database", style="cyan", width=20)
        table.add_column("Status", width=15)
        table.add_column("Host:Port", width=25)

        legacy_status = "✓ Connected" if legacy_connected else "✗ Disconnected"
        new_status = "✓ Connected" if new_connected else "✗ Disconnected"

        table.add_row(
            "Legacy DB",
            f"[green]{legacy_status}[/green]" if legacy_connected else f"[red]{legacy_status}[/red]",
            f"{settings.db_host}:{settings.legacy_db_port}"
        )
        table.add_row(
            "New DB",
            f"[green]{new_status}[/green]" if new_connected else f"[red]{new_status}[/red]",
            f"{settings.db_host}:{settings.new_db_port}"
        )

        console.print(table)

        # Show record counts if connected
        if legacy_connected:
            console.print("\n[bold cyan]Legacy Database Record Counts:[/bold cyan]")
            try:
                ben_count = db_manager.get_table_count("legacy", "beneficiary")
                console.print(f"  Beneficiaries: {ben_count}")
            except Exception:
                console.print("  Beneficiaries: [red]Error[/red]")

            try:
                dep_count = db_manager.get_table_count("legacy", "dependents")
                console.print(f"  Dependents: {dep_count}")
            except Exception:
                console.print("  Dependents: [red]Error[/red]")

        if new_connected:
            console.print("\n[bold cyan]New Database Record Counts:[/bold cyan]")
            try:
                ben_count = db_manager.get_table_count("new", "beneficiary")
                console.print(f"  Beneficiaries: {ben_count}")
            except Exception:
                console.print("  Beneficiaries: [red]Error[/red]")

            try:
                dep_count = db_manager.get_table_count("new", "dependent")
                console.print(f"  Dependents: {dep_count}")
            except Exception:
                console.print("  Dependents: [red]Error[/red]")

        console.print()
        sys.exit(0)

    except Exception as e:
        logger.error(f"Failed to get database status: {e}")
        sys.exit(1)


@cli.command("config")
def config_cmd():
    """
    Show current configuration.

    Displays all current configuration settings including database
    connections, batch sizes, and other parameters.

    \b
    Example:
        $ python main.py config
    """
    logger.print_header("CONFIGURATION")

    config_data = {
        "Database Host": settings.db_host,
        "Legacy DB": f"{settings.legacy_db} (port {settings.legacy_db_port})",
        "New DB": f"{settings.new_db} (port {settings.new_db_port})",
        "Batch Size": settings.batch_size,
        "Dry Run": settings.dry_run,
        "Log Level": settings.log_level,
        "Log File": settings.log_file,
        "Seed Count": settings.seed_count,
    }

    logger.print_summary("CURRENT CONFIGURATION", config_data)
    sys.exit(0)


if __name__ == "__main__":
    cli()
