import frappe
import logging
import traceback

logger = frappe.logger() or logging.getLogger("your_app")


def log_info(title: str, message: str, reference_doctype: str | None = None, reference_name: str | None = None):
    """Log an informational message. Optionally create an error log entry for tracing purposes.

    Use `reference_doctype` and `reference_name` to link the log to a document when helpful.
    """
    logger.info(message)


def log_error(title: str, message: str, exc: Exception | None = None, reference_doctype: str | None = None, reference_name: str | None = None):
    """Record an error to both the logger and frappe error log (for visibility in Desk).

    `exc` may be provided to capture a stack trace.
    """
    if exc:
        tb = traceback.format_exc()
        logger.error("%s - %s\n%s", title, message, tb)
        frappe.log_error(tb, title)
    else:
        logger.error("%s - %s", title, message)
        frappe.log_error(message, title)
