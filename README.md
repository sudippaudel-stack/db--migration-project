# Legacy Migration Tool

A comprehensive CLI tool for migrating data from legacy database schemas to new improved schemas with data validation, transformation, and seeding capabilities.

## Features

- ✅ **Database Migration**: Migrate beneficiary and dependent data from legacy to new schema
- ✅ **Data Validation**: Automatic data validation and transformation
- ✅ **Batch Processing**: Efficient batch processing with configurable batch sizes
- ✅ **Dry Run Mode**: Test migrations without making actual changes
- ✅ **Fake Data Generation**: Generate fake data for testing using Faker
- ✅ **Rich CLI**: Beautiful command-line interface with progress indicators
- ✅ **Comprehensive Logging**: File and console logging with different log levels
- ✅ **Docker Support**: Includes Docker Compose for MySQL databases
- ✅ **Type Safety**: Built with Pydantic for configuration and data validation
- ✅ **SQLAlchemy ORM**: Modern database operations with connection pooling

## Architecture

```
legacy-migration-tool/
├── legacy_migration_tool/       # Main package
│   ├── config/                  # Configuration management (Pydantic)
│   │   └── settings.py          # Environment-based settings
│   ├── models/                  # SQLAlchemy models
│   │   ├── legacy.py            # Legacy database models
│   │   └── new.py               # New database models
│   ├── services/                # Business logic
│   │   ├── database.py          # Database connection manager
│   │   ├── beneficiary_migration.py
│   │   ├── dependent_migration.py
│   │   └── seeder.py            # Fake data generator
│   └── utils/                   # Utilities
│       ├── logger.py            # Rich logging setup
│       └── helpers.py           # Helper functions
├── docker/                      # Docker configurations
│   └── init-scripts/            # SQL initialization scripts
│       ├── legacy/              # Legacy DB schemas
│       └── new/                 # New DB schemas
├── docker-compose.yml           # Docker Compose configuration
├── main.py                      # CLI entry point
├── .env                         # Environment variables
└── pyproject.toml              # UV project configuration
```

## Prerequisites

- Python 3.11+
- UV package manager
- Docker and Docker Compose (optional, for database containers)
- MySQL 8.0+ (if not using Docker)

## Installation

### 1. Clone/Navigate to the project

```bash
cd legacy-migration-tool
```

### 2. Install dependencies with UV

```bash
# UV will automatically create a virtual environment
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Start databases with Docker (recommended)

```bash
docker-compose up -d
```

This will start:

- `mysql-legacy` on port 3307
- `mysql-new` on port 3308
- `phpmyadmin` on port 8080 (for database management)

Wait a few seconds for the databases to initialize, then verify:

```bash
docker-compose ps
```

## Configuration

Edit `.env` file to configure the tool:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=rootpassword

# Legacy Database
LEGACY_DB=legacy_db
LEGACY_DB_PORT=3307

# New Database
NEW_DB=new_db
NEW_DB_PORT=3308

# Migration Settings
BATCH_SIZE=100
DRY_RUN=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/migration.log

# Faker/Seeder Settings
SEED_COUNT=3000
```

## Usage

### CLI Commands

The tool provides a comprehensive CLI with the following commands:

```bash
# Show help
uv run python main.py --help

# Show current configuration
uv run python main.py config
```

### Database Management

```bash
# Test database connections
uv run python main.py db test

# Show database status and record counts
uv run python main.py db status

# Create tables in databases
uv run python main.py db create-tables
uv run python main.py db create-tables --database legacy
uv run python main.py db create-tables --database new

# Get row count for a table
uv run python main.py db count --database legacy --table beneficiary
uv run python main.py db count --database new --table dependent

# Truncate a table (with confirmation)
uv run python main.py db truncate --database legacy --table beneficiary
```

### Seeding Fake Data

Generate fake data for testing:

