# App translations (multi-language)

## Overview
- Frappe supports translations for app strings to enable multi-language UI.
- Translations are typically stored in CSV files per language.

## Extract strings
- Use `bench get-app` or standard app structure to keep translatable strings in code.
- Use translation utilities to extract and update translation files.

## Translation files
- Store translations under `your_app/translations/`.
- Files are named by language (e.g., `en.csv`, `fr.csv`).

## Best practices
- Use clear, stable strings as translation keys.
- Avoid dynamically constructed strings when possible.
- Keep translations in app code for reuse across sites.

Sources: Translations (official docs)
