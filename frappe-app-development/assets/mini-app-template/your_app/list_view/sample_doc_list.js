frappe.listview_settings["Sample Doc"] = {
  onload(listview) {
    listview.page.add_action_item("Mark Closed", () => {
      const selected = listview.get_checked_items();
      if (!selected.length) {
        frappe.msgprint("Select at least one document");
        return;
      }
      frappe.call({
        method: "frappe.client.set_value",
        args: {
          doctype: "Sample Doc",
          name: selected[0].name,
          fieldname: "status",
          value: "Closed",
        },
      }).then(() => listview.refresh());
    });
  },
  get_indicator(doc) {
    if (doc.status === "Closed") {
      return ["Closed", "gray", "status,=,Closed"];
    }
    return ["Open", "green", "status,=,Open"];
  },
};