```bash
# Seed beneficiaries (default: 3000 records)
uv run python main.py seed beneficiary

# Seed beneficiaries with custom count
uv run python main.py seed beneficiary --count 5000

# Seed dependents
uv run python main.py seed dependent --count 1000
```

### Data Migration

Migrate data from legacy to new database:

```bash
# Migrate beneficiaries only
uv run python main.py migrate beneficiary

# Migrate dependents only
uv run python main.py migrate dependent

# Migrate all data (beneficiaries + dependents)
uv run python main.py migrate all
```

### Dry Run Mode

Test migrations without making actual changes:

```bash
# Dry run migration
uv run python main.py --dry-run migrate beneficiary

# Dry run all migrations
uv run python main.py --dry-run migrate all
```

### Batch Size Configuration

Change batch size for migrations:

```bash
# Use smaller batch size (50 records per batch)
uv run python main.py --batch-size 50 migrate beneficiary

# Use larger batch size (500 records per batch)
uv run python main.py --batch-size 500 migrate all
```

### Logging

Control log level:

```bash
# Debug level logging
uv run python main.py --log-level DEBUG migrate beneficiary

# Error level only
uv run python main.py --log-level ERROR migrate all
```

Logs are saved to `logs/migration.log` by default.

## Complete Workflow Example

Here's a complete workflow from setup to migration:

```bash
# 1. Start databases
docker-compose up -d

# 2. Wait for databases to be ready (check logs)
docker-compose logs -f mysql-legacy mysql-new

# 3. Test database connections
uv run python main.py db test

# 4. Check database status
uv run python main.py db status

# 5. Seed fake data into legacy database
uv run python main.py seed beneficiary --count 5000
uv run python main.py seed dependent --count 2000

# 6. Verify data was seeded
uv run python main.py db count --database legacy --table beneficiary
uv run python main.py db count --database legacy --table dependents

# 7. Test migration with dry run
uv run python main.py --dry-run migrate all

# 8. Perform actual migration
uv run python main.py migrate all

# 9. Verify migration
uv run python main.py db status

# 10. Check logs for any issues
tail -f logs/migration.log
```

## Data Transformation

The tool performs the following transformations during migration:

### Beneficiary Migration

- **ID Mapping**: `id` → `beneficiary_id` (VARCHAR)
- **User ID**: `userid` → `party_role_id` (VARCHAR)
- **Names**: `fname`, `lname`, `mname` → `first_name`, `last_name`, `middle_name` (VARCHAR 100)
- **Relation**: `relation` → `lkp_relation_id` (normalized, uppercase)
- **Date of Birth**: `dob` (VARCHAR, multiple formats) → `dob` (DATE)
- **Percentage**: `ben_percentage` (VARCHAR) → `percentage` (FLOAT, validated 0-100)
- **Timestamps**: `created_at`, `updated_at`, `deleted_at` (TIMESTAMP) → Unix milliseconds (BIGINT)
- **Booleans**: `is_primary`, `is_contigent` (INT) → proper BOOLEAN

### Dependent Migration

- **ID Mapping**: `did` → `dependent_id` (VARCHAR)
- **User ID**: `userid` → `party_role_id` (VARCHAR)
- **Names**: `d_fname`, `d_lname`, `d_mname` → `first_name`, `last_name`, `middle_name`
- **Relation**: `d_relate` → `lkp_relation_id` (normalized)
- **Gender**: `d_gender` → `lkp_gender_id` (normalized to M/F/O)
- **Date of Birth**: `d_dob` (VARCHAR) → `dob` (DATE)
- **Height**: `dhrq`, `dhrq2` (VARCHAR) → `height_in_feet`, `height_in_inch` (INT)
- **Weight**: `dwrq` (VARCHAR) → `weight` (FLOAT)
- **Notes**: `additional_notes` → `notes`
- **Disability**: `disabled`, `is_legally_disabled` → `is_disabled`, `is_legally_disapproved` (BOOLEAN)
- **Timestamps**: Converted to Unix milliseconds

### Date Parsing

The tool handles multiple date formats:

