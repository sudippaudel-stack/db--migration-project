# Getting Started with Legacy Migration Tool

Welcome! This guide will help you get started with the Legacy Migration Tool in less than 10 minutes.

## 🎯 What You've Got

A complete, production-ready database migration tool built with:
- **Python 3.11+** with UV package manager
- **SQLAlchemy** for database operations
- **Pydantic** for configuration management
- **Click** for CLI interface
- **Rich** for beautiful console output
- **Docker Compose** for MySQL databases
- **Faker** for test data generation

## 📋 Prerequisites

Before you start, make sure you have:

- [x] Python 3.11 or higher
- [x] UV package manager (already used in your project)
- [x] Docker and Docker Compose (for databases)
- [x] Basic understanding of MySQL databases

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd legacy-migration-tool
uv sync
```

This installs all required packages into a virtual environment.

### Step 2: Start Databases

```bash
# Start MySQL containers
docker-compose up -d

# Wait 30 seconds for databases to initialize
sleep 30

# Verify they're running
docker-compose ps
```

You should see:
- `legacy-db-mysql` on port 3307
- `new-db-mysql` on port 3308
- `phpmyadmin` on port 8080

### Step 3: Test Connection

```bash
uv run python main.py db test
```

Expected output:
```
✓ Connected to legacy database: legacy_db
✓ Connected to new database: new_db
```

### Step 4: Generate Test Data

```bash
# Generate 1,000 fake beneficiaries
uv run python main.py seed beneficiary --count 1000

# Generate 500 fake dependents
uv run python main.py seed dependent --count 500
```

### Step 5: Run Migration

```bash
# Test first with dry-run (no changes)
uv run python main.py --dry-run migrate all

# Run actual migration
uv run python main.py migrate all
```

### Step 6: Verify Results

```bash
uv run python main.py db status
```

## 🎓 Understanding the Tool

### Project Structure

```
legacy-migration-tool/
├── legacy_migration_tool/          # Main Python package
│   ├── config/                     # Pydantic settings
│   │   └── settings.py
│   ├── models/                     # SQLAlchemy models
│   │   ├── legacy.py               # Old schema
│   │   └── new.py                  # New schema
│   ├── services/                   # Business logic
│   │   ├── database.py             # Connection manager
│   │   ├── beneficiary_migration.py
│   │   ├── dependent_migration.py
│   │   └── seeder.py               # Fake data generator
│   └── utils/                      # Utilities
│       ├── logger.py               # Logging
│       └── helpers.py              # Helper functions
├── docker/                         # Docker setup
│   └── init-scripts/               # SQL initialization
├── main.py                         # CLI entry point
├── docker-compose.yml              # Docker configuration
├── .env                            # Your configuration
└── Documentation files
```

### Key Concepts

#### 1. Configuration (`.env` file)

All settings are in the `.env` file:

```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=rootpassword

# Ports
LEGACY_DB_PORT=3307
NEW_DB_PORT=3308

# Migration
BATCH_SIZE=100
DRY_RUN=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/migration.log
```

#### 2. Database Models

The tool uses SQLAlchemy ORM models:

```python
# Legacy database (old schema)
class LegacyBeneficiary:
    id (INT)
    userid (INT)
    fname (VARCHAR)
    dob (VARCHAR - mixed formats)
    
# New database (improved schema)
class NewBeneficiary:
    beneficiary_id (VARCHAR)
    party_role_id (VARCHAR)
    first_name (VARCHAR)
    dob (DATE - parsed)
```

#### 3. Data Transformation

The tool automatically transforms data:
- Date strings → Proper DATE types
- VARCHAR percentages → FLOAT (validated)
- INT booleans → BOOLEAN
- Timestamps → Unix milliseconds
- Normalizes relations and genders

#### 4. Services

Business logic is in services:
- `database.py` - Connection pooling, session management
- `beneficiary_migration.py` - Beneficiary migration logic
- `dependent_migration.py` - Dependent migration logic
- `seeder.py` - Fake data generation

## 📚 Common Commands

### View Help

```bash
# Main help
uv run python main.py --help

# Command-specific help
uv run python main.py migrate --help
uv run python main.py seed --help
uv run python main.py db --help
```

### Database Operations

```bash
# Test connections
uv run python main.py db test

