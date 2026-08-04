import frappe
from your_app.utils.errors import ERROR_CODES


def require_fields(payload: dict, fields: list[str]):
    """Raise a validation error if any required fields are missing or falsy.

    Keeps error messages consistent using `ERROR_CODES`.
    """
    missing = [f for f in fields if not payload.get(f)]
    if missing:
        frappe.throw(f"{ERROR_CODES['VALIDATION_ERROR']}: missing fields: {', '.join(missing)}")
