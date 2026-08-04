# Frappe UI (frontend framework)

## Overview
Frappe UI is a set of components and utilities for building frontend apps based on Frappe Framework. Built on Vue 3 and TailwindCSS, it provides:
- 30+ UI components following the Frappe design system
- Reactive data-fetching with Resource, List Resource, and Document Resource
- Utilities and Vue directives for common patterns

**Used by**: Frappe Cloud, Gameplan, Helpdesk, Frappe Insights, Frappe Drive, Frappe Builder

**Under the hood**: Vue 3, TailwindCSS, Headless UI, TipTap (rich text), PopperJS, dayjs, Feather Icons

## Installation and Setup

### Quick Start with Starter Template
Use the official Frappe UI starter template:

```bash
# Create a Frappe app first
bench new-app my_app

# Scaffold Vue frontend inside the app
cd apps/my_app
npx degit frappe/frappe-ui-starter frontend

# Install dependencies and start dev server
cd frontend
yarn
yarn dev
```

### Manual Installation
```bash
npm install frappe-ui
# or
yarn add frappe-ui
```

**main.js:**
```javascript
import { createApp } from 'vue'
import { FrappeUI, setConfig, frappeRequest, resourcesPlugin, pageMetaPlugin } from 'frappe-ui'
import App from './App.vue'
import './index.css'

let app = createApp(App)

// Register FrappeUI plugin
app.use(FrappeUI)

// Enable Frappe response parsing (extracts data from `message`, errors from `exc`)
setConfig('resourceFetcher', frappeRequest)

// Optional plugins
app.use(resourcesPlugin)    // For Options API resources
app.use(pageMetaPlugin)     // For reactive page titles

app.mount('#app')
```

**tailwind.config.js:**
```javascript
module.exports = {
  presets: [
    require('frappe-ui/src/utils/tailwind.config')
  ],
  // ... your config
}
```

### CSRF Configuration
```bash
# For local dev only (disable CSRF checks)
bench --site mysite.local set-config ignore_csrf 1
```

In production, `csrf_token` is automatically attached to the window in `index.html`.

## Data Fetching

### Resource (createResource)
For generic async data fetching with caching, loading states, and lifecycle hooks.

```javascript
import { createResource } from 'frappe-ui'

// Basic usage
let todos = createResource({
  url: 'frappe.client.get_list',  // Can omit /api/method when using frappeRequest
  params: {
    doctype: 'ToDo',
    filters: { status: 'Open' }
  },
  auto: true,           // Fetch automatically on mount
  cache: 'todos',       // Cache key (string or array)
  debounce: 500,        // Debounce requests (ms)
  initialData: [],      // Seed data before first fetch
  method: 'GET',        // HTTP method (default: POST)
  
  // Generate params dynamically
  makeParams() {
    return { id: 1 }
  },
  
  // Lifecycle hooks
  beforeSubmit(params) { },
  validate(params) {
    if (!params.doctype) return 'doctype is required'  // Return string to throw error
  },
  onSuccess(data) { },
  onError(error) { },
  transform(data) {
    // Modify data before setting
    return data.map(d => ({ ...d, open: false }))
  }
})

// Resource API - Properties
todos.data           // Returned data
todos.loading        // Boolean: fetching in progress
todos.error          // Error from request or validate
todos.fetched        // Boolean: has data been fetched once
todos.previousData   // Data before last reload
todos.params         // Current params (from makeParams if used)
todos.promise        // Awaitable promise

// Resource API - Methods
todos.fetch()        // Make request
todos.reload()       // Alias to fetch
todos.submit({ ... }) // Fetch with different params
todos.reset()        // Reset state
todos.update({ url, params }) // Update config
todos.setData(data)  // Override data manually
todos.setData(d => d.filter(x => x.open)) // Modify data
```

### List Resource (createListResource)
Specialized wrapper for fetching DocType lists with pagination and CRUD operations.

