```markdown
# Test Fixtures Reference

## Overview
Fixtures provide test data for Frappe tests. They can be JSON records, Python setup functions, or programmatically created data.

## Types of Fixtures

### 1. JSON Test Records
Automatically loaded before tests run.

```json
// my_app/doctype/sample_doc/test_records.json
[
    {
        "doctype": "Sample Doc",
        "name": "Test Record 1",
        "title": "First Test Document",
        "status": "Open"
    },
    {
        "doctype": "Sample Doc", 
        "name": "Test Record 2",
        "title": "Second Test Document",
        "status": "Closed"
    }
]
```

**File location:** `<app>/<module>/doctype/<doctype>/test_records.json`

### 2. Dependency Fixtures
Specify DocTypes that must be loaded first.

```python
# my_app/doctype/sales_order/test_sales_order.py
test_dependencies = ["Customer", "Item", "Warehouse"]
```

### 3. Programmatic Fixtures
Create in setUp method.

```python
class TestSalesOrder(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        """Run once before all tests in this class."""
        super().setUpClass()
        cls.customer = create_test_customer()
        cls.items = create_test_items(5)
    
    def setUp(self):
        """Run before each test method."""
        self.order = create_test_order(self.customer, self.items)
    
    def tearDown(self):
        """Run after each test method."""
        frappe.delete_doc("Sales Order", self.order.name, force=True)
    
    @classmethod
    def tearDownClass(cls):
        """Run once after all tests in this class."""
        frappe.delete_doc("Customer", cls.customer.name, force=True)
        for item in cls.items:
            frappe.delete_doc("Item", item.name, force=True)
        super().tearDownClass()
```

## Creating Test Data

### Factory Functions
```python
# my_app/tests/fixtures.py
import frappe
from frappe.utils import random_string

def create_test_customer(name=None, **kwargs):
    """Create a test customer with defaults."""
    customer = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": name or f"Test Customer {random_string(5)}",
        "customer_type": "Company",
        "territory": "_Test Territory",
        **kwargs
    })
    customer.insert(ignore_permissions=True)
    return customer

def create_test_item(name=None, **kwargs):
    """Create a test item with defaults."""
    item = frappe.get_doc({
        "doctype": "Item",
        "item_code": name or f"TEST-ITEM-{random_string(5)}",
        "item_name": name or f"Test Item {random_string(5)}",
        "item_group": "Products",
        "stock_uom": "Nos",
        **kwargs
    })
    item.insert(ignore_permissions=True)
    return item

def create_test_order(customer, items, **kwargs):
    """Create a test sales order."""
    order = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer.name if hasattr(customer, 'name') else customer,
        "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
        "items": [
            {"item_code": item.name if hasattr(item, 'name') else item, "qty": 1, "rate": 100}
            for item in items
        ],
        **kwargs
    })
    order.insert(ignore_permissions=True)
    return order
```

### Using Factory Functions
```python
from my_app.tests.fixtures import create_test_customer, create_test_item, create_test_order

class TestSalesWorkflow(FrappeTestCase):
    def test_order_submission(self):
        customer = create_test_customer()
        items = [create_test_item() for _ in range(3)]
        order = create_test_order(customer, items)
        
        order.submit()
        self.assertEqual(order.docstatus, 1)
```

## Fixture Best Practices

### Use Unique Names
```python
from frappe.utils import random_string

def create_unique_customer():
    # ✅ Unique name prevents collisions
    return create_test_customer(name=f"Test Cust {random_string(8)}")

def create_collision_prone_customer():
    # ❌ Fixed name may collide with other tests
    return create_test_customer(name="Test Customer")
```

### Cleanup After Tests
```python
class TestWithCleanup(FrappeTestCase):
    def setUp(self):
        self.created_docs = []
    
    def tearDown(self):
        for doctype, name in self.created_docs:
            frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
    
    def track_for_cleanup(self, doc):
        self.created_docs.append((doc.doctype, doc.name))
        return doc
    
    def test_something(self):
        customer = self.track_for_cleanup(create_test_customer())
        # Test uses customer, cleanup handled automatically
```

### Minimal Fixtures
```python
# ❌ Bad: Loading too much data
def setUpClass(cls):
    # Creates 1000 orders - slow!
    cls.orders = [create_test_order() for _ in range(1000)]

# ✅ Good: Load minimum needed
def setUpClass(cls):
    cls.sample_order = create_test_order()
    
def test_pagination(self):
    # Create specific data for this test
    for _ in range(25):
        create_test_order().insert()
    # Test pagination
```

## Shared Fixtures Module

```python
# my_app/tests/fixtures/__init__.py
from .customers import create_test_customer, get_test_customer
from .items import create_test_item, get_test_items
from .orders import create_test_order

__all__ = [
    "create_test_customer",
    "get_test_customer", 
    "create_test_item",
    "get_test_items",
    "create_test_order"
]
```

```python
# my_app/tests/fixtures/customers.py
_test_customers = {}

def create_test_customer(key=None, **kwargs):
    """Create a test customer, optionally cached by key."""
    if key and key in _test_customers:
        return _test_customers[key]
    
    customer = frappe.get_doc({...})
    customer.insert(ignore_permissions=True)
    
    if key:
        _test_customers[key] = customer
    
    return customer

def get_test_customer(key):
    """Get a cached test customer."""
    return _test_customers.get(key)

def cleanup_test_customers():
    """Delete all cached test customers."""
    for name in list(_test_customers.keys()):
        frappe.delete_doc("Customer", _test_customers[name].name, force=True)
        del _test_customers[name]
```

## Loading External Data

### From CSV
```python
import csv

def load_test_data_from_csv(csv_path, doctype):
    """Load test records from CSV file."""
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = frappe.get_doc({"doctype": doctype, **row})
            doc.insert(ignore_permissions=True)
```

### From JSON
```python
import json

def load_test_data_from_json(json_path):
    """Load test records from JSON file."""
    with open(json_path) as f:
        records = json.load(f)
    
    for record in records:
        doc = frappe.get_doc(record)
        doc.insert(ignore_permissions=True)
```

## Fixture Isolation

### Transaction Rollback
```python
class TestWithRollback(FrappeTestCase):
    def setUp(self):
        frappe.db.savepoint("test_start")
    
    def tearDown(self):
        frappe.db.rollback(save_point="test_start")
    
    def test_something(self):
        # Changes rolled back after test
        customer = create_test_customer()
```

### Database Isolation
```python
class TestIsolated(FrappeTestCase):
    """Tests that need complete isolation."""
    
    @classmethod
    def setUpClass(cls):
        # Use a separate test database if needed
        pass
```

Sources: Testing, Unit Tests, Fixtures (official docs)
```