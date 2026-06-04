# Jinja Templating in Frappe

## Overview
Jinja is Frappe's templating engine for rendering HTML in Print Formats, Email Templates, Portal Pages, and Web Views. Frappe provides a set of whitelisted methods accessible in Jinja templates.

## Syntax Basics

### Delimiters
```jinja
{{ variable }}              {# Output expression #}
{% if condition %}...{% endif %}   {# Statement/control structure #}
{# This is a comment #}     {# Comment (not rendered) #}
```

### Variables
```jinja
{{ doc.title }}             {# Attribute access #}
{{ doc['title'] }}          {# Item access (equivalent) #}
{{ name|upper }}            {# Filter: transform value #}
{{ items|length }}          {# Filter: get list length #}
```

### Control Structures
```jinja
{# For loop #}
{% for item in items %}
  {{ item.name }}
  {{ loop.index }}          {# 1-indexed iteration #}
  {{ loop.first }}          {# True on first iteration #}
  {{ loop.last }}           {# True on last iteration #}
{% else %}
  No items found
{% endfor %}

{# Conditionals #}
{% if doc.status == 'Open' %}
  Open
{% elif doc.status == 'Closed' %}
  Closed
{% else %}
  Unknown
{% endif %}

{# Set variable #}
{% set total = 0 %}
{% set total = total + item.amount %}
```

### Template Inheritance
```jinja
{# base.html #}
<!DOCTYPE html>
<html>
<head>{% block head %}{% endblock %}</head>
<body>{% block content %}{% endblock %}</body>
</html>

{# child.html #}
{% extends "base.html" %}
{% block content %}
  <h1>Hello</h1>
  {{ super() }}  {# Include parent block content #}
{% endblock %}
```

### Include and Import
```jinja
{# Include another template #}
{% include "templates/includes/header.html" %}

{# Import macros #}
{% from "templates/macros.html" import input_field %}
{{ input_field('email') }}
```

### Macros (Reusable Functions)
```jinja
{% macro input(name, value='', type='text') %}
  <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}

{{ input('username') }}
{{ input('password', type='password') }}
```

## Frappe Jinja API

These are whitelisted methods available in Frappe Jinja templates:

### Data Fetching

#### frappe.get_doc
```jinja
{% set task = frappe.get_doc('Task', 'TASK00002') %}
{{ task.title }} - {{ task.status }}
```

#### frappe.get_all / frappe.get_list
```jinja
{# get_all: ignores permissions #}
{% set tasks = frappe.get_all('Task', 
    filters={'status': 'Open'}, 
    fields=['title', 'due_date'],
    order_by='due_date asc',
    page_length=10) %}

{% for task in tasks %}
  {{ task.title }} - {{ frappe.format_date(task.due_date) }}
{% endfor %}

{# get_list: respects permissions #}
{% set my_tasks = frappe.get_list('Task', filters={'owner': frappe.session.user}) %}
```

#### frappe.db.get_value
```jinja
{# Single field #}
{% set abbr = frappe.db.get_value('Company', 'My Company', 'abbr') %}

{# Multiple fields #}
{% set title, status = frappe.db.get_value('Task', 'TASK001', ['title', 'status']) %}
```

#### frappe.db.get_single_value
```jinja
{% set timezone = frappe.db.get_single_value('System Settings', 'time_zone') %}
```

#### frappe.get_system_settings
```jinja
{% if frappe.get_system_settings('country') == 'India' %}
  INR Currency
{% endif %}
```

### Formatting

#### frappe.format
```jinja
{# Format value based on fieldtype #}
{{ frappe.format('2019-09-08', {'fieldtype': 'Date'}) }}
{{ frappe.format(50000, {'fieldtype': 'Currency'}) }}
```

#### frappe.format_date
```jinja
{{ frappe.format_date('2019-09-08') }}
{# Output: September 8, 2019 #}
```

### Metadata

