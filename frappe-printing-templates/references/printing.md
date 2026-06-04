# Printing and Print Formats

## Overview
Frappe has first-class support for generating print formats for documents and converting them to PDF. Print formats use Jinja templating.

## Print View
Every document has a Print View accessible from the form. Frappe generates a Standard print format based on the form layout and mandatory fields.

## Print Format Builder
Customize print formats using the Print Format Builder:
1. Create a copy of the Standard Print format
2. Customize using the drag-and-drop builder
3. These formats are user-editable and stored in the database (not files)

### Custom HTML
Drag and drop "Custom HTML" into your Print Format Editor. Use:
- Valid HTML with Bootstrap 3 classes
- Jinja templating for dynamic content

### Custom CSS
Add custom CSS via Customize > Edit Properties.

## Advanced Print Formats
For complete layout control, write your own HTML:
1. Type "new print format" in awesomebar
2. Set a unique name
3. Set "Standard" as "No"
4. Check "Custom Format"
5. Select Print Format Type as "Jinja"
6. Write your custom HTML

If Standard is "Yes" with Developer Mode enabled, a JSON file will be generated for version control.

## Jinja in Print Formats
```jinja
<div class="print-format">
    <h1>{{ doc.name }}</h1>
    <p><strong>Customer:</strong> {{ doc.customer }}</p>
    
    <table>
        <tr>
            <th>Item</th>
            <th>Qty</th>
        </tr>
        {% for item in doc.items %}
        <tr>
            <td>{{ item.item_name }}</td>
            <td>{{ item.qty }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <p><strong>Total:</strong> {{ frappe.format_value(doc.grand_total, {'fieldtype': 'Currency'}) }}</p>
</div>
```

## Print Formats for Reports
Create HTML files named `{report-name}.html` in the Report folder for custom report printing. These use JS templating (similar to Jinja but client-side).

## PDF Generation
Use `frappe.get_print()` for server-side PDF generation:
```python
pdf = frappe.get_print(doctype, docname, print_format, as_pdf=True)
```

## Letter Head
Configure Letter Head for company branding on print formats.

Sources: Printing, Print Formats, Jinja API (official docs)
