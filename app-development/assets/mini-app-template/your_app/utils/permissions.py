import frappe
from your_app.utils.errors import ERROR_CODES


def require_permission(doctype: str, perm: str, docname: str | None = None):
    """Raise a permission error if the current user lacks the requested permission.

    Uses a consistent error code so API consumers can react accordingly.
    """
    if not frappe.has_permission(doctype, perm, doc=docname):
        frappe.throw(ERROR_CODES["PERMISSION_DENIED"]) 