```javascript
import { createListResource } from 'frappe-ui'

let todos = createListResource({
  doctype: 'ToDo',
  fields: ['name', 'description', 'status'],
  filters: { status: 'Open' },
  orderBy: 'creation desc',
  start: 0,              // Starting index (default: 0)
  pageLength: 20,        // Records per page (default: 20)
  parent: null,          // Parent doctype for child tables
  debug: 0,              // Enable query debugging
  cache: 'todos',
  url: 'custom.api.get_todos',  // Custom API (default: frappe.client.get_list)
  auto: true,
  
  // Lifecycle hooks
  onSuccess(data) { },
  onError(error) { },
  transform(data) { return data },
  
  // Events for sub-resources
  fetchOne: { onSuccess() {}, onError() {} },
  insert: { onSuccess() {}, onError() {} },
  delete: { onSuccess() {}, onError() {} },
  setValue: { onSuccess() {}, onError() {} },
  runDocMethod: { onSuccess() {}, onError() {} },
})

// List Resource API
todos.data             // List data
todos.originalData     // Data before transform
todos.reload()         // Reload list
todos.next()           // Fetch next page
todos.hasNextPage      // Boolean: more pages available
todos.update({ fields, filters })  // Update list options

// Sub-resources for list operations
todos.list             // The underlying list resource
todos.list.loading     // Loading state
todos.list.error       // Error state
todos.list.promise     // Awaitable promise

// Fetch and update a single record in the list
todos.fetchOne.submit(name)

// Set values on a record
todos.setValue.submit({
  name: 'TODO-001',     // Record ID
  status: 'Closed',     // Field-value pairs
  description: 'Updated'
})

// Insert new record
todos.insert.submit({ description: 'New todo' })

// Delete record
todos.delete.submit(name)

// Run doc method
todos.runDocMethod.submit({
  method: 'send_email',
  name: 'TODO-001',
  email: 'test@example.com'
})
```

### Document Resource (createDocumentResource)
For working with a single document (fetch, update, delete, call methods).

```javascript
import { createDocumentResource } from 'frappe-ui'

let todo = createDocumentResource({
  doctype: 'ToDo',
  name: 'TODO-001',
  
  // Expose whitelisted controller methods as resources
  whitelistedMethods: {
    sendEmail: 'send_email',
    markComplete: 'mark_complete'
  },
  
  // Lifecycle hooks
  onSuccess(doc) { },
  onError(error) { },
  transform(doc) {
    doc.computed_field = doc.qty * doc.rate
    return doc
  },
  
  // Events for sub-resources
  delete: { onSuccess() {}, onError() {} },
  setValue: { onSuccess() {}, onError() {} },
})

// Document Resource API
todo.doc               // The document object with all fields
todo.reload()          // Reload document
todo.update({ doctype, name })  // Change document

// Sub-resources
todo.get               // The underlying get resource
todo.get.loading       // Loading state
todo.get.error         // Error state
todo.get.promise       // Awaitable promise

// Set values
todo.setValue.submit({
  status: 'Closed',
  description: 'Updated'
})

// Debounced setValue (runs once after 500ms)
todo.setValueDebounced.submit({
  description: 'Updated'
})

// Delete document
todo.delete.submit()

// Whitelisted methods become resources
todo.sendEmail.submit({ email: 'user@example.com' })
todo.sendEmail.loading
```

### Unified createResource with type
You can also use `createResource` with a `type` option:

```javascript
import { createResource } from 'frappe-ui'

let todos = createResource({
  type: 'list',
  doctype: 'ToDo',
  fields: ['name', 'description'],
  cache: 'ToDos',
  auto: true,
})
```

