```markdown
# Field Types Reference

## Overview
Frappe DocTypes use typed fields to define schema. Each field type has specific behavior, validation, and UI rendering.

## Data Fields

### Data
- **Purpose**: Single-line text input
- **Max Length**: 140 characters (default), configurable up to 255
- **Options**: Can specify validation pattern (Email, URL, Phone, Name)
- **Example**:
```json
{
  "fieldname": "email",
  "fieldtype": "Data",
  "options": "Email",
  "label": "Email Address"
}
```

### Small Text
- **Purpose**: Multi-line text, limited length
- **Max Length**: 255 characters
- **Use Case**: Short descriptions, notes

### Text
- **Purpose**: Multi-line text, unlimited length
- **Storage**: TEXT column in database
- **Use Case**: Detailed descriptions, content

### Long Text
- **Purpose**: Extended text content
- **Storage**: LONGTEXT column
- **Use Case**: Very large text blocks

### Text Editor
- **Purpose**: Rich text editing with HTML
- **Features**: WYSIWYG editor, formatting toolbar
- **Storage**: Stores HTML content

### Markdown Editor
- **Purpose**: Markdown text with preview
- **Use Case**: Documentation, formatted content

### Code
- **Purpose**: Code editing with syntax highlighting
- **Options**: Language (Python, JavaScript, HTML, CSS, JSON, etc.)
- **Example**:
```json
{
  "fieldname": "custom_script",
  "fieldtype": "Code",
  "options": "Python",
  "label": "Custom Script"
}
```

### HTML Editor
- **Purpose**: Direct HTML editing
- **Use Case**: Email templates, custom HTML content

## Numeric Fields

### Int
- **Purpose**: Integer values
- **Storage**: INT column
- **Validation**: Rounds floats to integers

### Float
- **Purpose**: Decimal numbers
- **Precision**: Standard float precision

### Currency
- **Purpose**: Money values with currency formatting
- **Options**: Currency field reference or default currency
- **Display**: Formatted with currency symbol
- **Example**:
```json
{
  "fieldname": "amount",
  "fieldtype": "Currency",
  "options": "currency",
  "label": "Amount"
}
```

### Percent
- **Purpose**: Percentage values
- **Display**: Shows % symbol
- **Range**: 0-100 (soft limit)

## Date & Time Fields

### Date
- **Purpose**: Date only (no time)
- **Format**: YYYY-MM-DD
- **UI**: Date picker

### Time
- **Purpose**: Time only (no date)
- **Format**: HH:MM:SS

### Datetime
- **Purpose**: Date and time combined
- **Format**: YYYY-MM-DD HH:MM:SS
- **Storage**: DATETIME column

### Duration
- **Purpose**: Time duration in seconds
- **Display**: Formatted as HH:MM:SS or days
- **Storage**: Float (seconds)

## Selection Fields

### Select
- **Purpose**: Dropdown selection from predefined options
- **Options**: Newline-separated values
- **Example**:
```json
{
  "fieldname": "status",
  "fieldtype": "Select",
  "options": "Open\nIn Progress\nClosed",
  "default": "Open"
}
```

### Check
- **Purpose**: Boolean checkbox
- **Storage**: 0 or 1
- **Example**:
```json
{
  "fieldname": "is_active",
  "fieldtype": "Check",
  "default": 1
}
```

## Link Fields

### Link
- **Purpose**: Reference to another DocType
- **Options**: Target DocType name
- **Features**: Autocomplete, navigation to linked record
- **Example**:
```json
{
  "fieldname": "customer",
  "fieldtype": "Link",
  "options": "Customer",
  "reqd": 1
}
```

### Dynamic Link
- **Purpose**: Link where target DocType varies
- **Options**: Field containing the DocType name
- **Example**:
```json
{
  "fieldname": "link_doctype",
  "fieldtype": "Link",
  "options": "DocType",
  "label": "Link DocType"
},
{
  "fieldname": "link_name",
  "fieldtype": "Dynamic Link",
  "options": "link_doctype",
  "label": "Link Name"
}
```

### Table
- **Purpose**: Child table (one-to-many relationship)
- **Options**: Child DocType name (must have `istable: 1`)
- **Example**:
```json
{
  "fieldname": "items",
  "fieldtype": "Table",
  "options": "Sales Order Item",
  "label": "Items"
}
```

### Table MultiSelect
- **Purpose**: Multi-select via child table
- **Options**: Link DocType for selection
- **Use Case**: Many-to-many relationships

## Media Fields

### Attach
- **Purpose**: Single file attachment
- **Storage**: File URL path
- **Features**: Upload, preview

### Attach Image
- **Purpose**: Image attachment with preview
- **Features**: Image preview in form

### Image
- **Purpose**: Display image from another field
- **Options**: Field containing image URL
- **Read Only**: Yes

### Signature
- **Purpose**: Digital signature capture
- **Storage**: Base64 encoded image

## Special Fields

### Password
- **Purpose**: Encrypted password storage
- **Display**: Masked input
- **Storage**: Encrypted (hashed for auth)

### Read Only
- **Purpose**: Display computed/derived values
- **Note**: Value must be set via controller

### Geolocation
- **Purpose**: Geographic coordinates
- **Storage**: GeoJSON format
- **Features**: Map picker

### Color
- **Purpose**: Color selection
- **Storage**: Hex code (#RRGGBB)
- **UI**: Color picker

### Rating
- **Purpose**: Star rating input
- **Range**: 0-5 (configurable)

### Barcode
- **Purpose**: Barcode display
- **Options**: Barcode type (Code128, QR, etc.)

### JSON
- **Purpose**: JSON data storage and editing
- **Storage**: TEXT column with JSON
- **UI**: JSON editor

### HTML
- **Purpose**: Display static HTML content
- **Options**: HTML content to display
- **Note**: Not editable by user

### Heading
- **Purpose**: Section heading label
- **Note**: Display only, no data

## Layout Fields

### Section Break
- **Purpose**: Start new form section
- **Options**: Collapsible, hidden by default
- **Example**:
```json
{
  "fieldname": "details_section",
  "fieldtype": "Section Break",
  "label": "Details",
  "collapsible": 1
}
```

### Column Break
- **Purpose**: Start new column within section
- **Note**: Creates multi-column layout

### Tab Break
- **Purpose**: Start new tab (v14+)
- **Example**:
```json
{
  "fieldname": "settings_tab",
  "fieldtype": "Tab Break",
  "label": "Settings"
}
```

### Fold
- **Purpose**: Collapse section below by default
- **Note**: All fields after Fold are hidden until expanded

## Field Properties

### Common Properties
| Property | Type | Description |
|----------|------|-------------|
| `fieldname` | String | API name (snake_case) |
| `fieldtype` | String | Field type |
| `label` | String | Display label |
| `reqd` | Int | Required (0/1) |
| `default` | Mixed | Default value |
| `hidden` | Int | Hidden (0/1) |
| `read_only` | Int | Read only (0/1) |
| `unique` | Int | Unique constraint (0/1) |
| `in_list_view` | Int | Show in list view |
| `in_standard_filter` | Int | Show in filter panel |
| `bold` | Int | Bold label |
| `allow_on_submit` | Int | Editable after submit |
| `depends_on` | String | Visibility condition |
| `mandatory_depends_on` | String | Required condition |
| `read_only_depends_on` | String | Read-only condition |

### Conditional Visibility
```json
{
  "fieldname": "discount",
  "fieldtype": "Currency",
  "depends_on": "eval:doc.apply_discount",
  "mandatory_depends_on": "eval:doc.apply_discount && doc.discount_type=='Fixed'"
}
```

## Field Naming Conventions

- Use `snake_case` for fieldnames
- Prefix with verb for actions: `is_`, `has_`, `can_`
- Use consistent suffixes: `_date`, `_time`, `_by`, `_at`
- Avoid reserved names: `name`, `owner`, `creation`, `modified`, `docstatus`

Sources: Field Types, DocType, Database Schema (official docs)
```