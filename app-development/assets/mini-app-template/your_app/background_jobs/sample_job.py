import frappe


def enqueue_sample_job(docname: str):
    """Enqueue a background job for Sample Doc processing."""
    frappe.enqueue(
        method="your_app.background_jobs.sample_job.run_sample_job",
        queue="default",
        timeout=300,
        docname=docname,
    )


def run_sample_job(docname: str):
    """Worker entrypoint for background job."""
    doc = frappe.get_doc("Sample Doc", docname)
    # Add long-running processing here
    doc.db_set("status", "Closed")
