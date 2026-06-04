```markdown
# Virtual DocTypes Reference

## Overview
Virtual DocTypes (v13+) allow you to create DocTypes that don't store data in a database table. Instead, data is fetched from external sources like APIs, files, or other databases.

## When to Use Virtual DocTypes

- Display data from external APIs
- Connect to secondary databases
- Read from files (JSON, CSV)
- Create computed/aggregated views
- Integrate with external systems without data duplication

## Creating a Virtual DocType

### 1. Define the DocType
```json
{
  "doctype": "DocType",
  "name": "External Product",
  "module": "My App",
  "is_virtual": 1,
  "fields": [
    {
      "fieldname": "product_id",
      "fieldtype": "Data",
      "label": "Product ID",
      "in_list_view": 1
    },
    {
      "fieldname": "product_name",
      "fieldtype": "Data",
      "label": "Product Name",
      "in_list_view": 1
    },
    {
      "fieldname": "price",
      "fieldtype": "Currency",
      "label": "Price",
      "in_list_view": 1
    },
    {
      "fieldname": "stock",
      "fieldtype": "Int",
      "label": "Stock"
    }
  ]
}
```

**Key Setting:** `"is_virtual": 1`

### 2. Implement the Controller

```python
# my_app/doctype/external_product/external_product.py
import frappe
from frappe.model.document import Document
import requests

class ExternalProduct(Document):
    @staticmethod
    def get_list(args):
        """Return list of documents for list view."""
        products = fetch_from_api()
        
        # Apply filters if provided
        if args.get("filters"):
            products = apply_filters(products, args["filters"])
        
        # Apply pagination
        start = args.get("start", 0)
        page_length = args.get("page_length", 20)
        products = products[start:start + page_length]
        
        return products
    
    @staticmethod
    def get_count(args):
        """Return total count for pagination."""
        products = fetch_from_api()
        if args.get("filters"):
            products = apply_filters(products, args["filters"])
        return len(products)
    
    @staticmethod
    def get_stats(args):
        """Return stats for sidebar."""
        return {}

def fetch_from_api():
    """Fetch products from external API."""
    cache_key = "external_products_list"
    cached = frappe.cache().get_value(cache_key)
    
    if cached:
        return cached
    
    try:
        response = requests.get(
            "https://api.example.com/products",
            headers={"Authorization": f"Bearer {get_api_key()}"},
            timeout=10
        )
        response.raise_for_status()
        products = response.json()
        
        # Cache for 5 minutes
        frappe.cache().set_value(cache_key, products, expires_in_sec=300)
        return products
        
    except requests.RequestException as e:
        frappe.log_error(f"External API error: {e}")
        return []

def apply_filters(products, filters):
    """Apply Frappe-style filters to product list."""
    result = products
    for f in filters:
        field, op, value = f[0], f[1], f[2] if len(f) > 2 else f[1]
        if op == "=":
            result = [p for p in result if p.get(field) == value]
        elif op == "like":
            value = value.replace("%", "")
            result = [p for p in result if value.lower() in str(p.get(field, "")).lower()]
    return result

def get_api_key():
    return frappe.db.get_single_value("My Settings", "api_key")
```

## Required Methods

### get_list(args)
Returns list of documents. Called for list view and `frappe.get_list()`.

```python
@staticmethod
def get_list(args):
    """
    args contains:
    - filters: List of filter conditions
    - fields: List of fields to return
    - start: Pagination start index
    - page_length: Number of records
    - order_by: Sort field and direction
    """
    return [
        {"name": "PROD-001", "product_name": "Widget", "price": 99.99},
        {"name": "PROD-002", "product_name": "Gadget", "price": 149.99}
    ]
```

### get_count(args)
Returns total count for pagination.

```python
@staticmethod
def get_count(args):
    return 100  # Total records
```

### get_stats(args)
Returns statistics for sidebar filters.

```python
@staticmethod
def get_stats(args):
    return {
        "status": {"Active": 50, "Inactive": 30}
    }
