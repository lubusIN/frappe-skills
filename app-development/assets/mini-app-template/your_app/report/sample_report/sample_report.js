frappe.query_reports["Sample Report"] = {
  filters: [
    {
      fieldname: "status",
      label: "Status",
      fieldtype: "Select",
      options: "\nOpen\nClosed",
      default: "Open",
    },
    {
      fieldname: "title",
      label: "Title Contains",
      fieldtype: "Data",
    },
    {
      fieldname: "page_length",
      label: "Page Size",
      fieldtype: "Int",
      default: 20,
    },
    {
      fieldname: "page",
      label: "Page",
      fieldtype: "Int",
      default: 1,
    },
  ],
  onload(report) {
    const updatePagerState = () => {
      const current = report.get_filter_value("page") || 1;
      const pageLength = report.get_filter_value("page_length") || 20;
      const summary = report.get_summary ? report.get_summary() : [];
      const totalRow = (summary || []).find((r) => r.label === "Total Records");
      const total = totalRow ? totalRow.value : null;
      const totalPages = total ? Math.max(1, Math.ceil(total / pageLength)) : null;

      if (report.page && report.page.set_title_sub && totalPages) {
        report.page.set_title_sub(`Page ${current} of ${totalPages}`);
      }

      const prevBtn = report.page && report.page.prev_btn;
      const nextBtn = report.page && report.page.next_btn;
      if (prevBtn) {
        prevBtn.prop("disabled", current <= 1);
      }
      if (nextBtn && totalPages) {
        nextBtn.prop("disabled", current >= totalPages);
      }
    };

    const addPagerButtons = () => {
      report.page.prev_btn = report.page.add_inner_button("Prev", () => {
        const current = report.get_filter_value("page") || 1;
        report.set_filter_value("page", Math.max(1, current - 1));
        report.refresh();
      });
      report.page.next_btn = report.page.add_inner_button("Next", () => {
        const current = report.get_filter_value("page") || 1;
        report.set_filter_value("page", current + 1);
        report.refresh();
      });
    };

    addPagerButtons();

    const originalRefresh = report.refresh.bind(report);
    report.refresh = () => {
      const result = originalRefresh();
      if (result && result.then) {
        return result.then(() => updatePagerState());
      }
      setTimeout(updatePagerState, 0);
      return result;
    };
  },
};
