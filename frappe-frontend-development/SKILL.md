---
name: frappe-frontend-development
description: Build modern Vue 3 frontend apps using Frappe UI with components, data fetching, and portal pages. Use when creating custom frontends, SPAs, or portal interfaces for Frappe applications.
---

# Frappe Frontend Development

Build modern frontend applications using Frappe UI (Vue 3 + TailwindCSS) and portal pages.

## When to use

- Building a custom SPA frontend for a Frappe app
- Using Frappe UI components (Button, Dialog, ListView, etc.)
- Implementing data fetching with Resource, ListResource, DocumentResource
- Creating portal/public-facing pages
- Setting up Vue 3 frontend tooling inside a Frappe app

## Inputs required

- App name and whether frontend already exists
- Frontend type (full SPA via Frappe UI, or portal pages)
- Authentication requirements (logged-in users, guest access)
- Key components and data resources needed

## Procedure

### 0) Choose frontend approach

| Approach | When to Use | Stack |
|----------|-------------|-------|
| Frappe UI SPA | Custom app frontend | Vue 3, TailwindCSS, Vite |
| Portal pages | Simple public pages | Jinja + HTML, minimal JS |
| Desk extensions | Admin UI enhancements | Form/List scripts (see `frappe-desk-customization`) |

### 1) Scaffold Frappe UI frontend

```bash
# Inside your Frappe app directory
cd apps/my_app
npx degit frappe/frappe-ui-starter frontend

# Install dependencies
cd frontend
yarn

# Start dev server
yarn dev
```

### 2) Configure main.js

```javascript
import { createApp } from 'vue'
import {
    FrappeUI,
    setConfig,
    frappeRequest,
    resourcesPlugin,
    pageMetaPlugin
} from 'frappe-ui'
import App from './App.vue'
import './index.css'

let app = createApp(App)

// Register FrappeUI plugin (components + directives)
app.use(FrappeUI)

// Enable Frappe response parsing
setConfig('resourceFetcher', frappeRequest)

// Optional: Options API resource support
app.use(resourcesPlugin)

// Optional: Reactive page titles
app.use(pageMetaPlugin)

app.mount('#app')
```

### 3) Fetch data with Resources

**Generic Resource** — for custom API calls:

```javascript
import { createResource } from 'frappe-ui'

let stats = createResource({
    url: 'my_app.api.get_dashboard_stats',
    params: { period: 'monthly' },
    auto: true,
    cache: 'dashboard-stats',
    transform(data) {
        return { ...data, formatted_total: format_currency(data.total) }
    },
    onSuccess(data) { console.log('Loaded:', data) },
    onError(error) { console.error('Failed:', error) }
})

// Properties
stats.data       // Response data
stats.loading    // Boolean: request in progress
stats.error      // Error object if failed
stats.fetched    // Boolean: data fetched at least once

// Methods
stats.fetch()    // Trigger request
stats.reload()   // Re-fetch
stats.submit({ period: 'weekly' })  // Fetch with new params
stats.reset()    // Reset state
```

**List Resource** — for DocType lists with pagination:

```javascript
import { createListResource } from 'frappe-ui'

let todos = createListResource({
    doctype: 'ToDo',
    fields: ['name', 'description', 'status'],
    filters: { status: 'Open' },
    orderBy: 'creation desc',
    pageLength: 20,
    auto: true,
    cache: 'open-todos'
})

// List-specific API
todos.data              // Array of records
todos.hasNextPage       // Boolean: more pages
todos.next()            // Load next page
todos.reload()          // Refresh list

// CRUD operations
todos.insert.submit({ description: 'New task' })
todos.setValue.submit({ name: 'TODO-001', status: 'Closed' })
todos.delete.submit('TODO-001')
todos.runDocMethod.submit({ method: 'send_email', name: 'TODO-001' })
```

**Document Resource** — for single document operations:

```javascript
import { createDocumentResource } from 'frappe-ui'

let todo = createDocumentResource({
    doctype: 'ToDo',
    name: 'TODO-001',
    whitelistedMethods: {
        sendEmail: 'send_email',
        markComplete: 'mark_complete'
    },
    onSuccess(doc) { console.log('Loaded:', doc.name) }
})

// Document API
todo.doc                 // Full document object
todo.reload()            // Refresh document

// Update fields
todo.setValue.submit({ status: 'Closed' })

// Debounced update (coalesces rapid changes)
todo.setValueDebounced.submit({ description: 'Updated' })

// Call whitelisted methods
todo.sendEmail.submit({ email: 'user@example.com' })

// Delete
todo.delete.submit()
```

### 4) Use Frappe UI components

```vue
<template>
    <div class="p-4">
        <Button variant="solid" theme="blue" @click="showDialog = true">
            Add Todo
        </Button>

        <ListView :columns="columns" :rows="todos.data">
            <template #cell="{ column, row, value }">
                <Badge v-if="column.key === 'status'" :theme="value === 'Open' ? 'orange' : 'green'">
                    {{ value }}
                </Badge>
                <span v-else>{{ value }}</span>
            </template>
        </ListView>

        <Dialog v-model="showDialog" :options="{ title: 'New Todo' }">
            <template #body-content>
                <TextInput v-model="newDescription" placeholder="Description" />
            </template>
            <template #actions>
                <Button variant="solid" @click="addTodo">Save</Button>
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button, ListView, Badge, Dialog, TextInput, createListResource } from 'frappe-ui'

const showDialog = ref(false)
const newDescription = ref('')

const todos = createListResource({
    doctype: 'ToDo',
    fields: ['name', 'description', 'status'],
    auto: true
})

const columns = [
    { label: 'Description', key: 'description' },
    { label: 'Status', key: 'status', width: 100 }
]

function addTodo() {
    todos.insert.submit(
        { description: newDescription.value },
        { onSuccess() { showDialog.value = false; newDescription.value = '' } }
    )
}
</script>
```

