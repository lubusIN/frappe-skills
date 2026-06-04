```markdown
# Naming Patterns Reference

## Overview
Frappe provides flexible auto-naming for documents. The naming pattern is configured in the DocType's `autoname` property.

## Naming Options

### Field-Based Naming
Use a field value as the document name.

```json
{
  "autoname": "field:customer_name"
}
```

**Use Case:** When field uniquely identifies the record (e.g., Customer name)

### Naming Series
Counter-based naming with prefixes.

```json
{
  "autoname": "naming_series:",
  "fields": [
    {
      "fieldname": "naming_series",
      "fieldtype": "Select",
      "options": "ORD-.YYYY.-\nORD-.YYYY.-.###",
      "default": "ORD-.YYYY.-"
    }
  ]
}
```

**Format Codes:**
| Code | Description | Example |
|------|-------------|---------|
| `.YYYY.` | 4-digit year | 2026 |
| `.YY.` | 2-digit year | 26 |
| `.MM.` | 2-digit month | 02 |
| `.DD.` | 2-digit day | 12 |
| `.#####` | Counter (5 digits) | 00001 |
| `.###` | Counter (3 digits) | 001 |

**Examples:**
- `ORD-.YYYY.-` → ORD-2026-00001
- `INV-.YY.MM.-` → INV-26.02-00001
- `PRJ-####` → PRJ-0001
- `SO-.YYYY.-.###` → SO-2026-001

### Format Strings
Template-based naming with placeholders.

```json
{
  "autoname": "format:PRJ-{customer_abbr}-{####}"
}
```

**Placeholders:**
- `{fieldname}` — Field value
- `{####}` — Counter with specified digits
- `{YYYY}`, `{YY}`, `{MM}`, `{DD}` — Date parts
- `{#####}` — Auto-incrementing counter

**Examples:**
```json
// Customer abbreviation + counter
"autoname": "format:{customer_abbr}-{#####}"
// Result: ACME-00001

// Type prefix + year + counter
"autoname": "format:{type_prefix}-{YYYY}-{###}"
// Result: SVC-2026-001
```

### Hash (Random)
Random unique string.

```json
{
  "autoname": "hash"
}
```

**Result:** 10-character random string (e.g., "a1b2c3d4e5")

**Use Case:** When human-readable name isn't needed

### Prompt
Ask user to enter name manually.

```json
{
  "autoname": "Prompt"
}
```

**Use Case:** User-defined unique identifiers

### Custom Autoname
Define naming in controller.

```json
{
  "autoname": "autoname"
}
```

```python
class MyDoc(Document):
    def autoname(self):
        # Custom naming logic
        prefix = self.get_prefix()
        counter = self.get_next_counter()
        self.name = f"{prefix}-{counter:05d}"
    
    def get_prefix(self):
        return self.region[:3].upper()
    
    def get_next_counter(self):
        return frappe.db.sql("""
            SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(name, '-', -1) AS UNSIGNED)), 0) + 1
            FROM `tabMy Doc`
            WHERE name LIKE %s
        """, f"{self.get_prefix()}-%")[0][0]
```

## Naming Series Management

### Define Options
```json
{
  "fieldname": "naming_series",
  "fieldtype": "Select",
  "options": "ORD-.YYYY.-\nPO-.YYYY.-\nQUOT-.YYYY.-",
  "default": "ORD-.YYYY.-",
  "reqd": 1
}
```

### Set Default via Setup
Via Naming Series DocType:
1. Go to Setup > Naming Series
2. Select DocType
3. Add/modify series options
4. Set default series

### Company-Specific Series
```json
{
  "autoname": "naming_series:",
  "fields": [
    {
      "fieldname": "naming_series",
      "fieldtype": "Select",
      "options": "",
      "label": "Series"
    },
    {
      "fieldname": "company",
      "fieldtype": "Link",
      "options": "Company",
      "label": "Company"
    }
  ]
}
```

Configure per-company prefixes in Naming Series DocType.

## Advanced Naming

### Composite Names
```python
def autoname(self):
    # Customer + Year + Counter
    self.name = f"{self.customer}-{frappe.utils.nowdate()[:4]}-{self.get_counter():04d}"

def get_counter(self):
    key = f"{self.customer}-{frappe.utils.nowdate()[:4]}"
    return frappe.db.count("My Doc", {"name": ("like", f"{key}-%")}) + 1
```

### Slug-Based Names
```python
from frappe.utils import slug

def autoname(self):
    base_name = slug(self.title)
    self.name = self.get_unique_name(base_name)

def get_unique_name(self, base_name):
    name = base_name
    counter = 1
    while frappe.db.exists(self.doctype, name):
        name = f"{base_name}-{counter}"
        counter += 1
    return name
```

### UUID Names
```python
import uuid

def autoname(self):
    self.name = str(uuid.uuid4())
```

## Renaming Documents

### Via Code
```python
frappe.rename_doc("Customer", "Old Name", "New Name")

# With merge
frappe.rename_doc("Customer", "Duplicate", "Original", merge=True)
```

### Rename Events
```python
class MyDoc(Document):
    def after_rename(self, old_name, new_name, merge=False):
        # Update references in other documents
        self.update_references(old_name, new_name)
```

### Prevent Rename
```python
class MyDoc(Document):
    def before_rename(self, old_name, new_name, merge=False):
        if self.status == "Closed":
            frappe.throw(_("Cannot rename closed documents"))
```

## Best Practices

### Naming Series Guidelines
| Use Case | Pattern | Example |
|----------|---------|---------|
| Orders | `{TYPE}-.YYYY.-` | ORD-2026-00001 |
| Invoices | `{COMPANY}-.YY.MM.-` | ACME-26.02-001 |
| Internal refs | `{TYPE}{#####}` | TKT00001 |
| Projects | `{CLIENT}-{YYYY}-{###}` | ACME-2026-001 |

### Avoid
- Spaces in names (use hyphens or underscores)
- Special characters that may cause URL issues
- Very long names (keep under 140 chars)
- Relying on name for business logic (use fields instead)

### Counter Reset
Counters reset based on the date pattern:
- `.YYYY.` — Resets annually
- `.YY.MM.` — Resets monthly
- `.YY.MM.DD.` — Resets daily
- No date pattern — Never resets

Sources: Naming, Autoname, Naming Series (official docs)
```