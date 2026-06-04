import frappe
from frappe import _


def create_sample_doc(title: str, status: str = "Open"):
    """Service layer: create a `Sample Doc`.

    This function performs lightweight validation and persists the document.
    Keep business logic here rather than in API handlers.
    """
    if not title:
        frappe.throw(_("Title is required"))

    doc = frappe.get_doc({
        "doctype": "Sample Doc",
        "title": title,
        "status": status,
    })
    # Use normal permission checks; callers should ensure permissions where appropriate.
    doc.insert()
    return doc