### Options API Usage
```javascript
import { resourcesPlugin } from 'frappe-ui'
app.use(resourcesPlugin)

// In component
export default {
  resources: {
    todos() {
      return {
        type: 'list',  // 'list' or 'document'
        doctype: 'ToDo',
        fields: ['name', 'status'],
        auto: true
      }
    },
    todo() {
      return {
        type: 'document',
        doctype: 'ToDo',
        name: '1'
      }
    }
  },
  computed: {
    todoList() {
      return this.$resources.todos.data
    }
  }
}
```

## Components

### Component List
| Category | Components |
|----------|------------|
| **Inputs** | TextInput, Textarea, Select, Combobox, MultiSelect, Checkbox, Switch, DatePicker, TimePicker, MonthPicker, Slider, Password, Rating |
| **Display** | Alert, Avatar, Badge, Breadcrumbs, Progress, Tooltip, ErrorMessage, LoadingText |
| **Navigation** | Button, Dropdown, Tabs, Sidebar, Popover |
| **Layout** | Dialog, ListView, Calendar, Tree |
| **Rich Content** | TextEditor (TipTap-based), Charts, FileUploader |

### Key Component Examples

#### Button
```vue
<template>
  <Button 
    variant="solid"
    theme="blue"
    :loading="isLoading"
    @click="handleClick"
  >
    Click Me
  </Button>
</template>

<script>
import { Button } from 'frappe-ui'
export default {
  components: { Button }
}
</script>
```

#### Dialog
```vue
<Dialog 
  v-model="showDialog"
  :options="{
    title: 'Confirm Action',
    message: 'Are you sure?',
    actions: [
      { label: 'Cancel', variant: 'outline' },
      { label: 'Confirm', variant: 'solid', theme: 'blue', onClick: confirm }
    ]
  }"
>
  <template #body-content>
    <p>Custom dialog content</p>
  </template>
</Dialog>
```

#### ListView
```vue
<ListView
  :columns="columns"
  :rows="todos.data"
>
  <template #cell="{ column, row, value }">
    <Badge v-if="column.key === 'status'">{{ value }}</Badge>
    <span v-else>{{ value }}</span>
  </template>
</ListView>
```

#### TextEditor (TipTap-based)
```vue
<TextEditor
  v-model="content"
  :editable="true"
  :fixedMenu="true"
  placeholder="Start typing..."
/>
```

## Utilities

### debounce
```javascript
import { debounce } from 'frappe-ui'

let debouncedSearch = debounce((query) => {
  // Search logic
}, 500)
```

### fileToBase64
```javascript
import { fileToBase64 } from 'frappe-ui'

let base64 = await fileToBase64(fileObject)
```

### pageMeta Plugin
```javascript
// In component (Options API)
export default {
  pageMeta() {
    return {
      title: 'Page Title',
      icon: '/path/to/icon.png',
      emoji: '✅'
    }
  }
}
```

## Directives

### v-on-outside-click
```vue
<template>
  <div v-on-outside-click="closeDropdown">
    <!-- Content -->
  </div>
</template>

<script>
import { onOutsideClickDirective } from 'frappe-ui'
export default {
  directives: {
    onOutsideClick: onOutsideClickDirective
  }
}
</script>
```

### v-visibility
```vue
<template>
  <div v-visibility="onVisibilityChange">
    <!-- Triggers when element enters/leaves viewport -->
  </div>
</template>

<script>
import { visibilityDirective } from 'frappe-ui'
export default {
  directives: {
    visibility: visibilityDirective
  },
  methods: {
    onVisibilityChange(visible, entry) {
      // entry is IntersectionObserverEntry
    }
  }
}
</script>
```

## References
- https://ui.frappe.io/docs/introduction
- https://ui.frappe.io/docs/getting-started
- https://ui.frappe.io/docs/data-fetching/resource
- https://ui.frappe.io/docs/data-fetching/list-resource
- https://ui.frappe.io/docs/data-fetching/document-resource
- https://ui.frappe.io/docs/other/utilities
- https://ui.frappe.io/docs/other/directives
- https://github.com/frappe/frappe-ui
- https://github.com/netchampfaris/frappe-ui-starter
