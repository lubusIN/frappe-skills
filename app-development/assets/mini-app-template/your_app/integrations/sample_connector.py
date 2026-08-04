import frappe
import requests
from requests.exceptions import RequestException
from your_app.utils.errors import ERROR_CODES
from your_app.utils.logging import log_error


def fetch_status(external_id: str):
    """Example integration connector stub.

    Wraps external HTTP calls with timeout and explicit error mapping so
    callers receive predictable exceptions.
    """
    if not external_id:
        frappe.throw("external_id is required")

    try:
        # Replace with real integration URL and authentication
        response = requests.get("https://example.com/status", params={"id": external_id}, timeout=10)
        response.raise_for_status()
        return response.json()

    except RequestException as exc:
        # Log and re-raise as a frappe-friendly error for the app to handle
        log_error("Integration fetch failed", str(exc), exc=exc)
        frappe.throw(ERROR_CODES["INTEGRATION_ERROR"] + ": failed to fetch external status")
