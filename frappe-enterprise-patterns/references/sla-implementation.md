```markdown
# SLA Implementation Reference

## Overview
Service Level Agreement implementation patterns for Frappe applications like CRM and Helpdesk.

## SLA DocType Structure

### Main SLA Definition
```json
{
  "doctype": "Service Level Agreement",
  "fields": [
    {"fieldname": "sla_name", "fieldtype": "Data", "reqd": 1},
    {"fieldname": "enabled", "fieldtype": "Check", "default": 1},
    {"fieldname": "document_type", "fieldtype": "Link", "options": "DocType", "reqd": 1},
    {"fieldname": "default_sla", "fieldtype": "Check"},
    {"fieldname": "condition", "fieldtype": "Code", "options": "Python"},
    {"fieldname": "apply_sla_for_resolution", "fieldtype": "Check"},
    {"fieldname": "priorities", "fieldtype": "Table", "options": "SLA Priority"}
  ]
}
```

### SLA Priority Child Table
```json
{
  "doctype": "SLA Priority",
  "fields": [
    {"fieldname": "priority", "fieldtype": "Link", "options": "Issue Priority"},
    {"fieldname": "response_time", "fieldtype": "Duration"},
    {"fieldname": "resolution_time", "fieldtype": "Duration"}
  ],
  "istable": 1
}
```

## SLA Application Logic

### Base SLA Controller
```python
# sla_controller.py
import frappe
from frappe.utils import now_datetime, time_diff_in_seconds, add_to_date

class SLAController:
    def __init__(self, doc):
        self.doc = doc
        self.sla = self.get_applicable_sla()
    
    def get_applicable_sla(self):
        """Find SLA matching document conditions"""
        slas = frappe.get_all("Service Level Agreement", 
            filters={
                "document_type": self.doc.doctype,
                "enabled": 1
            },
            order_by="default_sla asc"  # Non-default first to check conditions
        )
        
        for sla in slas:
            sla_doc = frappe.get_doc("Service Level Agreement", sla.name)
            if self.check_sla_condition(sla_doc):
                return sla_doc
        
        return None
    
    def check_sla_condition(self, sla):
        """Evaluate SLA condition"""
        if not sla.condition:
            return True
        
        return frappe.safe_eval(sla.condition, 
            eval_locals={"doc": self.doc})
    
    def apply_sla(self):
        """Apply SLA times to document"""
        if not self.sla:
            return
        
        priority_row = self.get_priority_row()
        if not priority_row:
            return
        
        now = now_datetime()
        
        # Calculate response due
        if priority_row.response_time:
            self.doc.response_by = self.calculate_due_date(
                now, priority_row.response_time)
        
        # Calculate resolution due
        if self.sla.apply_sla_for_resolution and priority_row.resolution_time:
            self.doc.resolution_by = self.calculate_due_date(
                now, priority_row.resolution_time)
        
        self.doc.service_level_agreement = self.sla.name
    
    def get_priority_row(self):
        """Get SLA times for document priority"""
        for row in self.sla.priorities:
            if row.priority == self.doc.priority:
                return row
        return None
    
    def calculate_due_date(self, start, duration_seconds):
        """Calculate due date considering support hours"""
        support_hours = self.get_support_hours()
        if support_hours:
            return self.calculate_with_support_hours(start, duration_seconds, support_hours)
        return add_to_date(start, seconds=duration_seconds)
```

## Support Hours / Business Hours

### Support Hours DocType
```json
{
  "doctype": "Support Hours",
  "fields": [
    {"fieldname": "support_hours_name", "fieldtype": "Data", "reqd": 1},
    {"fieldname": "enabled", "fieldtype": "Check", "default": 1},
    {"fieldname": "day_rows", "fieldtype": "Table", "options": "Support Hours Day"}
  ]
}
```

### Support Hours Day Child Table
```json
{
  "doctype": "Support Hours Day",
  "fields": [
    {"fieldname": "day", "fieldtype": "Select", "options": "Monday\nTuesday\nWednesday\nThursday\nFriday\nSaturday\nSunday"},
    {"fieldname": "start_time", "fieldtype": "Time"},
    {"fieldname": "end_time", "fieldtype": "Time"},
    {"fieldname": "is_working_day", "fieldtype": "Check", "default": 1}
  ],
  "istable": 1
}
```

### Business Hours Calculator
```python
def calculate_business_hours(start_dt, end_dt, support_hours_name):
    """Calculate elapsed business hours between two datetimes"""
    support_hours = frappe.get_doc("Support Hours", support_hours_name)
    
    total_seconds = 0
    current = start_dt
    
    while current < end_dt:
        day_name = current.strftime("%A")
        day_row = get_day_row(support_hours, day_name)
        
        if day_row and day_row.is_working_day:
            day_start = datetime.combine(current.date(), day_row.start_time)
            day_end = datetime.combine(current.date(), day_row.end_time)
            
            # Calculate overlap
            overlap_start = max(current, day_start)
            overlap_end = min(end_dt, day_end)
            
            if overlap_start < overlap_end:
                total_seconds += (overlap_end - overlap_start).total_seconds()
        
        current = datetime.combine(current.date() + timedelta(days=1), time.min)
    
    return total_seconds