- `YYYY-MM-DD` (ISO format)
- `MM/DD/YYYY` (US format)
- `DD-MM-YYYY` (European format)
- `YYYY/MM/DD`
- `DD/MM/YYYY`
- `MM-DD-YYYY`

### Data Validation

- **SSN**: Cleaned of non-numeric characters
- **Percentage**: Validated to be between 0-100
- **Boolean conversions**: Handles INT, VARCHAR ('0', '1', 'true', 'false', etc.)
- **String trimming**: Enforces VARCHAR length limits
- **NULL handling**: Graceful handling of missing/invalid data

## Accessing Databases

### Using phpMyAdmin

Access phpMyAdmin at http://localhost:8080

- **Server**: `mysql-legacy` or `mysql-new`
- **Username**: `root`
- **Password**: `rootpassword` (from .env)

### Using MySQL CLI

```bash
# Connect to legacy database
docker exec -it legacy-db-mysql mysql -uroot -prootpassword legacy_db

# Connect to new database
docker exec -it new-db-mysql mysql -uroot -prootpassword new_db
```

### Using Python Scripts

You can also use the database manager directly in Python:

```python
from legacy_migration_tool.services.database import db_manager
from legacy_migration_tool.models.legacy import LegacyBeneficiary

# Query legacy database
with db_manager.legacy_session() as session:
    beneficiaries = session.query(LegacyBeneficiary).limit(10).all()
    for ben in beneficiaries:
        print(f"{ben.fname} {ben.lname}")
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if containers are running
docker-compose ps

# Check container logs
docker-compose logs mysql-legacy
docker-compose logs mysql-new

# Restart containers
docker-compose restart

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Migration Errors

1. **Check logs**: Review `logs/migration.log` for detailed error messages
2. **Dry run first**: Always test with `--dry-run` flag before actual migration
3. **Batch size**: Reduce batch size if encountering memory issues
4. **Data validation**: Check for invalid dates, SSNs, or other data issues in legacy DB

### Common Issues

**Issue**: "No module named 'legacy_migration_tool'"
**Solution**: Make sure you're running with `uv run python main.py`

**Issue**: "Can't connect to MySQL server"
**Solution**: Wait for databases to initialize (check `docker-compose logs`)

**Issue**: "Table doesn't exist"
**Solution**: Run `uv run python main.py db create-tables`

**Issue**: Migration is slow
**Solution**: Increase batch size: `--batch-size 500`

## Development

### Project Structure

- **Models**: SQLAlchemy ORM models for both databases
- **Services**: Business logic for migrations and seeding
- **Utils**: Helper functions and logging utilities
- **Config**: Pydantic-based configuration management
- **CLI**: Click-based command-line interface

### Adding New Migrations

1. Create model in `models/legacy.py` and `models/new.py`
2. Create migration service in `services/your_migration.py`
3. Add CLI commands in `main.py`
4. Update tests

### Testing

```bash
# Run with dry-run mode
uv run python main.py --dry-run migrate all

# Test with small dataset
uv run python main.py seed beneficiary --count 100
uv run python main.py migrate beneficiary
```

## Performance Considerations

- **Batch Size**: Default 100 records per batch. Increase for faster migrations of clean data.
- **Connection Pooling**: SQLAlchemy connection pooling is configured (pool_size=10)
- **Memory**: Batch processing keeps memory usage low even for large datasets
- **Indexing**: New database includes indexes for better query performance

## Dependencies

Key dependencies:

- **click**: CLI framework
- **sqlalchemy**: ORM and database toolkit
- **pydantic**: Data validation and settings management
- **pymysql**: MySQL database driver
- **faker**: Fake data generation
- **rich**: Beautiful terminal output
- **python-dotenv**: Environment variable management

## License

[Your License Here]

## Support

For issues, questions, or contributions, please contact the development team or open an issue.

---

**Built with ❤️ using UV, SQLAlchemy, Pydantic, and Click**
