# Enterprise Patterns (CRM/Helpdesk-style apps)

Production-grade architectural patterns for building enterprise applications like CRM, Helpdesk, HRMS, and similar multi-entity systems.

## Data Model Design

### Core Entity Structure
- Use clear, normalized DocTypes for core entities (Lead, Contact, Ticket, SLA, Assignment)
- Define explicit relationships via Link fields and Dynamic Links
- Use child tables for activities, comments, timelines, and line items

### Naming and Identification
- Use `autoname` patterns: `naming_series`, `field:field_name`, or `hash`
- Consider human-readable names for customer-facing entities
- Use hash-based names for high-volume transactional records

### Example: Helpdesk Data Model
```
Ticket (parent)
├── ticket_type (Link: Ticket Type)
├── customer (Link: Customer)
├── assigned_to (Link: User)
├── status (Select)
├── priority (Link: Priority)
├── sla (Link: SLA)
└── activities (Table: Ticket Activity)
```

## Workflow and State Management

### State Machines
- Implement state transitions via Workflow DocType or `docstatus` for submission flow
- Use role-based transitions and approval chains
- Define allowed states and transitions explicitly

### Workflow Patterns
```python
# Check transition validity
def validate_transition(doc, new_status):
    allowed = get_allowed_transitions(doc.status, frappe.session.user)
    if new_status not in allowed:
        frappe.throw(f"Cannot transition from {doc.status} to {new_status}")
```

### docstatus Usage
| docstatus | Meaning | Use Case |
|-----------|---------|----------|
| 0 | Draft | Editable, not finalized |
| 1 | Submitted | Locked, can cancel |
| 2 | Cancelled | Soft delete, auditable |

## Permissions and Security

### Row-Level Permissions
- Use User Permissions to restrict access by entity (e.g., only own tickets)
- Combine with Role Permissions for field-level control
- Always re-check in RPC methods:

```python
@frappe.whitelist()
def update_ticket(name, status):
    doc = frappe.get_doc("Ticket", name)
    if not frappe.has_permission("Ticket", "write", doc):
        frappe.throw("Not permitted", frappe.PermissionError)
    doc.status = status
    doc.save()
```

### Permission Patterns
- Use `has_permission` hook for complex permission logic
- Implement team-based access via intermediate DocTypes
- Cache permission checks for batch operations

## Activity and Audit Trails

### Communication Log
- Use Comments for internal notes and activity tracking
- Use Communication DocType for customer interactions (email, calls)
- Link activities to parent documents via `reference_doctype` and `reference_name`

### Audit Trail Implementation
```python
def on_update(doc, method):
    if doc.has_value_changed("status"):
        frappe.get_doc({
            "doctype": "Activity Log",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "action": "Status Change",
            "data": f"{doc._doc_before_save.status} → {doc.status}"
        }).insert(ignore_permissions=True)
```

### Key Fields to Track
- Status changes
- Assignment changes
- SLA breaches
- Customer interactions
- Escalations

## SLA Management

### SLA DocType Structure
```
SLA
├── name
├── entity_type (Link: DocType)
├── conditions (Table: SLA Condition)
├── response_time (Duration)
├── resolution_time (Duration)
└── escalation_rules (Table: Escalation Rule)
```

### SLA Enforcement
```python
def apply_sla(doc):
    sla = get_applicable_sla(doc)
    if sla:
        doc.response_by = add_to_date(doc.creation, hours=sla.response_time)
        doc.resolution_by = add_to_date(doc.creation, hours=sla.resolution_time)
```

### SLA Breach Detection
- Use scheduled jobs to check approaching/breached SLAs
- Trigger Notification rules for SLA warnings
- Update breach flags on documents

## Assignment and Queue Management

### Assignment Patterns
- Use Assignment Rule DocType for automatic assignment
- Implement round-robin or load-balanced distribution
- Track assignment history in child table or Activity Log

### Queue Implementation
```python
def get_next_agent(queue):
    """Round-robin assignment within a queue"""
    agents = frappe.get_all("Queue Member", 
        filters={"queue": queue, "available": 1},
        fields=["user", "current_load"],
        order_by="current_load asc"
    )
    return agents[0].user if agents else None
```

### Queue Health Dashboards
- Show queue depth and aging
- Display agent workload distribution
- Track SLA compliance by queue

## Notifications and Escalations

### Notification Triggers
- SLA approaching breach
- Assignment changes
- Status transitions
- Customer replies
- Escalation events

### Escalation Chain
```
Level 1: Notify assigned agent
Level 2: Notify team lead (after X hours)
Level 3: Notify manager (after Y hours)
Level 4: Notify department head (after Z hours)
```

### Implementation
- Use Notification DocType with conditions
- Schedule background jobs for time-based escalations
- Track escalation level on document

## Integration Patterns

### External System Integration
- Centralize integrations in `integrations/` module
- Use background jobs for sync operations
- Implement retry logic with exponential backoff

### Common Integrations
| System | Pattern |
|--------|---------|
| Email | Email Account + Communication |
| Telephony | Webhook + Call Log DocType |
| External CRM | REST connector + sync job |
| Chat | Webhook + real-time events |

### Sync Job Template
```python
def sync_external_tickets():
    """Background job for external ticket sync"""
    last_sync = get_last_sync_timestamp()
    tickets = fetch_external_tickets(since=last_sync)
    
    for ticket in tickets:
        try:
            upsert_ticket(ticket)
        except Exception as e:
            log_sync_error(ticket, e)
    
    update_sync_timestamp()
```

## Reporting and Analytics

### Operational Reports
| Report | Purpose |
|--------|---------|
| SLA Compliance | Track response/resolution times |
| Backlog Aging | Identify stuck tickets |
| Agent Performance | Tickets resolved, avg resolution time |
| Queue Health | Volume, wait times by queue |

### Report Implementation
- Use Query Reports for SQL-based reports
- Use Script Reports for complex aggregations
- Build dashboards with Number Cards and Charts

### Example Query Report
```sql
SELECT
    assigned_to,
    COUNT(*) as total_tickets,
    AVG(TIMESTAMPDIFF(HOUR, creation, resolution_time)) as avg_resolution_hours,
    SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END) as breached
FROM `tabTicket`
WHERE creation BETWEEN %(from_date)s AND %(to_date)s
GROUP BY assigned_to
```

## Performance Considerations

### Query Optimization
- Index frequently filtered fields (status, assigned_to, customer)
- Use `frappe.get_list` with specific fields
- Paginate large result sets

### Caching Strategies
- Cache SLA configurations (change infrequently)
- Cache user permissions for batch operations
- Use Redis for real-time counters

### Background Processing
- Process bulk operations in background jobs
- Chunk large data migrations
- Use job queues for priority handling

## Templates and Examples

Reference the mini-app-template for implementation examples:
- Service layer: `assets/mini-app-template/your_app/services/`
- Background jobs: `assets/mini-app-template/your_app/background_jobs/`
- API patterns: `assets/mini-app-template/your_app/api.py`

## Sources

- Frappe Framework patterns for enterprise apps
- ERPNext CRM module architecture
- Frappe Helpdesk implementation patterns
