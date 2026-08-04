# DocTypes

## Core Concepts
- DocType is the schema/model definition for documents in Frappe.
- Standard DocTypes live in app code; Custom DocTypes are created via the UI and stored in the database.

## DocType Types
- **Standard**: Normal DocType with multiple records.
- **Single**: One record only; store configuration or singleton settings.
- **Child Table**: `istable = 1`, rows owned by parent DocType; no standalone permissions.
- **Submittable**: Uses `docstatus` workflow (0=Draft, 1=Submitted, 2=Cancelled).
- **Tree**: Hierarchical DocType with parent/child relationships.
- **Virtual** (v13+): DocTypes with custom data sources (external APIs, secondary DBs, JSON/CSV files); no database table created.

## Structure and Fields
- DocType fields define the schema and UI controls.
- Permissions are defined per role on the DocType.
- Controller classes are Python classes named after the DocType in `doctype/<doctype_name>/<doctype_name>.py`.

### Field Patterns
- Use **Data**, **Select**, **Date**, **Datetime**, **Link**, **Check**, **Int/Float**, **Currency**, **Text**, and **Small Text** for most data.
- Use **Link** for relations; use **Dynamic Link** when the target DocType varies by field.
- Use **Table** fields for child tables (one-to-many); ensure child DocType is marked **Child Table**.
- Use **Section Break**, **Column Break**, and **Tab Break** for layout.
- Use **Read Only** for computed fields; compute in server logic or client script.
- Use **Auto Name** rules (`naming_series:` or `field:`) to control identifiers.

## Controller Lifecycle
- Common hooks: `validate`, `before_save`, `after_insert`, `on_submit`, `on_cancel`.
- Keep controller code lightweight; delegate heavy logic to service modules.

## Actions and Links
- Use **Custom Buttons** in form scripts to trigger actions.
- Use **Dashboard** and **Links** to show related records.

## Customizing DocTypes
- **Custom Fields**: Add fields without changing app code; stored per site.
- **Custom DocTypes**: Created from UI; stored in DB, can be exported in developer mode.
- **Customize Form**: Reorder fields and set properties without code changes.
- Prefer custom apps for reusable changes; use Custom Fields for quick site-specific tweaks.

## Developer Mode Flow
- Enable developer mode to export DocTypes to files.
- Exported DocTypes are stored under the app module path in `doctype/<doctype_name>/`.
- Use **Export Customizations** to export Custom Fields and Custom DocTypes.

## Examples

### Naming Series (JSON)
```json
{
  "autoname": "naming_series:",
  "naming_series": "TS-.YYYY.-",
  "fields": [
    {
      "fieldname": "naming_series",
      "fieldtype": "Select",
      "label": "Series",
      "options": "TS-.YYYY.-\nTS-.YYYY.-.###",
      "reqd": 1
    }
  ]
}
```

### Child Table Field (JSON)
```json
{
  "fieldname": "items",
  "fieldtype": "Table",
  "label": "Items",
  "options": "Sample Doc Item"
}
```

### Workflow States (concept)
- Create a **Workflow** for a DocType with states like `Draft -> Approved -> Rejected`.
- Map transitions to roles (e.g., only `Manager` can move to `Approved`).

## Templates
- Single DocType: `/assets/mini-app-template/your_app/doctype/sample_single/sample_single.json`
- Tree DocType: `/assets/mini-app-template/your_app/doctype/sample_tree/sample_tree.json`
- Submittable DocType: `/assets/mini-app-template/your_app/doctype/sample_submittable/sample_submittable.json`
- Child DocType: `/assets/mini-app-template/your_app/doctype/sample_doc_item/sample_doc_item.json`
- Dashboard/Links: `/assets/mini-app-template/your_app/dashboard/sample_doc_dashboard.json`
- Dynamic Link fields: `/assets/mini-app-template/your_app/doctype/sample_doc/sample_doc_dynamic_link.json`
- Naming series: `/assets/mini-app-template/your_app/doctype/sample_doc/sample_doc_naming_series.json`
- Workflow: `/assets/mini-app-template/your_app/workflow/sample_doc_workflow.json`
- DocType with workflow and child table: `/assets/mini-app-template/your_app/doctype/sample_doc/sample_doc.json`

Sources: DocType, Child Table, Submittable, Tree, Custom Fields, Customize Form, Developer Mode, Dashboard, Naming Series, Dynamic Link, Workflow (official docs)