```

## SLA Breach Detection

### Real-Time Breach Check
```python
def check_sla_breaches():
    """Scheduled job to check for SLA breaches"""
    now = now_datetime()
    
    # Check response breaches
    breached_docs = frappe.get_all("Issue", filters={
        "status": ["not in", ["Closed", "Resolved"]],
        "first_responded_on": ["is", "not set"],
        "response_by": ["<", now]
    })
    
    for doc in breached_docs:
        mark_sla_breach(doc.name, "response")
    
    # Check resolution breaches
    resolution_breached = frappe.get_all("Issue", filters={
        "status": ["not in", ["Closed", "Resolved"]],
        "resolution_by": ["<", now]
    })
    
    for doc in resolution_breached:
        mark_sla_breach(doc.name, "resolution")

def mark_sla_breach(docname, breach_type):
    """Mark document as breached and notify"""
    doc = frappe.get_doc("Issue", docname)
    
    if breach_type == "response":
        doc.db_set("response_sla_status", "Breached", update_modified=False)
    else:
        doc.db_set("resolution_sla_status", "Breached", update_modified=False)
    
    # Send notification
    send_breach_notification(doc, breach_type)
```

## SLA Status Tracking

### Status Fields Pattern
```python
def update_sla_status(doc, method):
    """Update SLA status fields on document update"""
    now = now_datetime()
    
    # Response SLA
    if doc.first_responded_on:
        if doc.first_responded_on <= doc.response_by:
            doc.response_sla_status = "Fulfilled"
        else:
            doc.response_sla_status = "Breached"
    elif doc.response_by and now > doc.response_by:
        doc.response_sla_status = "Breached"
    else:
        doc.response_sla_status = "Ongoing"
    
    # Resolution SLA
    if doc.resolution_date:
        if doc.resolution_date <= doc.resolution_by:
            doc.resolution_sla_status = "Fulfilled"
        else:
            doc.resolution_sla_status = "Breached"
    elif doc.resolution_by and now > doc.resolution_by:
        doc.resolution_sla_status = "Breached"
    else:
        doc.resolution_sla_status = "Ongoing"
```

## SLA Pause/Resume

### Pausing SLA Timer
```python
def pause_sla(doc):
    """Pause SLA when ticket is waiting on customer"""
    if not doc.sla_paused_on:
        doc.db_set("sla_paused_on", now_datetime())
        doc.db_set("sla_paused", 1)

def resume_sla(doc):
    """Resume SLA and adjust due dates"""
    if doc.sla_paused_on:
        paused_duration = time_diff_in_seconds(now_datetime(), doc.sla_paused_on)
        
        if doc.response_by:
            doc.db_set("response_by", 
                add_to_date(doc.response_by, seconds=paused_duration))
        
        if doc.resolution_by:
            doc.db_set("resolution_by", 
                add_to_date(doc.resolution_by, seconds=paused_duration))
        
        doc.db_set("sla_paused_on", None)
        doc.db_set("sla_paused", 0)
```

## Holiday Handling

### Holiday List Integration
```python
def is_holiday(date, holiday_list):
    """Check if date is a holiday"""
    if not holiday_list:
        return False
    
    return frappe.db.exists("Holiday", {
        "parent": holiday_list,
        "holiday_date": date
    })

def calculate_due_with_holidays(start, duration, holiday_list):
    """Skip holidays when calculating due date"""
    due = start
    remaining = duration
    
    while remaining > 0:
        if not is_holiday(due.date(), holiday_list):
            day_start, day_end = get_working_hours(due.date())
            available = min(remaining, day_end - max(due.time(), day_start))
            remaining -= available
        
        if remaining > 0:
            due = next_working_day(due, holiday_list)
    
    return due
```

## SLA Reporting

### SLA Performance Query
```python
def get_sla_performance(filters):
    """Get SLA performance metrics"""
    return frappe.db.sql("""
        SELECT 
            service_level_agreement,
            COUNT(*) as total,
            SUM(CASE WHEN response_sla_status = 'Fulfilled' THEN 1 ELSE 0 END) as response_met,
            SUM(CASE WHEN resolution_sla_status = 'Fulfilled' THEN 1 ELSE 0 END) as resolution_met,
            AVG(TIMESTAMPDIFF(SECOND, creation, first_responded_on)) as avg_response_time,
            AVG(TIMESTAMPDIFF(SECOND, creation, resolution_date)) as avg_resolution_time
        FROM `tabIssue`
        WHERE creation BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY service_level_agreement
    """, filters, as_dict=True)
```

Sources: Frappe Helpdesk, ERPNext Support Module
```