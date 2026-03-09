# CLI Usage Guide

A comprehensive guide for using the Legacy Migration Tool command-line interface.

## Table of Contents

- [Quick Start](#quick-start)
- [Global Options](#global-options)
- [Database Commands](#database-commands)
- [Migration Commands](#migration-commands)
- [Seeding Commands](#seeding-commands)
- [Configuration](#configuration)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# Get help
python main.py --help

# Test database connections
python main.py db test

# Show current configuration
python main.py config

# Show database status
python main.py db status

# Seed test data
python main.py seed beneficiary --count 1000

# Migrate all data
python main.py migrate all
```

## Global Options

These options can be used with any command:

```bash
# Run in dry-run mode (no actual changes)
python main.py --dry-run migrate all

# Set log level
python main.py --log-level DEBUG db test

# Change batch size
python main.py --batch-size 500 migrate beneficiary

# Show version
python main.py --version
```

### Available Log Levels
- `DEBUG` - Detailed information for debugging
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors only

## Database Commands

### Test Connections

Test connectivity to both legacy and new databases:

```bash
python main.py db test
```

### Database Status

Show connection status and record counts for all tables:

```bash
python main.py db status
```

**Output includes:**
- Connection status for both databases
- Host and port information
- Record counts for all tables

### Create Tables

Create database tables in specified database(s):

```bash
# Create tables in both databases
python main.py db create-tables

# Create tables in legacy database only
python main.py db create-tables --database legacy

# Create tables in new database only
python main.py db create-tables --database new
```

### Count Records

Get row count for a specific table:

```bash
# Count beneficiaries in legacy database
python main.py db count --database legacy --table beneficiary

# Count dependents in new database
python main.py db count --database new --table dependent

# Count dependents in legacy database (note: table name is "dependents")
python main.py db count --database legacy --table dependents
```

### Truncate Tables

Delete all records from a table (with confirmation prompt):

```bash
# Truncate beneficiary table in legacy database
python main.py db truncate --database legacy --table beneficiary

# Truncate dependent table in new database
python main.py db truncate --database new --table dependent
```

⚠️ **WARNING:** This operation permanently deletes all data and cannot be undone!

## Migration Commands

### Migrate Beneficiaries

Migrate all beneficiary records from legacy to new database:

```bash
# Normal migration
python main.py migrate beneficiary

# Dry-run (no actual changes)
python main.py --dry-run migrate beneficiary

# With custom batch size
python main.py --batch-size 500 migrate beneficiary
```

**Features:**
- Data validation and transformation
- SSN encryption
- Date format conversion (string → DATE type)
- Error handling with detailed logging
- Statistics reporting

### Migrate Dependents

Migrate all dependent records from legacy to new database:

```bash
# Normal migration
python main.py migrate dependent

# Dry-run (no actual changes)
python main.py --dry-run migrate dependent

# With custom batch size
python main.py --batch-size 200 migrate dependent
```

**Features:**
- Data validation and transformation
- SSN encryption
- Date format conversion
- Height/weight data handling
- Gender and relation mapping
- Error handling with detailed logging

### Migrate All

Migrate both beneficiaries and dependents in sequence:

```bash
# Migrate everything
python main.py migrate all

# Dry-run
python main.py --dry-run migrate all

# With custom batch size
python main.py --batch-size 1000 migrate all
```

**Output includes:**
- Individual statistics for each migration type
- Overall summary with total counts
- Success/failure indicators

## Seeding Commands

### Seed Beneficiaries

Generate fake beneficiary records for testing:

```bash
# Generate 1000 records (default batch size: 100)
python main.py seed beneficiary --count 1000

# Generate 5000 records with custom batch size
python main.py seed beneficiary --count 5000 --batch-size 200

# Use default count (3000)
python main.py seed beneficiary
```

**Generated data includes:**
- First, middle, and last names
- SSN and SSN4
- Date of birth
- Relationship type
- Beneficiary percentage
- Primary/contingent status
- Timestamps

### Seed Dependents

Generate fake dependent records for testing:

```bash
# Generate 2000 records
python main.py seed dependent --count 2000

# Generate 10000 records with custom batch size
python main.py seed dependent --count 10000 --batch-size 500

# Use default count (3000)
python main.py seed dependent
```

**Generated data includes:**
- First, middle, and last names
- SSN and SSN4
- Date of birth
- Gender
- Relationship type
- Height and weight
- Disability information
- Approval status
- Timestamps

## Configuration

### View Configuration

Display all current configuration settings:

```bash
python main.py config
```

**Shows:**
- Database host and ports
- Database names
- Batch size
- Dry-run status
- Log level and file
- Seed count

### Environment Variables

Configuration can be customized via environment variables or `.env` file:

```bash
# Database settings
DB_HOST=localhost
LEGACY_DB_PORT=3307
NEW_DB_PORT=3308
LEGACY_DB_NAME=legacy_db
NEW_DB_NAME=new_db
DB_USER=root
DB_PASSWORD=password

# Application settings
BATCH_SIZE=100
SEED_COUNT=3000
LOG_LEVEL=INFO
LOG_FILE=logs/migration.log
DRY_RUN=false
```

## Common Workflows

### Initial Setup

```bash
# 1. Test database connections
python main.py db test

# 2. Create tables if needed
python main.py db create-tables

# 3. Check status
python main.py db status
```

### Testing Migration with Fake Data

```bash
# 1. Seed test data in legacy database
python main.py seed beneficiary --count 1000
python main.py seed dependent --count 2000

# 2. Verify data was created
python main.py db count --database legacy --table beneficiary
python main.py db count --database legacy --table dependents

# 3. Test migration with dry-run
python main.py --dry-run migrate all

# 4. Run actual migration
python main.py migrate all

# 5. Verify migration
python main.py db count --database new --table beneficiary
python main.py db count --database new --table dependent
```

### Production Migration

```bash
# 1. Verify configuration
python main.py config

# 2. Test connections
python main.py db test

# 3. Check record counts
python main.py db status

# 4. Dry-run migration
python main.py --dry-run migrate all

# 5. Run actual migration with logging
python main.py --log-level DEBUG migrate all > migration.log 2>&1

# 6. Verify results
python main.py db status
```

### Cleaning Up Test Data

```bash
# Remove all data from new database
python main.py db truncate --database new --table beneficiary
python main.py db truncate --database new --table dependent

# Remove all data from legacy database
python main.py db truncate --database legacy --table beneficiary
python main.py db truncate --database legacy --table dependents
```

### Debugging Failed Migrations

```bash
# 1. Run with debug logging
python main.py --log-level DEBUG migrate beneficiary

# 2. Check log file
cat logs/migration.log

# 3. Try with smaller batch size
python main.py --batch-size 10 migrate beneficiary

# 4. Use dry-run to see what would happen
python main.py --dry-run migrate beneficiary
```

## Troubleshooting

### Connection Issues

```bash
# Test connections
python main.py db test

# Check configuration
python main.py config

# Verify database is running
docker-compose ps

# Check environment variables
cat .env
```

### Migration Failures

If migration fails:

1. Check the log file: `logs/migration.log`
2. Run with debug logging: `--log-level DEBUG`
3. Try dry-run mode first: `--dry-run`
4. Reduce batch size: `--batch-size 10`
5. Check database status: `python main.py db status`

### Import Errors

If you see import errors:

```bash
# Install missing dependencies
uv pip install cryptography

# Or reinstall all dependencies
uv pip install -r pyproject.toml
```

### Permission Issues

If you get permission errors:

```bash
# Check database user permissions
# Make sure DB_USER has appropriate permissions

# For logs directory
mkdir -p logs
chmod 755 logs
```

## Exit Codes

The CLI uses standard exit codes:

- `0` - Success
- `1` - Failure/Error

This allows for scripting:

```bash
#!/bin/bash

if python main.py db test; then
    echo "Connections OK, proceeding with migration..."
    python main.py migrate all
else
    echo "Connection test failed!"
    exit 1
fi
```

## Getting Help

For any command, use `--help`:

```bash
# General help
python main.py --help

# Command group help
python main.py migrate --help
python main.py seed --help
python main.py db --help

# Specific command help
python main.py migrate beneficiary --help
python main.py seed dependent --help
python main.py db count --help
```

## Additional Resources

- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [GETTING_STARTED.md](GETTING_STARTED.md) - Detailed setup instructions
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture and design
- [MIGRATION_COMPARISON.md](MIGRATION_COMPARISON.md) - Schema comparison

## Examples

### Complete Migration Workflow

```bash
# Step 1: Setup
python main.py db test
python main.py db create-tables

# Step 2: Seed test data
python main.py seed beneficiary --count 1000
python main.py seed dependent --count 2000

# Step 3: Verify data
python main.py db status

# Step 4: Test migration
python main.py --dry-run migrate all

# Step 5: Run migration
python main.py migrate all

# Step 6: Verify results
python main.py db status
python main.py db count --database new --table beneficiary
python main.py db count --database new --table dependent
```

### Batch Processing with Different Sizes

```bash
# Small batches for careful processing
python main.py --batch-size 50 migrate beneficiary

# Large batches for speed
python main.py --batch-size 1000 migrate dependent

# Very small batches for debugging
python main.py --batch-size 10 --log-level DEBUG migrate all
```

### Automated Testing Script

```bash
#!/bin/bash
set -e

echo "Starting automated migration test..."

# Clean up
python main.py db truncate --database new --table beneficiary || true
python main.py db truncate --database new --table dependent || true

# Seed data
python main.py seed beneficiary --count 100
python main.py seed dependent --count 200

# Migrate
python main.py migrate all

# Verify
LEGACY_BEN=$(python main.py db count --database legacy --table beneficiary | grep -o '[0-9]*')
NEW_BEN=$(python main.py db count --database new --table beneficiary | grep -o '[0-9]*')

if [ "$LEGACY_BEN" == "$NEW_BEN" ]; then
    echo "✓ Migration successful! Counts match: $LEGACY_BEN"
else
    echo "✗ Migration failed! Legacy: $LEGACY_BEN, New: $NEW_BEN"
    exit 1
fi
```

---

**Version:** 1.0.0  
**Last Updated:** 2024-03-06