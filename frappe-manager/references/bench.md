# Bench Commands and App Setup

## Core Lifecycle
- `bench init <bench-path>`: create a new bench.
- `bench new-site <site>`: create a new site.
- `bench start`: run dev services (web, socketio, redis, etc.).

## Bench and App Layout
- A Frappe app is a Python package inside `frappe-bench/apps` and should be listed in `sites/apps.txt`.
- The `frappe` app is the framework itself; custom apps live alongside it.

## App Management
- Confirm you are in a bench directory: `bench find .`
- `bench new-app <app>`: scaffold a new app.
- `bench get-app <app> <git-url>`: fetch an app from a repo.
- `bench --site <site> install-app <app>`: install app on site.
- `bench --site <site> uninstall-app <app>`: remove app from site.

## Assets
- `bench build`: build assets for production.
- `bench build --app <app>`: build assets for a specific app.

## Migrations
- `bench migrate`: run migrations (schema, patches, etc.).
- Use migration patches for data fixes that must run during upgrades.
- Patches are Python functions referenced in `patches.txt` and executed by `bench migrate`.

## Testing
- `bench --site <site> run-tests`: run tests.
- `bench --site <site> run-ui-tests <app>`: run UI tests.

## Maintenance
- `bench clear-cache`: clear cache.
- `bench clear-website-cache`: clear website cache.
- `bench clear-logs`: clear logs.

## Backup and Restore
- `bench --site <site> backup`: backup site.
- `bench --site <site> restore <path>`: restore site.

## Scheduler
- `bench --site <site> enable-scheduler` / `disable-scheduler`.

Sources: Bench Commands, Install and Setup Bench, Apps, Create an App, Sites, Database Migrations, Patches (official docs)
