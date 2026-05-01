# Form Components

Reusable form components following Microsoft Fluent Design System.

## FormSelect Component

A dropdown select component with consistent Fluent styling matching the site's design system.

### Features

- **Fluent Design**: Matches `fluent-input` styling from Tailwind config
- **Flexible Options**: Supports objects `{ value, label }`, strings, or numbers
- **Dark Mode**: Automatic theme adaptation
- **Error States**: Built-in error message display
- **Helper Text**: Optional hint text
- **Accessibility**: Proper label associations and keyboard navigation

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string \| number` | `''` | Selected value (v-model) |
| `options` | `Array` | `[]` | Options array (objects, strings, or numbers) |
| `label` | `string` | - | Label text above select |
| `placeholder` | `string` | - | Placeholder option (empty value) |
| `error` | `string` | - | Error message to display |
| `hint` | `string` | - | Helper text below select |
| `required` | `boolean` | `false` | Required field indicator |
| `disabled` | `boolean` | `false` | Disabled state |
| `id` | `string` | auto | HTML id attribute |

### Events

| Event | Payload | Description |
|-------|---------|-------------|
| `update:modelValue` | `string \| number` | Emitted on selection change |
| `blur` | - | Emitted on blur |
| `focus` | - | Emitted on focus |

### Usage Examples

#### Basic with Object Options

```vue
<script setup>
import FormSelect from '@/components/forms/FormSelect.vue'
import { ref } from 'vue'

const selected = ref('')
const options = [
  { value: '1', label: 'Option 1' },
  { value: '2', label: 'Option 2' }
]
</script>

<template>
  <FormSelect
    v-model="selected"
    :options="options"
    label="Choose option"
    placeholder="Select..."
  />
</template>
```

#### Simple String Array

```vue
<FormSelect
  v-model="fruit"
  :options="['Apple', 'Banana', 'Orange']"
  label="Select fruit"
/>
```

#### With Error State

```vue
<FormSelect
  v-model="value"
  :options="options"
  label="Required Field"
  error="This field is required"
  required
/>
```

#### Inline (No Label)

```vue
<div class="flex items-center gap-3">
  <span class="text-sm">Sort by:</span>
  <FormSelect
    v-model="sortBy"
    :options="sortOptions"
  />
</div>
```

### Current Usage

- **JobSearchPage.vue** - Sort dropdown
- **Pagination.vue** - Page size selector
- **SearchBar.vue** - Source, experience, date filters
- **FilterPanel.vue** - Date posted filter
- **AlertsPage.vue** - Frequency and notification selectors

### Styling

The component uses the `.fluent-select` class which matches the Fluent Design System:

- **Colors**: Brand blue (#0078d4) for focus, gray scale for borders
- **Border Radius**: 4px (Fluent standard)
- **Transitions**: 0.15s ease-in-out
- **Focus State**: Blue border with box-shadow
- **Hover State**: Darker border color
- **Disabled State**: Gray background, reduced opacity

### Design System Alignment

This component follows the same design patterns as:
- `FormInput` (uses `.fluent-input`)
- `FormButton` (uses `.fluent-button`)
- All form components share consistent spacing, colors, and transitions

### Type Safety

Fully typed with TypeScript:
- Automatic type inference for option values
- Proper event payload types
- Props validation
