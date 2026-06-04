# Frappe Manager (Docker-based dev/prod environment)

## Overview
Frappe Manager (FM) is a CLI tool by **rtCamp** that simplifies managing Frappe-based projects using Docker Compose. It streamlines the entire lifecycle from development to deployment.

**Note**: Frappe Manager is a third-party tool by rtCamp, not an official Frappe project. It's built on official [Frappe Docker](https://github.com/frappe/frappe_docker) images.

## Bench vs Frappe Manager
| Aspect | Bench | Frappe Manager |
|--------|-------|----------------|
| **Setup** | Native Python, manual dependencies | Docker-based, minimal host setup |
| **Isolation** | Shared host environment | Isolated containers per site |
| **Best for** | Production servers, direct control | Local dev, quick onboarding, reproducible envs |
| **Requirements** | Python, Node, MariaDB, Redis, etc. | Python 3.11+, Docker |

## Requirements
- Python 3.11 or higher
- Docker
- VSCode (optional, for development features)

## Installation
```bash
# Install stable version
pipx install frappe-manager

# Install latest develop
pipx install git+https://github.com/rtcamp/frappe-manager@develop

# Setup shell completion
fm --install-completion
```

## Quick Start
```bash
# Create your first site (dev environment, frappe version-15)
fm create mysite

# Create site with ERPNext
fm create mysite --apps erpnext:version-15

# Create site with multiple apps
fm create mysite --apps erpnext --apps hrms --environment dev
```

## Commands Reference

### Site Management
```bash
fm create <benchname>     # Create a new bench/site
fm delete <benchname>     # Delete a bench
fm start <benchname>      # Start a bench
fm stop <benchname>       # Stop a bench
fm list                   # List all benches
fm info <benchname>       # Show bench information
fm logs <benchname> -f    # View logs (follow mode)
fm update <benchname>     # Update bench
```

### Development
```bash
fm shell <benchname>              # Access shell inside container
fm code <benchname>               # Open in VSCode
fm code <benchname> --debugger    # Open in VSCode with debugger
```

### Services & SSL
```bash
fm services                       # Manage global services
fm ssl <benchname>                # Manage SSL for a bench
```

## fm create Options
```bash
fm create [OPTIONS] BENCHNAME

Options:
  -a, --apps TEXT              Apps to install (format: app or app:branch)
  --environment, --env         Environment type: dev|prod (default: dev)
  --developer-mode             Toggle developer mode: enable|disable
  --frappe-branch TEXT         Frappe branch (default: version-15)
  --admin-pass TEXT            Admin password (default: admin)
  --ssl                        Enable SSL: letsencrypt|disable
  --template / --no-template   Create template bench
```

### Prebaked Apps
These apps are prebaked in Frappe Docker images (faster installation):
- `frappe`: version-15
- `erpnext`: version-15
- `hrms`: version-15

### Examples
```bash
# Basic site with frappe only
fm create example

# Site with frappe develop branch
fm create example --frappe-branch develop

# Site with ERPNext and HRMS
fm create example --apps erpnext --apps hrms

# Production site with SSL
fm create example.com --apps erpnext --env prod --ssl letsencrypt
```

## Production Setup
```bash
# Create production site with SSL (HTTP01 challenge)
fm create example.com --environment prod \
  --ssl letsencrypt \
  --letsencrypt-preferred-challenge http01 \
  --letsencrypt-email admin@example.com

# Create production site with SSL (DNS01 challenge)
fm create example.com --environment prod \
  --ssl letsencrypt \
  --letsencrypt-preferred-challenge dns01 \
  --letsencrypt-email admin@example.com
```

## Working Inside Containers

### fm shell
Access the container shell to run bench commands:
```bash
fm shell mysite

# Inside container:
bench new-app my_app
bench --site mysite install-app my_app
bench migrate
bench build --app my_app
```

### fmx CLI (Inside Container)
The `fmx` CLI manages internal services (Frappe, Workers, Scheduler):
```bash
fm shell mysite

# Inside container:
fmx status              # Check service status
fmx restart             # Restart Frappe services
fmx start               # Start services
fmx stop                # Stop services
```

## Operation Notes
- Sites are named like `example.localhost` (accessible at http://example.localhost)
- For custom domains without DNS, add entries to `/etc/hosts`
- Run as non-root user
- After updating Python packages, use `bench restart` or `fmx restart`
- In `prod` environment, developer mode and admin tools are disabled by default
- In `dev` environment, developer mode and admin tools are enabled by default

## Sample Dev Workflow
```bash
# 1. Create dev site with ERPNext
fm create devsite --apps erpnext:version-15 --environment dev

# 2. Start the site
fm start devsite

# 3. Access shell and create custom app
fm shell devsite
bench new-app my_custom_app
bench --site devsite install-app my_custom_app
exit

# 4. Open in VSCode with debugger
fm code devsite --debugger
```

## Agent-Driven Development Workflow

Frappe Manager is the recommended environment for AI code agents (vibe coding) to develop and test Frappe apps. It provides isolated, reproducible environments that agents can create, test, and reset.

### Why Frappe Manager for Agents
- **Isolated environments**: Each site runs in Docker containers—no host pollution
- **Quick reset**: Delete and recreate sites to test from clean state
- **Minimal dependencies**: Only Docker needed on host
- **Shell access**: Agents can run commands via `fm shell`
- **Reproducible**: Same environment across different machines

### Agent Workflow

```bash
# 1. Setup: Create a fresh dev environment
fm create testsite --apps erpnext:version-15 --environment dev
fm start testsite

# 2. Develop: Enter shell and create/modify app
fm shell testsite
bench new-app my_app
bench --site testsite install-app my_app
# ... make code changes ...
exit

# 3. Test: Run tests inside the container
fm shell testsite
bench --site testsite run-tests --app my_app
exit

# 4. Verify: Check logs for errors
fm logs testsite -f

# 5. Reset (if needed): Start fresh
fm stop testsite
fm delete testsite
fm create testsite --apps erpnext:version-15 --environment dev
```

### Key Commands for Agents

| Task | Command |
|------|---------|
| Create environment | `fm create <site> --environment dev` |
| Start environment | `fm start <site>` |
| Run shell command | `fm shell <site>` then run commands |
| View logs | `fm logs <site> -f` |
| Check site info | `fm info <site>` |
| List all sites | `fm list` |
| Stop environment | `fm stop <site>` |
| Delete environment | `fm delete <site>` |
| Restart services | `fm shell <site>` then `fmx restart` |

### Testing Inside Container
```bash
fm shell testsite

# Run all tests for an app
bench --site testsite run-tests --app my_app

# Run specific test module
bench --site testsite run-tests --module my_app.tests.test_feature

# Run with verbose output
bench --site testsite run-tests --app my_app -v

# Migrate after schema changes
bench --site testsite migrate

# Clear cache between tests
bench --site testsite clear-cache
```

## References
- https://github.com/rtCamp/Frappe-Manager
- https://github.com/rtCamp/Frappe-Manager/wiki
- https://github.com/frappe/frappe_docker (base images)
