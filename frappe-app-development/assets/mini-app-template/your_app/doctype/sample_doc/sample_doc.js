frappe.ui.form.on("Sample Doc", {
  setup(frm) {
    // Filter link options for a field (if you add a Link field)
    // frm.set_query("customer", () => ({ filters: { disabled: 0 } }));
  },
  refresh(frm) {
    frm.add_custom_button("Approve", () => {
      frappe.call({
        method: "your_app.api.hello",
        args: { name: frm.doc.title },
      }).then((r) => {
        frappe.msgprint(r.message || "Approved");
      });
    });
  },
  validate(frm) {
    if (!frm.doc.title) {
      frappe.msgprint("Title is required");
      frappe.validated = false;
    }
  },
  status(frm) {
    if (frm.doc.status === "Closed") {
      frm.set_value("title", `${frm.doc.title} (Closed)`);
    }
  },
});
