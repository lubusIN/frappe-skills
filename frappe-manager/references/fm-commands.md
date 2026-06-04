```markdown
# FM Commands Reference

## Overview
Complete reference for Frappe Manager CLI commands.

## Global Commands

```bash
# Show version
fm --version

# Show help
fm --help

# Install shell completion
fm --install-completion

# Uninstall shell completion
fm --uninstall-completion
```

## Site Creation

### fm create
Create a new Frappe bench/site.

```bash
fm create [OPTIONS] BENCHNAME
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `-a, --apps TEXT` | Apps to install (format: app or app:branch) | frappe |
| `--environment, --env` | Environment type: dev | prod | dev |
| `--developer-mode` | Toggle developer mode: enable | disable | enable |
| `--frappe-branch TEXT` | Frappe branch | version-15 |
| `--admin-pass TEXT` | Admin password | admin |
| `--ssl` | SSL type: letsencrypt | disable | disable |
| `--letsencrypt-email TEXT` | Email for Let's Encrypt | - |
| `--letsencrypt-preferred-challenge` | http01 | dns01 | http01 |
| `--template / --no-template` | Create template bench | no-template |

**Examples:**
```bash
# Basic site
fm create mysite

# With ERPNext
fm create mysite --apps erpnext:version-15

# Production with SSL
fm create example.com --env prod --ssl letsencrypt --letsencrypt-email admin@example.com

# Multiple apps
fm create mysite --apps erpnext --apps hrms --apps insights
```

## Site Management

### List Sites
```bash
fm list
```

### Start/Stop
```bash
fm start BENCHNAME
fm stop BENCHNAME
```

### Delete Site
```bash
fm delete BENCHNAME

# Force delete
fm delete BENCHNAME --force
```

### Site Info
```bash
fm info BENCHNAME
```

### View Logs
```bash
fm logs BENCHNAME

# Follow mode
fm logs BENCHNAME -f

# Last N lines
fm logs BENCHNAME --tail 100
```

### Update Site
```bash
fm update BENCHNAME
```

## Development Commands

### Shell Access
```bash
fm shell BENCHNAME
```

Opens an interactive shell inside the container with bench available.

### VS Code Integration
```bash
# Open in VS Code
fm code BENCHNAME

# With debugger
fm code BENCHNAME --debugger
```

### Restart Services
```bash
fm restart BENCHNAME
```

## SSL Management

### fm ssl
Manage SSL certificates for a site.

```bash
# Check status
fm ssl BENCHNAME status

# Enable Let's Encrypt
fm ssl BENCHNAME letsencrypt --email admin@example.com

# Use custom certificate
fm ssl BENCHNAME custom --cert-path /path/to/cert.pem --key-path /path/to/key.pem

# Disable SSL
fm ssl BENCHNAME disable

# Renew certificate
fm ssl BENCHNAME renew
```

## Global Services

### fm services
Manage global FM services (reverse proxy, etc.).

```bash
# List services
fm services list

# Start services
fm services start

# Stop services
fm services stop

# Restart services
fm services restart
```

## Configuration

### fm config
Manage FM configuration.

```bash
# Show config
fm config show

# Set value
fm config set KEY VALUE

# Get value
fm config get KEY
```

## Advanced Operations

### Export/Import

```bash
# Export site (for backup/migration)
fm export BENCHNAME --output /path/to/backup

# Import site
fm import /path/to/backup --name newsite
```

### Clone Site
```bash
fm clone SOURCEBENCH NEWBENCH
```

## Troubleshooting Commands

### Check Health
```bash
fm info BENCHNAME
```

### View All Containers
```bash
fm ps

# With details
fm ps -a
```

### Clean Up
```bash
# Remove unused images
fm clean

# Remove stopped containers
fm clean --containers

# Remove all (dangerous)
fm clean --all
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Site not found |
| 4 | Docker error |

## Environment Variables

```bash
# Set FM home directory
export FM_HOME=/path/to/fm

# Set default Frappe version
export FM_DEFAULT_FRAPPE_BRANCH=version-15

# Enable debug output
export FM_DEBUG=1
```

## Configuration File

FM stores configuration in `~/.fm/config.yml`:

```yaml
# ~/.fm/config.yml
default_frappe_branch: version-15
default_environment: dev
default_admin_password: admin
docker_compose_version: "3.8"
```

Sources: Frappe Manager GitHub (rtCamp/Frappe-Manager)
```