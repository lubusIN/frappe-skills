```markdown
# Docker Configuration Reference

## Overview
Advanced Docker configuration for Frappe Manager sites.

## Environment Variables

### Common Variables
```bash
# Database
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=your_site
DB_HOST=mariadb

# Redis
REDIS_CACHE=redis://redis-cache:6379
REDIS_QUEUE=redis://redis-queue:6379
REDIS_SOCKETIO=redis://redis-socketio:6379

# Frappe
FRAPPE_SITE=your-site.localhost
DEVELOPER_MODE=1
ADMIN_PASSWORD=admin
```

### Docker Compose Override

Create `docker-compose.override.yml` for custom configuration:

```yaml
# docker-compose.override.yml
version: "3.8"

services:
  frappe:
    environment:
      - DEVELOPER_MODE=1
      - FRAPPE_SENTRY_DSN=https://key@sentry.io/123
    volumes:
      - ./custom-config:/app/custom-config:ro
    ports:
      - "8001:8000"  # Different port
```

## Resource Limits

```yaml
services:
  frappe:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Database Configuration

### Custom MariaDB Settings

```yaml
services:
  mariadb:
    image: mariadb:10.6
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --max_allowed_packet=256M
      - --innodb_buffer_pool_size=1G
    environment:
      - MYSQL_ROOT_PASSWORD=root
```

### Persistent Data
```yaml
volumes:
  mariadb_data:
    driver: local
  
services:
  mariadb:
    volumes:
      - mariadb_data:/var/lib/mysql
```

## Redis Configuration

```yaml
services:
  redis-cache:
    image: redis:alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
  
  redis-queue:
    image: redis:alpine
    command: redis-server --appendonly yes
```

## Networking

### Custom Network
```yaml
networks:
  frappe_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

services:
  frappe:
    networks:
      frappe_network:
        ipv4_address: 172.28.0.10
```

### Expose to Host
```yaml
services:
  frappe:
    ports:
      - "8000:8000"      # Web
      - "9000:9000"      # Socket.IO
      - "6787:6787"      # Debugger (if enabled)
```

## Volume Mounts for Development

```yaml
services:
  frappe:
    volumes:
      # Mount local apps for live editing
      - ./apps/my_app:/workspace/frappe-bench/apps/my_app:cached
      
      # Persist sites data
      - sites_data:/workspace/frappe-bench/sites
      
      # Persist logs
      - ./logs:/workspace/frappe-bench/logs
```

## Multi-Site Configuration

```yaml
services:
  frappe:
    environment:
      - FRAPPE_SITE=site1.localhost
    volumes:
      - sites_data:/workspace/frappe-bench/sites
  
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
```

## Debugging Configuration

### Enable Xdebug
```yaml
services:
  frappe:
    environment:
      - XDEBUG_MODE=debug
      - XDEBUG_CONFIG=client_host=host.docker.internal client_port=9003
```

### VS Code Debug Config
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Frappe Python",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 6787
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/apps/my_app",
          "remoteRoot": "/workspace/frappe-bench/apps/my_app"
        }
      ]
    }
  ]
}
```

## Health Checks

```yaml
services:
  frappe:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
  
  mariadb:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Backup Configuration

```yaml
services:
  backup:
    image: frrouting/backup
    volumes:
      - sites_data:/backup/sites:ro
      - ./backups:/backup/output
    environment:
      - BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
```

## Production Overrides

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  frappe:
    environment:
      - DEVELOPER_MODE=0
    restart: unless-stopped
    deploy:
      replicas: 2
  
  nginx:
    restart: unless-stopped
  
  mariadb:
    restart: unless-stopped
```

Usage:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Sources: Docker Compose, Frappe Docker (official repos)
```