```

## Loading Single Documents

For viewing individual documents:

```python
class ExternalProduct(Document):
    def load_from_db(self):
        """Load document from external source."""
        product_id = self.name
        product = fetch_single_product(product_id)
        
        if not product:
            frappe.throw(_("Product not found"))
        
        # Set document attributes
        self.product_id = product["id"]
        self.product_name = product["name"]
        self.price = product["price"]
        self.stock = product["stock"]
    
    def db_insert(self):
        """Create in external source."""
        create_product_in_api(self.as_dict())
    
    def db_update(self):
        """Update in external source."""
        update_product_in_api(self.name, self.as_dict())
    
    def delete(self):
        """Delete from external source."""
        delete_product_from_api(self.name)

def fetch_single_product(product_id):
    response = requests.get(f"https://api.example.com/products/{product_id}")
    if response.status_code == 200:
        return response.json()
    return None
```

## Virtual DocType from Database

Connect to a secondary database:

```python
import pymysql

class ExternalCustomer(Document):
    @staticmethod
    def get_list(args):
        conn = get_secondary_db()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT id as name, name as customer_name, email FROM customers"
                
                if args.get("filters"):
                    where_clauses = []
                    for f in args["filters"]:
                        where_clauses.append(f"{f[0]} = %s")
                    sql += " WHERE " + " AND ".join(where_clauses)
                
                sql += f" LIMIT {args.get('start', 0)}, {args.get('page_length', 20)}"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conn.close()

def get_secondary_db():
    config = frappe.get_single("External DB Config")
    return pymysql.connect(
        host=config.host,
        user=config.user,
        password=config.get_password("password"),
        database=config.database
    )
```

## Virtual DocType from File

Read from JSON/CSV files:

```python
import json
import csv

class FileBasedProduct(Document):
    @staticmethod
    def get_list(args):
        file_path = frappe.get_site_path("private", "products.json")
        
        with open(file_path) as f:
            products = json.load(f)
        
        # Add name field for Frappe compatibility
        for p in products:
            p["name"] = p.get("id", p.get("sku"))
        
        return products
    
    def load_from_db(self):
        products = self.get_list({})
        for p in products:
            if p["name"] == self.name:
                for key, value in p.items():
                    setattr(self, key, value)
                return
        frappe.throw(_("Product not found"))
```

## Caching Strategies

### Time-Based Cache
```python
def fetch_with_cache():
    cache_key = "virtual_doctype_data"
    data = frappe.cache().get_value(cache_key)
    
    if data is None:
        data = expensive_fetch()
        frappe.cache().set_value(cache_key, data, expires_in_sec=600)
    
    return data
```

### Invalidation-Based Cache
```python
def fetch_with_version_cache():
    version = frappe.cache().get_value("data_version") or 0
    cache_key = f"virtual_data_v{version}"
    
    data = frappe.cache().get_value(cache_key)
    if data is None:
        data = expensive_fetch()
        frappe.cache().set_value(cache_key, data)
    
    return data

def invalidate_cache():
    """Call when external data changes."""
    current = frappe.cache().get_value("data_version") or 0
    frappe.cache().set_value("data_version", current + 1)
```

## Limitations

- No automatic indexing
- No database-level filtering/sorting (must implement in code)
- No transactions across virtual and real DocTypes
- Links to Virtual DocTypes need manual handling
- Report Builder may not work (use Script Reports)

## Best Practices

1. **Always cache external calls** — Avoid hitting APIs on every request
2. **Implement pagination** — Don't fetch all records at once
3. **Handle errors gracefully** — Return empty lists, not exceptions
4. **Use timeouts** — Set reasonable timeouts for external calls
5. **Log errors** — Use `frappe.log_error()` for debugging
6. **Validate on write** — If supporting writes, validate before sending

Sources: Virtual DocType, Custom Data Sources (official docs)
```