# Show status and counts
uv run python main.py db status

# Count rows in a table
uv run python main.py db count --database legacy --table beneficiary

# Create tables
uv run python main.py db create-tables

# Truncate a table (with confirmation)
uv run python main.py db truncate --database legacy --table beneficiary
```

### Seeding Data

```bash
# Seed beneficiaries (default: 3000)
uv run python main.py seed beneficiary

# Seed with custom count
uv run python main.py seed beneficiary --count 5000

# Seed dependents
uv run python main.py seed dependent --count 2000
```

### Migration

```bash
# Migrate beneficiaries only
uv run python main.py migrate beneficiary

# Migrate dependents only
uv run python main.py migrate dependent

# Migrate everything
uv run python main.py migrate all
```

### Using Flags

```bash
# Dry run (test without changes)
uv run python main.py --dry-run migrate all

# Change log level
uv run python main.py --log-level DEBUG migrate beneficiary

# Change batch size
uv run python main.py --batch-size 500 migrate all

# Combine flags
uv run python main.py --dry-run --log-level DEBUG --batch-size 50 migrate all
```

### Using Makefile (Shortcuts)

```bash
# See all available commands
make help

# Complete setup
make setup

# Seed all data
make seed-all

# Run migrations
make migrate-all

# Test migration (dry run)
make dry-run

# Check status
make db-status

# Clean everything
make clean
```

## 🎬 Typical Workflows

### Workflow 1: First-Time Setup

```bash
# 1. Setup everything
make setup

# 2. Generate test data
make seed-all

# 3. Test migration
make dry-run

# 4. Run migration
make migrate-all

# 5. Check results
make db-status
```

### Workflow 2: Test With Small Dataset

```bash
# Start databases
docker-compose up -d

# Generate small dataset
uv run python main.py seed beneficiary --count 100
uv run python main.py seed dependent --count 50

# Test migration
uv run python main.py --dry-run migrate all

# Run migration
uv run python main.py migrate all

# Verify
uv run python main.py db status
```

### Workflow 3: Using Real Data

```bash
# Start databases
docker-compose up -d

# Import your data into legacy database
docker exec -i legacy-db-mysql mysql -uroot -prootpassword legacy_db < your_data.sql

# Verify import
uv run python main.py db count --database legacy --table beneficiary

# Test migration
uv run python main.py --dry-run migrate all

# Review logs
tail -f logs/migration.log

# Run migration
uv run python main.py migrate all

# Verify
uv run python main.py db status
```

### Workflow 4: Incremental Migration

The tool automatically skips already migrated records:

```bash
# Initial migration
uv run python main.py migrate all

# Add more data to legacy DB
uv run python main.py seed beneficiary --count 1000

# Run migration again - only migrates new records
uv run python main.py migrate all
```

## 🔍 Accessing Your Data

### Using phpMyAdmin

1. Open http://localhost:8080
2. Choose server: `mysql-legacy` or `mysql-new`
3. Username: `root`
4. Password: `rootpassword`

### Using MySQL CLI

```bash
# Legacy database
docker exec -it legacy-db-mysql mysql -uroot -prootpassword legacy_db

# New database
docker exec -it new-db-mysql mysql -uroot -prootpassword new_db
```

### Sample Queries

```sql
-- In legacy database
SELECT COUNT(*) FROM beneficiary;
SELECT * FROM beneficiary LIMIT 10;

-- In new database
SELECT COUNT(*) FROM beneficiary;
SELECT * FROM beneficiary LIMIT 10;
```

## 📊 Understanding Logs

Logs are saved to `logs/migration.log`:

```bash
# View logs in real-time
tail -f logs/migration.log

# Search for errors
grep "ERROR" logs/migration.log

# Search for warnings
grep "WARNING" logs/migration.log

# View last 100 lines
tail -n 100 logs/migration.log
```

Log format:
```
2024-03-06 11:54:00 | INFO     | legacy_migration_tool | migrate:45 | Starting migration...
2024-03-06 11:54:01 | WARNING  | legacy_migration_tool | transform:78 | Could not parse DOB: '99/99/9999'
2024-03-06 11:54:05 | INFO     | legacy_migration_tool | migrate:120 | ✓ Batch 1/10 committed successfully
```

## 🛠️ Troubleshooting

### Problem: Can't connect to database

```bash
# Check containers
docker-compose ps

