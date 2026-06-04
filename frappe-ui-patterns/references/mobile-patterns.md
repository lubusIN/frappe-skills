# Mobile Patterns

Responsive design patterns for Frappe applications.

## Breakpoints

Frappe UI apps use TailwindCSS breakpoints:

| Breakpoint | Min Width | Typical Device |
|------------|-----------|----------------|
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large screens |

## Responsive Shell

### Collapsible sidebar

```vue
<template>
  <div class="flex h-screen">
    <!-- Desktop sidebar -->
    <aside 
      v-show="!isMobile"
      class="w-56 border-r bg-gray-50 flex-shrink-0"
    >
      <Sidebar />
    </aside>
    
    <!-- Mobile drawer -->
    <Transition name="slide">
      <div 
        v-if="isMobile && sidebarOpen"
        class="fixed inset-0 z-50 flex"
      >
        <!-- Backdrop -->
        <div 
          class="fixed inset-0 bg-black/50"
          @click="sidebarOpen = false"
        />
        <!-- Drawer -->
        <aside class="relative w-64 bg-white shadow-xl">
          <Button 
            variant="ghost" 
            icon="x" 
            class="absolute top-2 right-2"
            @click="sidebarOpen = false"
          />
          <Sidebar />
        </aside>
      </div>
    </Transition>
    
    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Mobile header -->
      <header v-if="isMobile" class="h-12 border-b flex items-center px-4">
        <Button variant="ghost" icon="menu" @click="sidebarOpen = true" />
        <span class="ml-3 font-medium">{{ pageTitle }}</span>
      </header>
      
      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMediaQuery } from '@vueuse/core'

const isMobile = useMediaQuery('(max-width: 1023px)')
const sidebarOpen = ref(false)
</script>

<style>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}
.slide-enter-from aside,
.slide-leave-to aside {
  transform: translateX(-100%);
}
</style>
```

### Mobile-first layout

```vue
<template>
  <!-- Stack on mobile, side-by-side on desktop -->
  <div class="flex flex-col lg:flex-row h-full">
    <!-- List: full width on mobile, half on desktop when detail open -->
    <div 
      :class="[
        'lg:border-r',
        selectedDoc 
          ? 'hidden lg:block lg:w-1/2' 
          : 'w-full'
      ]"
    >
      <ListView :data="items" @select="selectDoc" />
    </div>
    
    <!-- Detail: full screen on mobile, side panel on desktop -->
    <div 
      v-if="selectedDoc"
      :class="[
        'w-full lg:w-1/2',
        isMobile && 'fixed inset-0 bg-white z-40'
      ]"
    >
      <DetailPanel 
        :doc="selectedDoc" 
        @close="selectedDoc = null"
        :showBackButton="isMobile"
      />
    </div>
  </div>
</template>
```

## Responsive Components

### Responsive table → cards

```vue
<template>
  <!-- Table on desktop -->
  <table class="hidden md:table w-full">
    <thead>
      <tr>
        <th v-for="col in columns" :key="col.key">{{ col.label }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="row.name">
        <td v-for="col in columns" :key="col.key">{{ row[col.key] }}</td>
      </tr>
    </tbody>
  </table>
  
  <!-- Cards on mobile -->
  <div class="md:hidden space-y-3 p-4">
    <div 
      v-for="row in rows" 
      :key="row.name"
      class="bg-white border rounded-lg p-4 shadow-sm"
    >
      <div class="flex items-center justify-between mb-2">
        <span class="font-medium">{{ row.name }}</span>
        <Badge :variant="statusVariant(row.status)">{{ row.status }}</Badge>
      </div>
      <div class="text-sm text-gray-600 space-y-1">
        <p>{{ row.customer }}</p>
        <p>{{ formatDate(row.date) }}</p>
      </div>
    </div>
  </div>
</template>
```

### Responsive filters

```vue
<template>
  <div>
    <!-- Desktop: inline filters -->
    <div class="hidden md:flex items-center gap-2">
      <Input type="search" v-model="search" placeholder="Search..." />
      <Select v-model="statusFilter" :options="statusOptions" />
      <Select v-model="sortBy" :options="sortOptions" />
    </div>
    
    <!-- Mobile: filter sheet -->
    <div class="md:hidden flex items-center gap-2">
      <Input type="search" v-model="search" placeholder="Search..." class="flex-1" />
      <Button variant="subtle" @click="showFilters = true">
        <FeatherIcon name="filter" class="w-4 h-4" />
        <Badge v-if="activeFilterCount" class="ml-1">{{ activeFilterCount }}</Badge>
      </Button>
    </div>
    
    <!-- Filter bottom sheet -->
    <BottomSheet v-model="showFilters" title="Filters">
      <div class="space-y-4 p-4">
        <FormControl label="Status" type="select" v-model="statusFilter" :options="statusOptions" />
        <FormControl label="Sort by" type="select" v-model="sortBy" :options="sortOptions" />
      </div>
      <template #footer>
        <Button class="flex-1" @click="clearFilters">Clear</Button>
        <Button class="flex-1" variant="solid" @click="applyFilters">Apply</Button>
      </template>
    </BottomSheet>
  </div>
</template>
```

### Responsive actions