#### frappe.get_meta
```jinja
{% set meta = frappe.get_meta('Task') %}
Task has {{ meta.fields|length }} fields.
{% if meta.get_field('status') %}
  Has status field
{% endif %}
```

### URLs and Rendering

#### frappe.get_url
```jinja
<a href="{{ frappe.get_url() }}/task/{{ doc.name }}">View Task</a>
```

#### frappe.render_template
```jinja
{# Render a template file #}
{{ frappe.render_template('templates/includes/footer.html', {}) }}

{# Render a template string #}
{{ frappe.render_template('Hello {{ name }}', {'name': 'World'}) }}
```

### Translation

#### frappe._ or _()
```jinja
{{ _('Hello World') }}
{{ frappe._('This will be translated') }}
```

### Session Context

```jinja
{# Current user #}
{{ frappe.session.user }}

{# User's full name #}
{{ frappe.get_fullname() }}
{{ frappe.get_fullname('user@example.com') }}

{# CSRF token (for forms) #}
<input type="hidden" name="csrf_token" value="{{ frappe.session.csrf_token }}">

{# Current language (e.g., 'en', 'de') #}
{{ frappe.lang }}

{# Query parameters in web requests #}
{{ frappe.form_dict.get('search') }}
```

## Common Use Cases

### Print Format
```jinja
<h1>{{ doc.name }}</h1>
<p>Customer: {{ doc.customer }}</p>

<table>
  <tr><th>Item</th><th>Qty</th><th>Amount</th></tr>
  {% for item in doc.items %}
  <tr>
    <td>{{ item.item_name }}</td>
    <td>{{ item.qty }}</td>
    <td>{{ frappe.format(item.amount, {'fieldtype': 'Currency'}) }}</td>
  </tr>
  {% endfor %}
</table>

<p>Total: {{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}</p>
```

### Email Template
```jinja
Dear {{ doc.customer_name }},

Your order {{ doc.name }} has been confirmed.

Items:
{% for item in doc.items %}
- {{ item.item_name }} x {{ item.qty }}
{% endfor %}

Total: {{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}

Thank you,
{{ frappe.get_fullname() }}
```

### Web Page
```jinja
{% extends "templates/web.html" %}

{% block page_content %}
<h1>{{ title }}</h1>

{% set posts = frappe.get_all('Blog Post', 
    filters={'published': 1},
    fields=['title', 'route', 'published_on'],
    order_by='published_on desc',
    page_length=5) %}

{% for post in posts %}
<article>
  <h2><a href="/{{ post.route }}">{{ post.title }}</a></h2>
  <time>{{ frappe.format_date(post.published_on) }}</time>
</article>
{% endfor %}
{% endblock %}
```

## Built-in Filters

Common Jinja filters available:
```jinja
{{ name|upper }}          {# UPPERCASE #}
{{ name|lower }}          {# lowercase #}
{{ name|title }}          {# Title Case #}
{{ name|capitalize }}     {# First letter uppercase #}
{{ text|truncate(50) }}   {# Truncate to 50 chars #}
{{ text|striptags }}      {# Remove HTML tags #}
{{ text|safe }}           {# Mark as safe HTML (no escaping) #}
{{ list|join(', ') }}     {# Join list items #}
{{ list|length }}         {# List length #}
{{ list|first }}          {# First item #}
{{ list|last }}           {# Last item #}
{{ value|default('N/A') }} {# Default if undefined #}
{{ dict|dictsort }}       {# Sort dictionary #}
{{ number|round(2) }}     {# Round to 2 decimals #}
{{ number|int }}          {# Convert to integer #}
{{ data|tojson }}         {# Convert to JSON string #}
```

## Security Notes
- Frappe auto-escapes HTML in templates to prevent XSS
- Use `{{ value|safe }}` only for trusted HTML content
- The `frappe.get_all` method ignores permissions; use `frappe.get_list` for permission-aware queries

## References
- https://frappeframework.com/docs/user/en/api/jinja
- https://jinja.palletsprojects.com/en/3.1.x/templates/