# Check logs
docker-compose logs mysql-legacy
docker-compose logs mysql-new

# Restart
docker-compose restart

# If still failing, rebuild
docker-compose down -v
docker-compose up -d
```

### Problem: Migration errors

```bash
# Check logs
tail -f logs/migration.log

# Try with smaller batch size
uv run python main.py --batch-size 50 migrate all

# Test with dry-run first
uv run python main.py --dry-run migrate all

# Enable debug logging
uv run python main.py --log-level DEBUG migrate all
```

### Problem: Import errors

```bash
# Make sure you're using UV
uv run python main.py --help

# If modules not found, reinstall
uv sync --reinstall
```

### Problem: Docker issues

```bash
# Stop everything
docker-compose down -v

# Remove volumes
docker volume prune

# Start fresh
docker-compose up -d
```

## 🎓 Next Steps

### Learn More

1. **Read comprehensive docs**: [README.md](README.md)
2. **Quick reference**: [QUICKSTART.md](QUICKSTART.md)
3. **See what's improved**: [MIGRATION_COMPARISON.md](MIGRATION_COMPARISON.md)
4. **Project overview**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### Customize the Tool

1. **Adjust configuration**: Edit `.env` file
2. **Add custom transformations**: Edit `utils/helpers.py`
3. **Modify migration logic**: Edit `services/*_migration.py`
4. **Add new entities**: Follow existing patterns

### Extend Functionality

```python
# Example: Add custom validation
# In utils/helpers.py

def validate_email(email: Optional[str]) -> bool:
    """Validate email format."""
    if not email:
        return False
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Use in migration services
from legacy_migration_tool.utils.helpers import validate_email

if not validate_email(record.email):
    logger.warning(f"Invalid email: {record.email}")
```

## 💡 Tips & Best Practices

### 1. Always Test First

```bash
# ALWAYS use dry-run first
uv run python main.py --dry-run migrate all
```

### 2. Start Small

```bash
# Test with small datasets
uv run python main.py seed beneficiary --count 100
uv run python main.py migrate beneficiary
```

### 3. Monitor Logs

```bash
# Keep logs open during migration
tail -f logs/migration.log
```

### 4. Backup Before Production

```bash
# Backup your databases before migrating production data
docker exec legacy-db-mysql mysqldump -uroot -prootpassword legacy_db > backup.sql
```

### 5. Use Appropriate Batch Size

- Small batches (50-100): Complex data, many transformations
- Medium batches (100-500): Normal data
- Large batches (500-1000): Simple, clean data

### 6. Check Database Status Regularly

```bash
uv run python main.py db status
```

## 📞 Getting Help

### Documentation Files

- **README.md** - Complete documentation
- **QUICKSTART.md** - 5-minute quick start
- **PROJECT_SUMMARY.md** - High-level overview
- **MIGRATION_COMPARISON.md** - Old vs new approach
- **GETTING_STARTED.md** - This file

### CLI Help

```bash
uv run python main.py --help
uv run python main.py migrate --help
uv run python main.py seed --help
uv run python main.py db --help
```

### Check Logs

```bash
tail -f logs/migration.log
```

## ✅ Checklist: Are You Ready?

Before running production migrations:

- [ ] Tested with small dataset
- [ ] Tested with dry-run mode
- [ ] Reviewed log output
- [ ] Verified data transformations
- [ ] Backed up databases
- [ ] Tested rollback procedure
- [ ] Documented any custom changes
- [ ] Set appropriate batch size
- [ ] Configured proper log level
- [ ] Tested error scenarios

## 🎉 You're Ready!

You now have everything you need to:

1. ✅ Generate test data
2. ✅ Test migrations safely
3. ✅ Run production migrations
4. ✅ Monitor and troubleshoot
5. ✅ Extend the tool

**Start with**: `make setup && make seed-all && make dry-run`

Happy migrating! 🚀

---

**Questions?** Check the other documentation files or review the code - it's well-commented!