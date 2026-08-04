```markdown
# Workflow Patterns Reference

## Overview
Production-grade workflow patterns for enterprise Frappe applications.

## Workflow States Design

### State Machine Pattern
```python
# workflow_patterns.py
WORKFLOW_STATES = {
    "Draft": {
        "allowed_next": ["Pending Approval", "Cancelled"],
        "actions": ["submit_for_approval", "cancel"],
        "roles": ["Employee"]
    },
    "Pending Approval": {
        "allowed_next": ["Approved", "Rejected"],
        "actions": ["approve", "reject"],
        "roles": ["Manager"]
    },
    "Approved": {
        "allowed_next": ["In Progress", "Cancelled"],
        "actions": ["start_work", "cancel"],
        "roles": ["Manager", "Admin"]
    },
    "In Progress": {
        "allowed_next": ["Completed", "On Hold"],
        "actions": ["complete", "hold"],
        "roles": ["Employee"]
    },
    "Completed": {
        "allowed_next": [],
        "actions": [],
        "roles": [],
        "is_final": True
    },
    "Rejected": {
        "allowed_next": ["Draft"],
        "actions": ["restart"],
        "roles": ["Employee"]
    }
}
```

### Workflow JSON Definition
```json
{
  "workflow_name": "Request Approval Workflow",
  "document_type": "Request",
  "is_active": 1,
  "override_status": 1,
  "states": [
    {
      "state": "Draft",
      "doc_status": 0,
      "allow_edit": "Employee",
      "is_optional_state": 0
    },
    {
      "state": "Pending Approval",
      "doc_status": 0,
      "allow_edit": "Manager",
      "next_action_email_template": "Approval Required"
    },
    {
      "state": "Approved",
      "doc_status": 1,
      "allow_edit": "",
      "message": "Request has been approved"
    }
  ],
  "transitions": [
    {
      "state": "Draft",
      "action": "Submit for Approval",
      "next_state": "Pending Approval",
      "allowed": "Employee",
      "condition": "doc.amount > 0"
    },
    {
      "state": "Pending Approval",
      "action": "Approve",
      "next_state": "Approved",
      "allowed": "Manager",
      "condition": "doc.amount <= 10000 or frappe.session.user == doc.approver"
    }
  ]
}
```

## Multi-Level Approval

### Tiered Approval Matrix
```python
def get_required_approvers(doc):
    """Determine approvers based on document amount"""
    if doc.amount <= 1000:
        return [{"role": "Team Lead", "required": 1}]
    elif doc.amount <= 10000:
        return [
            {"role": "Team Lead", "required": 1},
            {"role": "Manager", "required": 1}
        ]
    elif doc.amount <= 100000:
        return [
            {"role": "Manager", "required": 1},
            {"role": "Director", "required": 1}
        ]
    else:
        return [
            {"role": "Director", "required": 1},
            {"role": "CEO", "required": 1}
        ]
```

### Approval Tracking DocType
```json
{
  "doctype": "Approval Entry",
  "fields": [
    {"fieldname": "reference_doctype", "fieldtype": "Link", "options": "DocType"},
    {"fieldname": "reference_name", "fieldtype": "Dynamic Link", "options": "reference_doctype"},
    {"fieldname": "approval_level", "fieldtype": "Int"},
    {"fieldname": "approver", "fieldtype": "Link", "options": "User"},
    {"fieldname": "status", "fieldtype": "Select", "options": "Pending\nApproved\nRejected"},
    {"fieldname": "approved_on", "fieldtype": "Datetime"},
    {"fieldname": "comments", "fieldtype": "Text"}
  ]
}
```

### Controller Integration
```python
class RequestDocument(Document):
    def on_update(self):
        if self.workflow_state == "Pending Approval":
            self.create_approval_entries()
    
    def create_approval_entries(self):
        approvers = get_required_approvers(self)
        for level, approver_config in enumerate(approvers):
            frappe.get_doc({
                "doctype": "Approval Entry",
                "reference_doctype": self.doctype,
                "reference_name": self.name,
                "approval_level": level + 1,
                "approver": self.get_approver_for_role(approver_config["role"]),
                "status": "Pending"
            }).insert(ignore_permissions=True)
    
    def check_all_approvals(self):
        pending = frappe.db.count("Approval Entry", {
            "reference_doctype": self.doctype,
            "reference_name": self.name,
            "status": "Pending"
        })
        return pending == 0
```

## Parallel Workflows

### Multiple Active Workflows
```python
def handle_parallel_workflows(doc, method):
    """Run multiple workflows in parallel"""
    workflows = [
        {"name": "Finance Approval", "condition": lambda d: d.requires_finance},
        {"name": "HR Approval", "condition": lambda d: d.requires_hr},
        {"name": "Legal Review", "condition": lambda d: d.amount > 100000}
    ]
    
    active_workflows = []
    for wf in workflows:
        if wf["condition"](doc):
            active_workflows.append(wf["name"])
            create_workflow_instance(doc, wf["name"])
    
    doc.db_set("active_workflows", ",".join(active_workflows))
```

## Escalation Patterns

### Time-Based Escalation
```python
def check_escalations():
    """Run via scheduler"""
    pending_docs = frappe.get_all("Request", filters={
        "workflow_state": "Pending Approval",
        "modified": ["<", add_days(nowdate(), -3)]
    })
    
    for doc in pending_docs:
        escalate_to_next_level(doc.name)
```

### Escalation Rules
```json
{
  "doctype": "Escalation Rule",
  "fields": [
    {"fieldname": "workflow_state", "fieldtype": "Data"},
    {"fieldname": "wait_days", "fieldtype": "Int"},
    {"fieldname": "escalate_to", "fieldtype": "Link", "options": "Role"},
    {"fieldname": "notification_template", "fieldtype": "Link", "options": "Email Template"}
  ]
}
```

## Workflow State Change Hooks

```python
# hooks.py
doc_events = {
    "Request": {
        "on_change": "my_app.workflows.handle_workflow_state_change"
    }
}

# workflows.py
def handle_workflow_state_change(doc, method):
    if doc.has_value_changed("workflow_state"):
        old_state = doc.get_doc_before_save().workflow_state
        new_state = doc.workflow_state
        
        # Log transition
        log_workflow_transition(doc, old_state, new_state)
        
        # Trigger state-specific actions
        state_handlers = {
            "Approved": on_approved,
            "Rejected": on_rejected,
            "Completed": on_completed
        }
        
        handler = state_handlers.get(new_state)
        if handler:
            handler(doc)
```

## Workflow Visualization

### Generate Workflow Diagram
```python
def generate_workflow_diagram(workflow_name):
    """Generate Mermaid diagram for workflow"""
    workflow = frappe.get_doc("Workflow", workflow_name)
    
    lines = ["graph TD"]
    for t in workflow.transitions:
        lines.append(f"    {t.state.replace(' ', '_')} -->|{t.action}| {t.next_state.replace(' ', '_')}")
    
    return "\n".join(lines)
```

## Best Practices

1. **Keep states descriptive** - Use verb-based names like "Pending Approval", "Under Review"
2. **Limit transitions** - Each state should have 2-3 max transitions
3. **Use conditions wisely** - Keep conditions simple, move complex logic to Python
4. **Document state purposes** - Add help text explaining what each state means
5. **Test edge cases** - Test all possible state transitions

Sources: Frappe Workflow Documentation, ERPNext Workflow Patterns
```