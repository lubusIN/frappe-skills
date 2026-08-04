import frappe
from frappe.model.document import Document


class SampleDoc(Document):
    def validate(self):
        """Example server-side validation.

        Keep checks minimal and deterministic. For complex validation and
        side-effects, prefer service-layer functions that can be unit tested.
        """
        if not self.title:
            frappe.throw("Title is required")

        # Example: enforce a maximum title length for predictable storage
        if self.title and len(self.title) > 255:
            frappe.throw("Title must be 255 characters or fewer")
