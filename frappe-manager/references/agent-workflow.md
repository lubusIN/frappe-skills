```markdown
# Agent Workflow Reference

## Overview
Optimized workflows for AI agents developing Frappe applications using Frappe Manager.

## Quick Start Workflow

### 1. Environment Setup
```bash
# Create isolated development environment
fm create devsite --apps erpnext:version-15 --environment dev
fm start devsite
```

### 2. Create Custom App
```bash
fm shell devsite
bench new-app my_custom_app
bench --site devsite install-app my_custom_app
exit
```

### 3. Development Cycle
```bash
# Make changes to app code in apps/my_custom_app/

# Test changes
fm shell devsite
bench --site devsite migrate
bench --site devsite run-tests --app my_custom_app
exit

# Check logs if issues
fm logs devsite -f
```

### 4. Reset if Needed
```bash
fm stop devsite
fm delete devsite --force
fm create devsite --apps erpnext:version-15 --environment dev
```

## Agent-Optimized Patterns

### Fast Iteration Loop
```bash
# One-liner for test iteration
fm shell devsite -c "bench --site devsite run-tests --app my_app"
```

### Check Changes Without Shell
```bash
# Run single command in container
docker exec -it devsite-frappe bench --site devsite migrate
```

### Verify Site Status
```bash
# Quick health check
fm info devsite
fm logs devsite --tail 20
```

## Directory Structure for Agents

```
~/frappe-manager/
├── devsite/                    # FM site directory
│   ├── workspace/
│   │   └── frappe-bench/
│   │       ├── apps/
│   │       │   ├── frappe/
│   │       │   ├── erpnext/
│   │       │   └── my_custom_app/  ← Your app code
│   │       └── sites/
│   │           └── devsite/
│   │               └── site_config.json
│   └── docker-compose.yml
```

## File Editing Workflow

### Edit from Host (Recommended)
```bash
# Files are mounted, edit directly on host
code ~/frappe-manager/devsite/workspace/frappe-bench/apps/my_custom_app/

# Or use VS Code with FM
fm code devsite
```

### Apply Changes
```bash
fm shell devsite
bench build --app my_custom_app  # For JS changes
bench --site devsite migrate      # For schema changes
bench --site devsite clear-cache  # For Python changes
exit
```

## Testing Strategies

### Run Single Test
```bash
fm shell devsite -c "bench --site devsite run-tests --module my_app.doctype.my_doc.test_my_doc"
```

### Run with Output
```bash
fm shell devsite -c "bench --site devsite run-tests --app my_app -v"
```

### Test Specific DocType
```bash
fm shell devsite -c "bench --site devsite run-tests --doctype 'My DocType'"
```

## Debugging Workflow

### Enable Debug Mode
```bash
fm shell devsite
bench set-config -g developer_mode 1
exit

# Open with debugger
fm code devsite --debugger
```

### Check Error Logs
```bash
# Recent errors
fm logs devsite | grep -i error | tail -20

# Follow live
fm logs devsite -f
```

### Console Debugging
```bash
fm shell devsite
bench --site devsite console
>>> doc = frappe.get_doc("My DocType", "XYZ")
>>> doc.status
>>> exit()
```

## Database Operations

### Quick DB Access
```bash
fm shell devsite -c "bench --site devsite mariadb -e 'SHOW TABLES;'"
```

### Backup Before Changes
```bash
fm shell devsite -c "bench --site devsite backup"
```

### Reset Database
```bash
fm shell devsite
bench --site devsite reinstall --yes
exit
```

## Multi-App Development

```bash
# Create shared environment
fm create multiapp --apps erpnext:version-15 --apps hrms:version-15

# Install your apps
fm shell multiapp
bench new-app app_one
bench new-app app_two
bench --site multiapp install-app app_one
bench --site multiapp install-app app_two
exit
```

## CI/CD Integration

### GitHub Actions Integration
```yaml
- name: Setup FM
  run: pipx install frappe-manager @
- name: Create Test Site
  run: |
    fm create testsite --apps erpnext:version-15
    fm shell testsite -c "bench --site testsite install-app ${{ github.workspace }}"

- name: Run Tests
  run: fm shell testsite -c "bench --site testsite run-tests --app my_app"
```

## Cleanup

### Daily Cleanup
```bash
# Remove stopped sites
fm clean --containers

# Remove old images
docker image prune -f
```

### Full Reset
```bash
# Remove all FM sites
fm list | xargs -I {} fm delete {} --force

# Clean Docker
docker system prune -af
```

## Quick Reference Card

| Task | Command |
|------|---------|
| Create site | `fm create mysite --apps erpnext` |
| Enter shell | `fm shell mysite` |
| Run tests | `fm shell mysite -c "bench --site mysite run-tests --app my_app"` |
| Check logs | `fm logs mysite -f` |
| Restart | `fm restart mysite` |
| Delete | `fm delete mysite --force` |

Sources: Frappe Manager, Agent Development Patterns
```