# Styling Guide - JobSpy Frontend

## ⚠️ IMPORTANT: Centralized Styling Rules

### DO NOT Override Tailwind Config Styles

All form components MUST use the centralized Fluent Design classes defined in `tailwind.config.js`. 

**❌ NEVER DO THIS:**
```vue
<style scoped>
.my-select {
  background-color: white;
  border: 1px solid #ccc;
  /* ... duplicate styles */
}
</style>
```

**✅ ALWAYS DO THIS:**
```vue
<template>
  <select class="fluent-select">
    <!-- options -->
  </select>
</template>

<!-- NO scoped styles needed! -->
```

---

## Centralized Fluent Classes (from tailwind.config.js)

### `.fluent-input`
Used for: Text inputs, textareas

**Features:**
- Consistent padding: `0.625rem 1rem`
- Border: `1px solid gray-300`
- Border radius: `4px` (Fluent standard)
- Focus: Blue border (`#0078d4`) with box-shadow
- Hover: Darker border
- Dark mode: Automatic via `.dark &`

**Usage:**
```vue
<input class="fluent-input" type="text" />
```

### `.fluent-select`
Used for: Dropdown selects

**Features:**
- Consistent padding: `0.625rem 2.5rem 0.625rem 1rem` (extra right padding for icon)
- Border: `1px solid gray-300`
- Border radius: `4px`
- Focus: Blue border with box-shadow
- Hover: Darker border
- Dark mode: Automatic
- Option styling: Proper background/text colors for both modes
- `appearance: none` - removes default arrow

**Usage:**
```vue
<select class="fluent-select">
  <option>Option 1</option>
</select>
```

### `.fluent-button`
Used for: All buttons

**Features:**
- Inline flex with center alignment
- Padding: `0.5rem 1.25rem`
- Font weight: `600`
- Transition: `0.15s ease-in-out`
- Disabled state: `opacity: 0.6`

**Usage:**
```vue
<button class="fluent-button fluent-button-primary">
  Click Me
</button>
```

### `.fluent-button-primary`
Used for: Primary action buttons

**Features:**
- Background: Brand blue (`#0078d4`)
- Hover: Darker blue (`#106ebe`)
- Active: Even darker with scale effect

### `.fluent-card`
Used for: Card containers

**Features:**
- Background: White (dark: gray-900)
- Border: `1px solid gray-200`
- Border radius: `8px`
- Shadow: Fluent-sm
- Dark mode: Automatic

---

## Color Palette

### Brand Colors
```js
brand: {
  DEFAULT: '#0078d4',  // Primary blue
  hover: '#106ebe',    // Hover state
  active: '#005a9e',   // Active state
  light: '#2b88d8',    // Light variant
  dim: 'rgba(0, 120, 212, 0.1)', // Transparent
}
```

### Gray Scale (Fluent Design)
```js
gray: {
  950: '#0b0b0a', // Deep black
  900: '#11100f', // Dark background
  800: '#1b1a19', // Input dark bg
  700: '#252423', // Border dark
  600: '#323130',
  500: '#605e5c',
  400: '#a19f9d',
  300: '#c8c6c4', // Border light
  200: '#edebe9',
  100: '#f3f2f1', // Input disabled bg
  50: '#faf9f8',
}
```

### Semantic Colors
```js
success: '#107c10',
error: '#a4262c',
warning: '#ffb900',
info: '#0078d4',
```

---

## Component Styling Rules

### FormInput.vue
```vue
<input class="fluent-input" />
```
- Uses centralized `.fluent-input` class
- NO scoped styles
- Error state: Add Tailwind classes conditionally

### FormSelect.vue
```vue
<select class="fluent-select">
  <option>...</option>
</select>
```
- Uses centralized `.fluent-select` class
- NO scoped styles (except IE fix)
- Option colors handled by Tailwind config
- Icon positioned with Tailwind utility classes

### FormButton.vue
```vue
<button class="fluent-button fluent-button-primary">
  Button
</button>
```
- Uses centralized button classes
- NO custom styles

---

## Dark Mode

All Fluent classes automatically support dark mode via `.dark &` selector in Tailwind config.

**How it works:**
1. User toggles dark mode
2. `<html>` or `<body>` gets `class="dark"`
3. All `.dark &` styles activate automatically

**DO NOT:**
- Add manual dark mode styles in components
- Use `@media (prefers-color-scheme: dark)`
- Duplicate dark mode logic

**DO:**
- Use Tailwind's `dark:` prefix for one-off styles
- Trust the centralized Fluent classes

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Duplicate Styles
```vue
<style scoped>
.my-select {
  background-color: white;
  border: 1px solid #ccc;
}
</style>
```
**Problem:** Overrides centralized styles, breaks dark mode

### ❌ Mistake 2: Hardcoded Colors
```vue
<div style="background-color: #fff; border: 1px solid #ccc">
```
**Problem:** Doesn't respect theme, no dark mode

### ❌ Mistake 3: Custom Option Styling
```vue
<style scoped>
select option {
  background-color: white;
  color: black;
}
</style>
```
**Problem:** Already handled in Tailwind config

---

## ✅ Correct Approach

### Example: Custom Select Component
```vue
<template>
  <div :class="label ? 'mb-4' : ''">
    <label v-if="label" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      {{ label }}
    </label>
    
    <div class="relative">
      <select class="fluent-select">
        <option v-for="opt in options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      
      <!-- Icon -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500">
          <!-- icon path -->
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic
</script>

<style scoped>
/* ONLY browser-specific fixes, NO styling */
select::-ms-expand {
  display: none;
}
</style>
```

---

## Testing Checklist

When creating or modifying form components:

- [ ] Uses centralized Fluent class (`.fluent-input`, `.fluent-select`, etc.)
- [ ] NO duplicate styles in `<style scoped>`
- [ ] NO hardcoded colors
- [ ] Works in light mode
- [ ] Works in dark mode
- [ ] Focus state shows blue border
- [ ] Hover state changes border color
- [ ] Disabled state has reduced opacity
- [ ] Options are readable in both modes (for selects)

---

## File Structure

```
Frontend/
├── tailwind.config.js          # ⭐ SINGLE SOURCE OF TRUTH
├── src/
│   ├── components/
│   │   ├── forms/
│   │   │   ├── FormInput.vue   # Uses .fluent-input
│   │   │   ├── FormSelect.vue  # Uses .fluent-select
│   │   │   └── FormButton.vue  # Uses .fluent-button
│   │   └── ...
│   └── ...
```

---

## Summary

1. **All form styling is centralized in `tailwind.config.js`**
2. **Components use Fluent classes, NOT custom styles**
3. **Dark mode is automatic via `.dark &` selector**
4. **Option styling is handled in Tailwind config**
5. **Only add scoped styles for browser-specific fixes**

**Remember:** If you're writing CSS for form elements, you're probably doing it wrong! Use the centralized Fluent classes instead.