```vue
<template>
  <!-- Desktop: button row -->
  <div class="hidden md:flex items-center gap-2">
    <Button>Edit</Button>
    <Button>Duplicate</Button>
    <Button>Share</Button>
    <Button variant="subtle" theme="red">Delete</Button>
  </div>
  
  <!-- Mobile: FAB + action sheet -->
  <div class="md:hidden">
    <Button 
      variant="solid" 
      class="fixed bottom-4 right-4 rounded-full w-14 h-14 shadow-lg"
      @click="showActions = true"
    >
      <FeatherIcon name="more-vertical" class="w-6 h-6" />
    </Button>
    
    <ActionSheet v-model="showActions">
      <ActionSheetItem icon="edit-2" @click="edit">Edit</ActionSheetItem>
      <ActionSheetItem icon="copy" @click="duplicate">Duplicate</ActionSheetItem>
      <ActionSheetItem icon="share" @click="share">Share</ActionSheetItem>
      <ActionSheetItem icon="trash-2" theme="red" @click="confirmDelete">Delete</ActionSheetItem>
    </ActionSheet>
  </div>
</template>
```

## Bottom Sheet Component

```vue
<!-- BottomSheet.vue -->
<template>
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="modelValue" class="fixed inset-0 z-50">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50" @click="close" />
        
        <!-- Sheet -->
        <div class="absolute bottom-0 inset-x-0 bg-white rounded-t-xl max-h-[90vh] flex flex-col">
          <!-- Handle -->
          <div class="flex justify-center py-2">
            <div class="w-10 h-1 bg-gray-300 rounded-full" />
          </div>
          
          <!-- Header -->
          <div v-if="title" class="px-4 pb-2 border-b">
            <h3 class="font-semibold">{{ title }}</h3>
          </div>
          
          <!-- Content -->
          <div class="flex-1 overflow-auto">
            <slot />
          </div>
          
          <!-- Footer -->
          <div v-if="$slots.footer" class="p-4 border-t flex gap-2">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: String
})

const emit = defineEmits(['update:modelValue'])
const close = () => emit('update:modelValue', false)
</script>

<style>
.sheet-enter-active,
.sheet-leave-active {
  transition: all 0.3s ease;
}
.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
}
.sheet-enter-from > div:last-child,
.sheet-leave-to > div:last-child {
  transform: translateY(100%);
}
</style>
```

## Touch Interactions

### Swipe actions

```vue
<template>
  <div 
    class="relative overflow-hidden"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- Actions revealed on swipe -->
    <div class="absolute inset-y-0 right-0 flex">
      <button class="w-20 bg-blue-500 text-white">Edit</button>
      <button class="w-20 bg-red-500 text-white">Delete</button>
    </div>
    
    <!-- Main content -->
    <div 
      class="relative bg-white"
      :style="{ transform: `translateX(${offset}px)` }"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const offset = ref(0)
const startX = ref(0)
const threshold = 100

const onTouchStart = (e) => {
  startX.value = e.touches[0].clientX
}

const onTouchMove = (e) => {
  const diff = e.touches[0].clientX - startX.value
  offset.value = Math.min(0, Math.max(-160, diff))
}

const onTouchEnd = () => {
  if (offset.value < -threshold) {
    offset.value = -160 // Snap to reveal actions
  } else {
    offset.value = 0 // Reset
  }
}
</script>
```

### Pull to refresh

```vue
<template>
  <div 
    class="relative overflow-hidden"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- Refresh indicator -->
    <div 
      class="absolute top-0 left-0 right-0 flex justify-center py-4 transition-transform"
      :style="{ transform: `translateY(${Math.min(pullDistance - 60, 0)}px)` }"
    >
      <FeatherIcon 
        name="refresh-cw" 
        :class="['w-6 h-6 transition-transform', refreshing && 'animate-spin']"
        :style="{ transform: `rotate(${pullDistance * 2}deg)` }"
      />
    </div>
    
    <!-- Content -->
    <div 
      class="transition-transform"
      :style="{ transform: `translateY(${pulling ? pullDistance : 0}px)` }"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['refresh'])

const pulling = ref(false)
const pullDistance = ref(0)
const refreshing = ref(false)
const startY = ref(0)
const threshold = 80

const onTouchStart = (e) => {
  if (window.scrollY === 0) {
    startY.value = e.touches[0].clientY
    pulling.value = true
  }
}

const onTouchMove = (e) => {
  if (pulling.value) {
    pullDistance.value = Math.max(0, (e.touches[0].clientY - startY.value) * 0.5)
  }
}

const onTouchEnd = async () => {
  if (pullDistance.value > threshold) {
    refreshing.value = true
    await new Promise(r => emit('refresh', r))
    refreshing.value = false
  }
  pulling.value = false
  pullDistance.value = 0
}
</script>
```

## Safe Areas

Handle notches and home indicators:

```css
/* In your global CSS */
.safe-area-inset {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Fixed bottom elements */
.fixed-bottom-safe {
  padding-bottom: calc(1rem + env(safe-area-inset-bottom));
}
```

```vue
<!-- Fixed bottom bar with safe area -->
<div class="fixed bottom-0 inset-x-0 bg-white border-t pb-[env(safe-area-inset-bottom)]">
  <div class="flex items-center justify-around p-2">
    <NavItem icon="home" label="Home" />
    <NavItem icon="search" label="Search" />
    <NavItem icon="user" label="Profile" />
  </div>
</div>
```

## Testing Responsive Designs

1. **Browser DevTools**: Use Chrome/Firefox responsive mode
2. **Real devices**: Test on actual phones/tablets
3. **Common viewport sizes**:
   - iPhone SE: 375x667
   - iPhone 14: 390x844
   - iPad: 768x1024
   - iPad Pro: 1024x1366

```javascript
// Utility for testing
const breakpoints = {
  mobile: '(max-width: 639px)',
  tablet: '(min-width: 640px) and (max-width: 1023px)',
  desktop: '(min-width: 1024px)'
}

// In component
import { useMediaQuery } from '@vueuse/core'

const isMobile = useMediaQuery(breakpoints.mobile)
const isTablet = useMediaQuery(breakpoints.tablet)
const isDesktop = useMediaQuery(breakpoints.desktop)
```