**Available component categories:**

| Category | Components |
|----------|------------|
| Inputs | TextInput, Textarea, Select, Combobox, MultiSelect, Checkbox, Switch, DatePicker, TimePicker, Slider, Password, Rating |
| Display | Alert, Avatar, Badge, Breadcrumbs, Progress, Tooltip, ErrorMessage, LoadingText |
| Navigation | Button, Dropdown, Tabs, Sidebar, Popover |
| Layout | Dialog, ListView, Calendar, Tree |
| Rich Content | TextEditor (TipTap), Charts, FileUploader |

### 5) Add directives and utilities

```vue
<script setup>
import { onOutsideClickDirective, visibilityDirective, debounce } from 'frappe-ui'

const vOnOutsideClick = onOutsideClickDirective
const vVisibility = visibilityDirective

const debouncedSearch = debounce((query) => {
    // Search logic
}, 500)
</script>

<template>
    <div v-on-outside-click="closeDropdown">...</div>
    <div v-visibility="onVisible">Lazy loaded content</div>
</template>
```

### 6) Configure TailwindCSS

```javascript
// tailwind.config.js
module.exports = {
    presets: [
        require('frappe-ui/src/utils/tailwind.config')
    ],
    content: [
        './index.html',
        './src/**/*.{vue,js,ts}',
        './node_modules/frappe-ui/src/components/**/*.{vue,js,ts}'
    ]
}
```

### 7) Build for production

```bash
# Build frontend assets
cd frontend && yarn build

# Assets are served at /frontend by Frappe
```

### 8) Portal pages (alternative approach)

For simple public pages without a full SPA:

```python
# In your app's website/ or www/ directory
# my_app/www/my_page.html

{% extends "templates/web.html" %}
{% block page_content %}
<h1>{{ title }}</h1>
<p>Welcome, {{ frappe.session.user }}</p>
{% endblock %}
```

```python
# my_app/www/my_page.py
def get_context(context):
    context.title = "My Page"
    context.data = frappe.get_all("ToDo", filters={"owner": frappe.session.user})
```

## Verification

- [ ] `yarn dev` starts without errors
- [ ] Components render correctly
- [ ] Data resources fetch and display data
- [ ] CRUD operations work (insert, update, delete)
- [ ] Authentication works (login redirect, session handling)
- [ ] `yarn build` completes successfully
- [ ] Production assets serve correctly from Frappe

## Failure modes / debugging

- **CORS errors**: Set `ignore_csrf` for local dev; ensure proper CSRF token in production
- **404 on API calls**: Check method path; verify `@frappe.whitelist()` decorator
- **Component not found**: Ensure import path is correct; check `frappe-ui` version
- **Styles broken**: Verify TailwindCSS config includes `frappe-ui` component paths
- **Auth issues**: Check session cookie; ensure site URL matches in dev proxy config

## Escalation

- For Desk UI scripting → `frappe-desk-customization`
- For API endpoint implementation → `frappe-api-development`
- For app architecture → `frappe-app-development`
- For UI/UX patterns from official apps → `frappe-ui-patterns`

## References

- [references/frappe-ui.md](references/frappe-ui.md) — Frappe UI framework reference
- [references/portal-development.md](references/portal-development.md) — Portal pages overview

## Guardrails

- **ALWAYS use Frappe UI for custom frontends**: Never use vanilla JS, jQuery, or custom frameworks for app frontends — Frappe UI (Vue 3 + TailwindCSS) is the standard. This ensures consistency with CRM, Helpdesk, and other official Frappe apps.
- **Use FrappeUI components**: Prefer `<Button>`, `<Input>`, `<FormControl>` over custom HTML for consistency
- **Follow CRM/Helpdesk app shell patterns**: For CRUD apps, follow `frappe-ui-patterns` skill which documents sidebar navigation, list views, form layouts, and routing patterns from official Frappe apps
- **Handle loading states**: Always show loading indicators during API calls; use `resource.loading`
- **Validate API responses**: Check for errors before accessing data; handle `exc` responses
- **Configure proxy correctly**: Dev server must proxy API calls to Frappe backend
- **Handle authentication**: Check `$session.user` and redirect to login when needed

## Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Missing CORS/proxy setup | API calls fail in development | Configure Vite proxy to forward `/api` to Frappe site |
| Not handling auth state | App crashes for logged-out users | Check `call('frappe.auth.get_logged_user')` on mount |
| Wrong resource URLs | 404 errors on API calls | Use `createResource` with correct method paths |
| Hardcoded site URL | Breaks across environments | Use relative URLs or environment variables |
| Not including CSRF token | POST requests fail | Use `frappe.csrf_token` or configure session properly |
| Missing TailwindCSS config | Frappe UI styles broken | Include `frappe-ui` in Tailwind content paths |
| Using vanilla JS/jQuery | Inconsistent UX, maintenance burden | Always use Frappe UI for custom frontends |
| Custom app shell design | Inconsistent with ecosystem | Follow CRM/Helpdesk patterns for navigation, lists, forms |
