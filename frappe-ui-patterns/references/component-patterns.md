# Component Patterns

Usage patterns for Frappe UI components in app development.

## Button Patterns

### Variants

```vue
<!-- Primary action -->
<Button variant="solid">Save</Button>

<!-- Secondary action -->
<Button variant="subtle">Cancel</Button>

<!-- Tertiary/icon action -->
<Button variant="ghost" icon="more-horizontal" />

<!-- Destructive action -->
<Button variant="solid" theme="red">Delete</Button>
```

### With icons

```vue
<!-- Icon prefix -->
<Button variant="solid">
  <template #prefix><FeatherIcon name="plus" class="w-4 h-4" /></template>
  New Lead
</Button>

<!-- Icon only -->
<Button variant="ghost" icon="settings" />

<!-- Loading state -->
<Button variant="solid" :loading="saving">
  {{ saving ? 'Saving...' : 'Save' }}
</Button>
```

### Button groups

```vue
<ButtonGroup>
  <Button>Left</Button>
  <Button>Center</Button>
  <Button>Right</Button>
</ButtonGroup>
```

## Form Controls

### Basic inputs

```vue
<!-- Text input -->
<FormControl
  label="Full Name"
  type="text"
  v-model="form.name"
  :required="true"
  placeholder="Enter name"
/>

<!-- Email with validation -->
<FormControl
  label="Email"
  type="email"
  v-model="form.email"
  :error="emailError"
  description="We'll never share your email"
/>

<!-- Textarea -->
<FormControl
  label="Description"
  type="textarea"
  v-model="form.description"
  :rows="4"
/>
```

### Select and Link

```vue
<!-- Static options -->
<FormControl
  label="Status"
  type="select"
  v-model="form.status"
  :options="[
    { label: 'Open', value: 'Open' },
    { label: 'Closed', value: 'Closed' }
  ]"
/>

<!-- Link to DocType (with async search) -->
<FormControl
  label="Customer"
  type="link"
  v-model="form.customer"
  doctype="Customer"
  :filters="{ status: 'Active' }"
/>
```

### Date and time

```vue
<!-- Date picker -->
<FormControl
  label="Due Date"
  type="date"
  v-model="form.due_date"
/>

<!-- Datetime -->
<FormControl
  label="Scheduled At"
  type="datetime"
  v-model="form.scheduled_at"
/>
```

### Checkbox and switch

```vue
<!-- Checkbox -->
<FormControl
  label="I agree to terms"
  type="checkbox"
  v-model="form.agree"
/>

<!-- Switch for toggles -->
<div class="flex items-center justify-between">
  <div>
    <p class="font-medium">Email notifications</p>
    <p class="text-sm text-gray-500">Receive email updates</p>
  </div>
  <Switch v-model="settings.email_notifications" />
</div>
```

## Lists and Tables

### Basic list

```vue
<ListView
  :columns="columns"
  :rows="rows"
  :options="{
    selectable: true,
    onRowClick: handleRowClick
  }"
>
  <template #cell="{ column, row }">
    <Badge v-if="column.key === 'status'" :variant="statusVariant(row.status)">
      {{ row.status }}
    </Badge>
    <span v-else>{{ row[column.key] }}</span>
  </template>
</ListView>

<script setup>
const columns = [
  { label: 'Name', key: 'name', width: '200px' },
  { label: 'Status', key: 'status', width: '100px' },
  { label: 'Modified', key: 'modified', width: '150px' }
]
</script>
```

### Custom row rendering

```vue
<div class="divide-y">
  <div 
    v-for="item in items" 
    :key="item.name"
    class="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
    @click="select(item)"
  >
    <Avatar :label="item.title" :image="item.image" class="mr-3" />
    <div class="flex-1 min-w-0">
      <p class="font-medium truncate">{{ item.title }}</p>
      <p class="text-sm text-gray-500">{{ item.subtitle }}</p>
    </div>
    <Badge :variant="statusVariant(item.status)">{{ item.status }}</Badge>
    <Dropdown :options="rowActions" class="ml-2">
      <Button variant="ghost" icon="more-horizontal" />
    </Dropdown>
  </div>
</div>
```

## Dialogs and Modals

### Confirmation dialog

```vue
<Dialog
  v-model="showConfirm"
  :options="{
    title: 'Delete Lead?',
    message: 'This action cannot be undone.',
    actions: [
      { label: 'Cancel', onClick: () => showConfirm = false },
      { label: 'Delete', variant: 'solid', theme: 'red', onClick: handleDelete }
    ]
  }"
/>
```

### Form dialog

```vue
<Dialog v-model="showForm" :options="{ title: 'New Lead', size: 'lg' }">
  <template #body-content>
    <div class="space-y-4">
      <FormControl label="Name" v-model="newLead.name" />
      <FormControl label="Email" v-model="newLead.email" type="email" />
      <FormControl label="Source" v-model="newLead.source" type="select" :options="sources" />
    </div>
  </template>
  <template #actions>
    <Button @click="showForm = false">Cancel</Button>
    <Button variant="solid" @click="createLead" :loading="creating">Create</Button>
  </template>
</Dialog>
```

### Nested dialogs

```vue
<!-- Avoid deeply nested dialogs. Use side panels instead. -->
<Dialog v-model="showEdit">
  <template #body-content>
    <FormFields :doc="editDoc" />
    <!-- Instead of nested dialog, emit event to parent -->
    <Button @click="$emit('show-advanced')">Advanced Options</Button>
  </template>
</Dialog>
```

## Dropdowns and Menus

