import frappe
from frappe.query_builder import functions as fn


def execute(filters=None):
    filters = filters or {}

    columns = [
        {
            "label": "Title",
            "fieldname": "title",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
        },
    ]

    SampleDoc = frappe.qb.DocType("Sample Doc")
    base = frappe.qb.from_(SampleDoc)

    where_clauses = []
    if filters.get("status"):
        where_clauses.append(SampleDoc.status == filters["status"])
    if filters.get("title"):
        where_clauses.append(SampleDoc.title.like(f"%{filters['title']}%"))

    query = (
        base.select(SampleDoc.name, SampleDoc.title, SampleDoc.status)
        .orderby(SampleDoc.modified, order=frappe.qb.desc)
    )
    for clause in where_clauses:
        query = query.where(clause)

    page_length = int(filters.get("page_length") or 20)
    page = int(filters.get("page") or 1)
    if page < 1:
        page = 1
    if page_length < 1:
        page_length = 20

    offset = (page - 1) * page_length
    query = query.limit(page_length).offset(offset)

    data = query.run(as_dict=True)

    count_query = base.select(fn.Count("*").as_("count"))
    for clause in where_clauses:
        count_query = count_query.where(clause)
    total_count = count_query.run(as_dict=True)[0]["count"]

    report_summary = [
        {
            "label": "Total Records",
            "value": total_count,
            "indicator": "blue",
        }
    ]

    return columns, data, None, None, report_summary
