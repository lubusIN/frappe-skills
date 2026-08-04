# Reports

## Overview
Frappe supports three types of reports:
- **Report Builder**: Simple reports built using the UI
- **Query Report**: Reports generated from SQL queries
- **Script Report**: Reports with custom Python and JavaScript logic

## Report Builder
Basic reports created through the UI with filters, grouping, and field selection. No coding required.

## Query Report
Reports using a single SQL query. Created by System Manager and stored in the database.

### Creating a Query Report
1. Type "new report" in the awesomebar
2. Set Report Type as "Query Report"
3. Set the Reference DocType (controls access permissions)
4. Set the Module
5. Write your SQL query

### Columns and Filters (v13+)
Configure columns and filters in the Report document:
- Set label, width, and fieldtype for columns
- Filters can be used as variables in the query: `%(filter_name)s`

### Example Query
```sql
SELECT
    name,
    creation,
    production_item,
    qty,
    produced_qty,
    company
FROM `tabWork Order`
WHERE docstatus=1
AND ifnull(produced_qty,0) < qty
```

### Column Formatting (Old Style)
Format columns in the SELECT clause: `{label}:{fieldtype}/{options}:{width}`

```sql
SELECT
    `tabWork Order`.name as "Work Order:Link/Work Order:200",
    `tabWork Order`.creation as "Date:Date:120",
    `tabWork Order`.qty as "To Produce:Int:100"
FROM `tabWork Order`
```

## Script Report
Reports with complex logic using Python for data processing and JavaScript for UI customization.

### Creating a Script Report
1. Create a Report document with Type = "Script Report"
2. Set Is Standard = "Yes" (Developer Mode required)
3. Create the report folder structure in your app:
   ```
   your_app/
   └── module_name/
       └── report/
           └── report_name/
               ├── report_name.json
               ├── report_name.py
               └── report_name.js
   ```

### Python Script (`report_name.py`)
```python
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Name", "fieldname": "name", "fieldtype": "Link", "options": "DocType", "width": 200},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},
    ]

def get_data(filters):
    return frappe.get_all("DocType",
        filters=filters,
        fields=["name", "amount"]
    )
```

### JavaScript Script (`report_name.js`)
```javascript
frappe.query_reports["Report Name"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        }
    ],
    onload: function(report) {
        // Custom onload behavior
    },
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        // Custom formatting
        return value;
    }
};
```

## Standard vs Custom Reports
- **Standard**: Bundled with app, version controlled, requires Developer Mode
- **Custom**: Stored in database, user-editable, site-specific

## Print Formats for Reports
Create `{report-name}.html` in the Report folder for custom print formats (uses JS templating).

Sources: Reports, Script Report, Query Report, Report Builder (official docs)
