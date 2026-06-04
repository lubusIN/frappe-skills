```markdown
# Bench Commands Reference

## Overview
Frappe Bench CLI commands for use inside Frappe Manager containers.

## Accessing Bench CLI

```bash
# Enter container shell
fm shell mysite

# Now bench commands are available
bench --help
```

## Site Management

```bash
# Create new site
bench new-site mysite.localhost --db-root-password root --admin-password admin

# Delete site
bench drop-site mysite.localhost --db-root-password root

# List sites
ls sites/

# Set default site
bench use mysite.localhost
```

## App Management

```bash
# Get app from frappe.cloud
bench get-app erpnext

# Get app from GitHub
bench get-app https://github.com/frappe/hrms.git

# Get specific branch
bench get-app erpnext --branch version-15

# Install app on site
bench --site mysite.localhost install-app erpnext

# Uninstall app
bench --site mysite.localhost uninstall-app erpnext

# List installed apps
bench --site mysite.localhost list-apps

# Create new custom app
bench new-app my_custom_app
```

## Database & Migrations

```bash
# Run migrations
bench --site mysite.localhost migrate

# Run all pending patches
bench --site mysite.localhost migrate --skip-failing

# Backup database
bench --site mysite.localhost backup

# Backup with files
bench --site mysite.localhost backup --with-files

# Restore from backup
bench --site mysite.localhost restore /path/to/backup.sql.gz

# Access MariaDB
bench --site mysite.localhost mariadb
```

## Development

```bash
# Enable developer mode
bench set-config -g developer_mode 1

# Disable developer mode
bench set-config -g developer_mode 0

# Build assets
bench build

# Build specific app
bench build --app my_app

# Watch mode (live rebuild)
bench watch

# Clear cache
bench --site mysite.localhost clear-cache

# Clear website cache
bench --site mysite.localhost clear-website-cache

# Console (Python REPL)
bench --site mysite.localhost console
```

## Testing

```bash
# Run all tests for app
bench --site mysite.localhost run-tests --app my_app

# Run specific doctype tests
bench --site mysite.localhost run-tests --doctype "Sales Order"

# Run specific module tests
bench --site mysite.localhost run-tests --module my_app.utils.tests

# With coverage
bench --site mysite.localhost run-tests --app my_app --coverage

# UI tests
bench --site mysite.localhost run-ui-tests my_app --headless
```

## Server Management

```bash
# Start development server
bench serve

# Start with specific settings
bench serve --port 8001

# Check service status
bench doctor

# Version info
bench version

# Update bench
bench update

# Update specific app
bench update --apps erpnext
```

## User Management

```bash
# Set admin password
bench --site mysite.localhost set-admin-password newpassword

# Add system manager
bench --site mysite.localhost add-system-manager user@example.com

# Disable user
bench --site mysite.localhost disable-user user@example.com
```

## Scheduler & Jobs

```bash
# Enable scheduler
bench --site mysite.localhost enable-scheduler

# Disable scheduler
bench --site mysite.localhost disable-scheduler

# Run scheduler manually
bench --site mysite.localhost scheduler

# Execute specific job
bench --site mysite.localhost execute my_app.tasks.daily_cleanup

# Clear failed jobs
bench --site mysite.localhost clear-scheduler-priority-jobs
```

## Configuration

```bash
# Set config value
bench --site mysite.localhost set-config key value

# Set global config
bench set-config -g key value

# Show config
bench --site mysite.localhost show-config

# Bench config file
# Located at: sites/common_site_config.json
```

## Data Management

```bash
# Export fixtures
bench --site mysite.localhost export-fixtures

# Import data
bench --site mysite.localhost import-doc /path/to/doc.json

# Export data
bench --site mysite.localhost export-doc "DocType/DocName"

# Bulk data import
bench --site mysite.localhost data-import --file /path/to/file.csv --doctype "Customer"
```

## Translations

```bash
# Update translations
bench update-translations

# Build translations
bench build-message-files

# Get untranslated
bench --site mysite.localhost get-untranslated
```

## Useful Shortcuts

```bash
# Quick site console
bench c

# Quick mariadb
bench m

# Quick serve
bench s
```

## Environment Variables

```bash
# Set Python path
export PYTHONPATH=/workspace/frappe-bench/apps/my_app

# Run with specific site
FRAPPE_SITE=mysite.localhost bench execute my_app.utils.run_task
```

Sources: Bench CLI, Frappe Commands (official docs)
```