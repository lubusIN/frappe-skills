```markdown
# Test Patterns Reference

## Overview
Common testing patterns and best practices for Frappe applications.

## Test Case Classes

### FrappeTestCase
Base class for unit and integration tests.

```python
from frappe.tests.utils import FrappeTestCase

class TestMyDocType(FrappeTestCase):
    def test_example(self):
        self.assertEqual(1 + 1, 2)
```

### IntegrationTestCase
For tests requiring full Frappe setup.

```python
from frappe.tests.utils import IntegrationTestCase

class TestWorkflow(IntegrationTestCase):
    def test_full_workflow(self):
        # Has access to full Frappe environment
        pass
```

## Common Test Patterns

### Testing Document Creation
```python
def test_document_creation(self):
    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": "Test Customer"
    })
    doc.insert()
    
    self.assertIsNotNone(doc.name)
    self.assertEqual(doc.customer_name, "Test Customer")
    
    # Verify it exists in DB
    exists = frappe.db.exists("Customer", doc.name)
    self.assertTrue(exists)
```

### Testing Validation Errors
```python
def test_validation_error(self):
    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": ""  # Required field empty
    })
    
    # Using assertRaises
    self.assertRaises(frappe.ValidationError, doc.insert)
    
    # Or with context manager for message check
    with self.assertRaises(frappe.ValidationError) as context:
        doc.insert()
    
    self.assertIn("required", str(context.exception).lower())
```

### Testing Computed Fields
```python
def test_computed_field(self):
    doc = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": "_Test Customer",
        "items": [
            {"item_code": "_Test Item", "qty": 5, "rate": 100},
            {"item_code": "_Test Item", "qty": 3, "rate": 200}
        ]
    })
    doc.insert()
    
    # Check computed total
    expected_total = (5 * 100) + (3 * 200)  # 1100
    self.assertEqual(doc.grand_total, expected_total)
```

### Testing Workflows (Submit/Cancel)
```python
def test_submit_workflow(self):
    doc = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": "_Test Customer",
        "items": [{"item_code": "_Test Item", "qty": 1, "rate": 100}]
    })
    doc.insert()
    
    # Test draft state
    self.assertEqual(doc.docstatus, 0)
    
    # Test submit
    doc.submit()
    self.assertEqual(doc.docstatus, 1)
    
    # Test cannot edit after submit
    doc.customer = "Other Customer"
    self.assertRaises(frappe.ValidationError, doc.save)
    
    # Test cancel
    doc.cancel()
    self.assertEqual(doc.docstatus, 2)
```

### Testing Permissions
```python
def test_permission_denied(self):
    # Create document as admin
    doc = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": "_Test Customer"
    })
    doc.insert()
    
    # Switch to restricted user
    frappe.set_user("guest@example.com")
    
    try:
        # Attempt unauthorized action
        doc.customer = "Other"
        self.assertRaises(frappe.PermissionError, doc.save)
    finally:
        frappe.set_user("Administrator")
```

### Testing API Methods
```python
def test_api_method(self):
    from my_app.api import process_order
    
    # Create test data
    order = frappe.get_doc({...})
    order.insert()
    
    # Call API method
    result = process_order(order.name, "approve")
    
    # Verify result
    self.assertEqual(result["status"], "success")
    
    # Verify side effects
    order.reload()
    self.assertEqual(order.status, "Approved")
```

### Testing with Mocks
```python
from unittest.mock import patch, MagicMock

def test_external_api_call(self):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.status_code = 200
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        from my_app.integrations import sync_to_external
        
        result = sync_to_external({"data": "test"})
        
        # Verify external call was made
        mock_post.assert_called_once()
        self.assertEqual(result["status"], "ok")
```

### Testing Events
```python
def test_document_events(self):
    # Track event calls
    events_fired = []
    
    original_validate = MyDoc.validate
    def track_validate(self):
        events_fired.append("validate")
        original_validate(self)
    
    with patch.object(MyDoc, 'validate', track_validate):
        doc = frappe.get_doc({...})
        doc.insert()
    
    self.assertIn("validate", events_fired)
```

### Testing Background Jobs
```python
def test_background_job(self):
    from my_app.jobs import process_batch
    
    # Execute job synchronously for testing
    with patch("frappe.enqueue") as mock_enqueue:
        # Trigger the job
        process_batch(filters={"status": "Pending"})
        
        # Verify job was enqueued
        mock_enqueue.assert_called()
```

### Testing Email
```python
def test_email_sent(self):
    with patch("frappe.sendmail") as mock_send:
        # Trigger action that sends email
        doc = frappe.get_doc(...)
        doc.submit()
        
        # Verify email was sent
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        self.assertEqual(call_args.kwargs["subject"], "Order Submitted")
```

## Database Testing Patterns

### Testing Queries
```python
def test_query_with_filters(self):
    # Create test data
    for i in range(5):
        frappe.get_doc({
            "doctype": "Task",
            "subject": f"Task {i}",
            "status": "Open" if i < 3 else "Closed"
        }).insert()
    
    # Test query
    open_tasks = frappe.get_list("Task", filters={"status": "Open"})
    self.assertEqual(len(open_tasks), 3)
```

### Testing Transactions
```python
def test_transaction_rollback(self):
    # Start transaction
    frappe.db.savepoint("test")
    
    try:
        # Create document
        doc = frappe.get_doc(...)
        doc.insert()
        
        # Simulate error
        raise Exception("Test error")
    except:
        # Rollback
        frappe.db.rollback(save_point="test")
    
    # Verify document was not created
    self.assertFalse(frappe.db.exists("MyDocType", doc.name))
```

## Test Data Patterns

### SetUp and TearDown
```python
class TestWithFixtures(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create shared test data
        cls.customer = cls.create_test_customer()
    
    @classmethod
    def tearDownClass(cls):
        # Cleanup shared data
        frappe.delete_doc("Customer", cls.customer.name, force=True)
        super().tearDownClass()
    
    def setUp(self):
        # Per-test setup
        self.order = self.create_test_order()
    
    def tearDown(self):
        # Per-test cleanup  
        frappe.delete_doc("Sales Order", self.order.name, force=True)
```

### Parameterized Tests
```python
from parameterized import parameterized

class TestCalculations(FrappeTestCase):
    @parameterized.expand([
        (10, 5, 15),
        (0, 0, 0),
        (-5, 5, 0),
        (100, 200, 300),
    ])
    def test_addition(self, a, b, expected):
        self.assertEqual(a + b, expected)
```

## Assertions Reference

```python
# Equality
self.assertEqual(actual, expected)
self.assertNotEqual(actual, expected)

# Truthiness
self.assertTrue(condition)
self.assertFalse(condition)

# None checks
self.assertIsNone(value)
self.assertIsNotNone(value)

# Container checks
self.assertIn(item, container)
self.assertNotIn(item, container)

# Type checks
self.assertIsInstance(obj, cls)

# Exceptions
self.assertRaises(ExceptionClass, callable, args)

# Approximate equality (for floats)
self.assertAlmostEqual(a, b, places=2)

# Greater/Less
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertGreaterEqual(a, b)
self.assertLessEqual(a, b)

# Length
self.assertEqual(len(collection), expected_length)
```

Sources: Testing, Unit Tests, pytest (official docs)
```