### Action dropdown

```vue
<Dropdown
  :options="[
    { label: 'Edit', icon: 'edit-2', onClick: edit },
    { label: 'Duplicate', icon: 'copy', onClick: duplicate },
    { component: 'separator' },
    { label: 'Delete', icon: 'trash-2', onClick: confirmDelete, theme: 'red' }
  ]"
>
  <Button variant="ghost" icon="more-horizontal" />
</Dropdown>
```

### Filter dropdown

```vue
<Dropdown
  :options="filterOptions"
  v-model="selectedFilter"
>
  <Button variant="subtle">
    <template #prefix><FeatherIcon name="filter" class="w-4 h-4" /></template>
    {{ selectedFilter?.label || 'All' }}
    <template #suffix><FeatherIcon name="chevron-down" class="w-4 h-4" /></template>
  </Button>
</Dropdown>
```

## Avatars and Badges

### Avatar sizes

```vue
<!-- Small (list items) -->
<Avatar :label="user.name" :image="user.image" size="sm" />

<!-- Medium (default) -->
<Avatar :label="user.name" :image="user.image" />

<!-- Large (profile headers) -->
<Avatar :label="user.name" :image="user.image" size="lg" />

<!-- With status indicator -->
<div class="relative">
  <Avatar :label="user.name" :image="user.image" />
  <span class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
</div>
```

### Badge variants

```vue
<!-- Status badges -->
<Badge variant="subtle">Draft</Badge>
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Overdue</Badge>

<!-- Count badges -->
<Badge variant="solid">42</Badge>

<!-- Custom colors -->
<Badge class="bg-purple-100 text-purple-700">Custom</Badge>
```

## Tabs

### Basic tabs

```vue
<Tabs v-model="activeTab">
  <Tab name="details" label="Details" />
  <Tab name="activity" label="Activity" />
  <Tab name="notes" label="Notes" />
</Tabs>

<div class="mt-4">
  <DetailsPanel v-if="activeTab === 'details'" :doc="doc" />
  <ActivityFeed v-else-if="activeTab === 'activity'" :doctype="doctype" :name="doc.name" />
  <NotesList v-else :doctype="doctype" :name="doc.name" />
</div>
```

### Tabs with counts

```vue
<Tabs v-model="activeTab">
  <Tab name="all">
    All <Badge class="ml-2">{{ allCount }}</Badge>
  </Tab>
  <Tab name="open">
    Open <Badge class="ml-2" variant="warning">{{ openCount }}</Badge>
  </Tab>
  <Tab name="closed">
    Closed <Badge class="ml-2">{{ closedCount }}</Badge>
  </Tab>
</Tabs>
```

## Tooltips

```vue
<!-- Basic tooltip -->
<Tooltip text="Click to edit">
  <Button variant="ghost" icon="edit-2" />
</Tooltip>

<!-- Tooltip for truncated text -->
<Tooltip :text="fullText" :disabled="!isTruncated">
  <p class="truncate">{{ fullText }}</p>
</Tooltip>

<!-- Tooltip with HTML -->
<Tooltip>
  <template #content>
    <div class="text-sm">
      <p class="font-medium">{{ user.name }}</p>
      <p class="text-gray-400">{{ user.email }}</p>
    </div>
  </template>
  <Avatar :label="user.name" />
</Tooltip>
```

## Loading States

### Skeleton components

```vue
<!-- Text skeleton -->
<Skeleton class="h-4 w-32" />

<!-- Multi-line -->
<div class="space-y-2">
  <Skeleton class="h-4 w-full" />
  <Skeleton class="h-4 w-3/4" />
</div>

<!-- Circle (avatar) -->
<Skeleton class="h-10 w-10 rounded-full" />

<!-- Card skeleton -->
<div class="border rounded-lg p-4 space-y-3">
  <Skeleton class="h-6 w-1/3" />
  <Skeleton class="h-4 w-full" />
  <Skeleton class="h-4 w-2/3" />
</div>
```

### List skeleton

```vue
<template>
  <div v-if="loading" class="divide-y">
    <div v-for="i in pageSize" :key="i" class="flex items-center p-3 gap-3">
      <Skeleton class="h-10 w-10 rounded-full" />
      <div class="flex-1 space-y-2">
        <Skeleton class="h-4 w-1/3" />
        <Skeleton class="h-3 w-1/2" />
      </div>
      <Skeleton class="h-6 w-16 rounded" />
    </div>
  </div>
</template>
```

## Empty States

```vue
<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
      <FeatherIcon :name="icon" class="w-8 h-8 text-gray-400" />
    </div>
    <h3 class="font-medium text-gray-900 mb-1">{{ title }}</h3>
    <p class="text-sm text-gray-500 max-w-sm mb-4">{{ description }}</p>
    <Button v-if="action" variant="solid" @click="action.handler">
      <template #prefix><FeatherIcon name="plus" class="w-4 h-4" /></template>
      {{ action.label }}
    </Button>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'inbox' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  action: { type: Object, default: null }
})
</script>
```

## Error States

```vue
<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mb-4">
      <FeatherIcon name="alert-triangle" class="w-8 h-8 text-red-500" />
    </div>
    <h3 class="font-medium text-gray-900 mb-1">Something went wrong</h3>
    <p class="text-sm text-gray-500 max-w-sm mb-4">{{ error.message }}</p>
    <Button variant="subtle" @click="retry">
      <template #prefix><FeatherIcon name="refresh-cw" class="w-4 h-4" /></template>
      Try Again
    </Button>
  </div>
</template>
```
