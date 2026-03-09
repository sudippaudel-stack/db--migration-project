# Quick Start Guide

Get up and running with the Legacy Migration Tool in 5 minutes!

## 🚀 Quick Setup (5 minutes)

### Step 1: Start Databases (1 minute)

```bash
docker-compose up -d
```

Wait ~30 seconds for databases to initialize.

### Step 2: Test Connection (30 seconds)

```bash
uv run python main.py db test
```

You should see:
```
✓ Connected to legacy database: legacy_db
✓ Connected to new database: new_db
```

### Step 3: Generate Test Data (2 minutes)

```bash
# Generate 5,000 fake beneficiaries
uv run python main.py seed beneficiary --count 5000

# Generate 2,000 fake dependents
uv run python main.py seed dependent --count 2000
```

### Step 4: Run Migration (2 minutes)

```bash
# Test with dry run first (recommended)
uv run python main.py --dry-run migrate all

# Run actual migration
uv run python main.py migrate all
```

### Step 5: Verify Results (30 seconds)

```bash
uv run python main.py db status
```

## ✨ Using the Makefile (Even Easier!)

If you prefer a single command approach:

```bash
# Complete setup and workflow
make setup      # Install + start databases
make seed-all   # Generate test data
make migrate-all # Run migration
```

## 📊 View Your Data

### Using phpMyAdmin

Open http://localhost:8080 in your browser

- **Server**: `mysql-legacy` or `mysql-new`
- **Username**: `root`
- **Password**: `rootpassword`

### Using MySQL CLI

```bash
# Legacy database
docker exec -it legacy-db-mysql mysql -uroot -prootpassword legacy_db

# New database
docker exec -it new-db-mysql mysql -uroot -prootpassword new_db
```

## 🎯 Common Commands

```bash
# Check database status
uv run python main.py db status

# Test connections
uv run python main.py db test

# View configuration
uv run python main.py config

# Seed more data
uv run python main.py seed beneficiary --count 10000

# Migrate specific entity
uv run python main.py migrate beneficiary
uv run python main.py migrate dependent

# Dry run (test without changes)
uv run python main.py --dry-run migrate all

# Custom batch size
uv run python main.py --batch-size 500 migrate all

# Debug mode
uv run python main.py --log-level DEBUG migrate all
```

## 🔧 Using Makefile Commands

```bash
make help           # Show all available commands
make status         # Docker container status
make db-status      # Database status
make seed-all       # Seed all data
make migrate-all    # Migrate all data
make dry-run        # Test migration
make clean          # Clean up everything
```

## 📝 Real-World Workflow

Here's a typical workflow for production use:

```bash
# 1. Start fresh
docker-compose up -d
make db-test

# 2. Optional: Seed test data (skip if using real data)
make seed-all

# 3. Verify source data
uv run python main.py db count --database legacy --table beneficiary
uv run python main.py db count --database legacy --table dependents

# 4. Test migration (DRY RUN - no changes)
uv run python main.py --dry-run migrate all

# 5. Check logs
tail -f logs/migration.log

# 6. Run actual migration
uv run python main.py migrate all

# 7. Verify results
uv run python main.py db status
uv run python main.py db count --database new --table beneficiary
uv run python main.py db count --database new --table dependent

# 8. Review logs for any issues
grep "ERROR" logs/migration.log
grep "WARNING" logs/migration.log
```

## 🎬 Complete Example Session

```bash
# Terminal Session Example
$ cd legacy-migration-tool

$ docker-compose up -d
✓ Started mysql-legacy on port 3307
✓ Started mysql-new on port 3308
✓ Started phpmyadmin on port 8080

$ uv run python main.py db test
✓ Connected to legacy database: legacy_db
✓ Connected to new database: new_db

$ uv run python main.py seed beneficiary --count 3000
✓ Generated 3000 beneficiaries in 30 batches

$ uv run python main.py seed dependent --count 1000
✓ Generated 1000 dependents in 10 batches

$ uv run python main.py --dry-run migrate all
DRY RUN MODE - No actual changes
✓ Would migrate 3000 beneficiaries
✓ Would migrate 1000 dependents

$ uv run python main.py migrate all
✓ Migrated 3000 beneficiaries
✓ Migrated 1000 dependents
✓ All migrations completed successfully!

$ uv run python main.py db status
Legacy DB: ✓ Connected - 3000 beneficiaries, 1000 dependents
New DB: ✓ Connected - 3000 beneficiaries, 1000 dependents
```

## 🛠️ Troubleshooting

### Can't connect to database?

```bash
# Check containers are running
docker-compose ps

# Check logs
docker-compose logs mysql-legacy
docker-compose logs mysql-new

# Restart
docker-compose restart
```

### Migration errors?

```bash
# Check logs
tail -f logs/migration.log

# Try with smaller batch size
uv run python main.py --batch-size 50 migrate all

# Test with dry run first
uv run python main.py --dry-run migrate all
```

### Want to start fresh?

```bash
# Stop and remove everything
docker-compose down -v

# Start again
docker-compose up -d

# Or use make
make clean
make setup
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [logs/migration.log](logs/migration.log) for detailed logs
- Explore different CLI options with `--help`
- Customize `.env` file for your environment
- Add custom transformations in `services/` directory

## 💡 Tips

1. **Always test with `--dry-run` first**
2. **Check logs regularly**: `tail -f logs/migration.log`
3. **Use appropriate batch size**: Smaller for complex data, larger for simple data
4. **Monitor database status**: `make db-status` or `uv run python main.py db status`
5. **Backup before production**: Always backup your databases before migration

## 🎉 You're Ready!

That's it! You now have a working migration tool. Start with small batches, test thoroughly, and scale up as needed.

For more details, see [README.md](README.md)