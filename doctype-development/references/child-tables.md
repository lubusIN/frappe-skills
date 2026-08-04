```markdown
# Child Tables Reference

## Overview
Child tables implement one-to-many relationships in Frappe. A child DocType is embedded within a parent DocType and stores rows of related data.

## Creating a Child Table DocType

### 1. Define the Child DocType
```json
{
  "doctype": "DocType",
  "name": "Sales Order Item",
  "module": "Selling",
  "istable": 1,
  "fields": [
    {
      "fieldname": "item_code",
      "fieldtype": "Link",
      "options": "Item",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "qty",
      "fieldtype": "Float",
      "in_list_view": 1,
      "reqd": 1
    },
    {
      "fieldname": "rate",
      "fieldtype": "Currency",
      "in_list_view": 1
    },
    {
      "fieldname": "amount",
      "fieldtype": "Currency",
      "in_list_view": 1,
      "read_only": 1
    }
  ]
}
```

**Key Settings:**
- `istable: 1` — Marks as child table
- `in_list_view: 1` — Shows field in table grid

### 2. Add Table Field to Parent
```json
{
  "fieldname": "items",
  "fieldtype": "Table",
  "options": "Sales Order Item",
  "label": "Items",
  "reqd": 1
}
```

## Working with Child Tables in Python

### Reading Child Rows
```python
def get_item_total(self):
    total = 0
    for item in self.items:
        total += item.amount or 0
    return total

# Alternative: List comprehension
def get_item_codes(self):
    return [item.item_code for item in self.items]
```

### Adding Rows
```python
def add_item(self, item_code, qty, rate):
    self.append("items", {
        "item_code": item_code,
        "qty": qty,
        "rate": rate,
        "amount": qty * rate
    })

# With child table object
def add_item_row(self):
    row = self.append("items", {})
    row.item_code = "ITEM-001"
    row.qty = 1
    return row
```

### Modifying Rows
```python
def update_prices(self, new_rate):
    for item in self.items:
        item.rate = new_rate
        item.amount = item.qty * new_rate

# Using idx (1-based index)
def update_first_item(self):
    if self.items:
        self.items[0].qty = 10
```

### Removing Rows
```python
def remove_zero_qty_items(self):
    self.items = [item for item in self.items if item.qty > 0]

# Remove specific row
def remove_item(self, item_code):
    to_remove = []
    for item in self.items:
        if item.item_code == item_code:
            to_remove.append(item)
    for item in to_remove:
        self.remove(item)
```

### Clearing All Rows
```python
def clear_items(self):
    self.items = []
    # or
    self.set("items", [])
```

## Child Table Events

### Form Script (JavaScript)
```javascript
frappe.ui.form.on("Sales Order Item", {
    // Row added
    items_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.rate = 100;  // Default rate
    },
    
    // Row removed
    items_remove(frm, cdt, cdn) {
        calculate_total(frm);
    },
    
    // Field changed in row
    qty(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        calculate_total(frm);
    },
    
    rate(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", row.qty * row.rate);
        calculate_total(frm);
    },
    
    // Before row removed (return false to prevent)
    before_items_remove(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.is_mandatory) {
            frappe.msgprint(__("Cannot remove mandatory item"));
            return false;
        }
    }
});

function calculate_total(frm) {
    let total = 0;
    (frm.doc.items || []).forEach(row => {
        total += row.amount || 0;
    });
    frm.set_value("grand_total", total);
}
```

### Controller Validation
```python
def validate(self):
    self.validate_items()
    self.calculate_totals()

def validate_items(self):
    if not self.items:
        frappe.throw(_("At least one item is required"))
    
    seen_items = set()
    for item in self.items:
        if item.item_code in seen_items:
            frappe.throw(_("Duplicate item: {0}").format(item.item_code))
        seen_items.add(item.item_code)
        
        if item.qty <= 0:
            frappe.throw(_("Quantity must be positive for {0}").format(item.item_code))

def calculate_totals(self):
    self.total_qty = 0
    self.grand_total = 0
    
    for idx, item in enumerate(self.items, 1):
        item.idx = idx  # Ensure sequential idx
        item.amount = (item.qty or 0) * (item.rate or 0)
        self.total_qty += item.qty or 0
        self.grand_total += item.amount
```

## Child Table Properties

### Automatic Fields
Every child table row has these system fields:
- `parent` — Parent document name
- `parenttype` — Parent DocType name  
- `parentfield` — Field name in parent
- `idx` — Row index (1-based)
- `name` — Unique row identifier

### Accessing Parent
```python
# From child row
def get_parent_doc(child_row):
    return frappe.get_doc(child_row.parenttype, child_row.parent)

# In controller context
class SalesOrderItem(Document):
    def validate(self):
        parent = self.get_parent()
        if parent.status == "Closed":
            frappe.throw(_("Cannot modify closed order"))
```

## Querying Child Tables

### Get Child Rows
```python
# Via parent document
doc = frappe.get_doc("Sales Order", "SO-001")
for item in doc.items:
    print(item.item_code)

# Direct query
items = frappe.get_all("Sales Order Item",
    filters={"parent": "SO-001"},
    fields=["item_code", "qty", "amount"]
)
```

### Query with Parent Join
```python
# Using Query Builder
from frappe.query_builder import DocType

SOItem = DocType("Sales Order Item")
SO = DocType("Sales Order")

query = (
    frappe.qb.from_(SOItem)
    .join(SO).on(SOItem.parent == SO.name)
    .where(SO.status == "To Deliver")
    .select(SOItem.item_code, SOItem.qty, SO.customer)
)
items = query.run(as_dict=True)
```

### Aggregate Queries
```python
# Total qty per item across all orders
from frappe.query_builder.functions import Sum

SOItem = DocType("Sales Order Item")
query = (
    frappe.qb.from_(SOItem)
    .groupby(SOItem.item_code)
    .select(SOItem.item_code, Sum(SOItem.qty).as_("total_qty"))
)
```

## Common Patterns

### Copy Child Table
```python
def copy_items_from(self, source_doc):
    self.items = []
    for item in source_doc.items:
        self.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate
        })
```

### Child Table with Link to Another Parent
```python
# Multi-parent child table pattern (using Dynamic Link)
{
  "fieldname": "reference_doctype",
  "fieldtype": "Link",
  "options": "DocType"
},
{
  "fieldname": "reference_name", 
  "fieldtype": "Dynamic Link",
  "options": "reference_doctype"
}
```

### Conditional Child Table Fields
```javascript
frappe.ui.form.on("Parent DocType", {
    type(frm) {
        // Show/hide columns based on parent field
        frm.fields_dict.items.grid.toggle_display("discount", frm.doc.type === "Retail");
    }
});
```

## Best Practices

### Do
- Always iterate with `for item in self.items` (not by index)
- Recalculate `idx` in validate if rows can be reordered
- Use `in_list_view` for important fields
- Validate child data in parent's `validate` method

### Don't
- Don't query child tables separately if you have the parent doc
- Don't modify `idx` outside of controlled scenarios
- Don't use child tables for many-to-many (use Table MultiSelect or link tables)

Sources: Child Table, Table Field, Child DocType (official docs)
```