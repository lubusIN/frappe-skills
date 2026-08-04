import frappe
from frappe import _
from your_app.services.sample_service import create_sample_doc
from your_app.utils.errors import ok, error, ERROR_CODES
from your_app.utils.permissions import require_permission
from your_app.utils.validation import require_fields
from your_app.utils.logging import log_error
import frappe.exceptions


@frappe.whitelist(allow_guest=False)
def hello(name: str | None = None) -> str:
    """Simple whitelisted method example used by the client side.

    Keep this tiny and focused; use service layer functions for heavier logic.
    """
    return f"Hello {name}" if name else "Hello"


@frappe.whitelist()
def create_sample(title: str | None = None, status: str = "Open"):
    """Create a `Sample Doc` via the service layer and return a consistent payload.

    Returns `ok(...)` on success and `error(...)` on failure. Handles common
    framework exceptions to provide predictable error codes for consumers.
    """
    try:
        require_permission("Sample Doc", "create")
        require_fields({"title": title}, ["title"])
        doc = create_sample_doc(title=title, status=status)
        return ok("Created", {"name": doc.name})

    except frappe.exceptions.PermissionError as pe:
        log_error("Create Sample - permission denied", str(pe), exc=pe)
        return error("Permission denied", {"detail": str(pe)}, code=ERROR_CODES["PERMISSION_DENIED"])

    except frappe.ValidationError as ve:
        log_error("Create Sample - validation", str(ve), exc=ve)
        return error("Validation failed", {"detail": str(ve)}, code=ERROR_CODES["VALIDATION_ERROR"])    

    except Exception as exc:
        # Unexpected error -- capture details for later debugging
        log_error("Create Sample failed", str(exc), exc=exc)
        return error("Create Sample failed", {"detail": str(exc)}, code=ERROR_CODES["APP_ERROR"])    
