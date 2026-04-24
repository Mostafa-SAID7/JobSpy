# JobSpy Theme System Guide

## Quick Reference

### How Theme Toggle Works

1. **User clicks theme toggle button** (sun/moon icon in header)
2. **Theme preference is saved** to localStorage
3. **HTML element gets `dark` class** when dark mode is active
4. **All components respond** with dark mode styles

### Using Dark Mode in Components

#### Basic Pattern
```vue
<!-- Light mode (default) -->
<div class="bg-white text-gray-900">
  Light mode content
</div>

<!-- Dark mode (with dark: prefix) -->
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Works in both modes
</div>
```

#### Color Mapping

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Background | bg-white | dark:bg-gray-800 |
| Text | text-gray-900 | dark:text-white |
| Borders | border-gray-200 | dark:border-gray-700 |
| Hover | hover:bg-gray-100 | dark:hover:bg-gray-700 |
| Badges | bg-blue-100 | dark:bg-blue-900 |
| Badge Text | text-blue-700 | dark:text-blue-400 |

### Component Examples

#### Card Component
```vue
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
  <h3 class="text-gray-900 dark:text-white">Title</h3>
  <p class="text-gray-600 dark:text-gray-400">Description</p>
</div>
```

#### Button Component
```vue
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
  Click me
</button>

<!-- With dark mode -->
<button class="bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800 text-white px-4 py-2 rounded-lg transition-colors">
  Click me
</button>
```

#### Form Input
```vue
<input 
  class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-500"
  placeholder="Enter text..."
/>
```

---

## Color System

### Light Mode Palette
```
Primary Background: #ffffff (white)
Secondary Background: #f5f7fa (light gray)
Text Primary: #1a1a1a (dark gray)
Text Secondary: #666666 (medium gray)
Border: rgba(0,0,0,0.12)
Accent: #0078d4 (blue)
```

### Dark Mode Palette
```
Primary Background: #161616 (dark gray)
Secondary Background: #0e0e0e (very dark)
Text Primary: #f0f0f0 (light gray)
Text Secondary: #c8c8c8 (medium gray)
Border: rgba(255,255,255,0.12)
Accent: #0078d4 (blue) / #2899f5 (light blue)
```

---

## Tailwind Dark Mode Classes

### Background Colors
```
Light: bg-white, bg-gray-50, bg-gray-100
Dark: dark:bg-gray-800, dark:bg-gray-900, dark:bg-black
```

### Text Colors
```
Light: text-gray-900, text-gray-700, text-gray-600
Dark: dark:text-white, dark:text-gray-300, dark:text-gray-400
```

### Border Colors
```
Light: border-gray-200, border-gray-300
Dark: dark:border-gray-700, dark:border-gray-600
```

### Hover States
```
Light: hover:bg-gray-100, hover:text-blue-600
Dark: dark:hover:bg-gray-700, dark:hover:text-blue-400
```

### Transitions
```
transition-colors  /* Smooth color transitions */
transition-all     /* All property transitions */
```

---

## Component Checklist

When creating new components, ensure:

- [ ] Light mode colors applied
- [ ] Dark mode colors added with `dark:` prefix
- [ ] Proper contrast ratios verified
- [ ] Hover states defined for both modes
- [ ] Focus states visible
- [ ] Transitions smooth
- [ ] Icons have proper colors
- [ ] Badges/badges have dark variants
- [ ] Borders have dark variants
- [ ] Text has proper contrast

---

## Testing Theme

### In Browser
1. Open DevTools (F12)
2. Go to Console
3. Run: `document.documentElement.classList.add('dark')`
4. To remove: `document.documentElement.classList.remove('dark')`

### In Code
```javascript
// Check if dark mode is active
const isDark = document.documentElement.classList.contains('dark')

// Toggle dark mode
document.documentElement.classList.toggle('dark')

// Set dark mode
document.documentElement.classList.add('dark')

// Remove dark mode
document.documentElement.classList.remove('dark')
```

---

## Common Patterns

### Status Badges
```vue
<!-- Active (Green) -->
<span class="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-400 rounded-full text-xs font-medium">
  Active
</span>

<!-- Inactive (Gray) -->
<span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400 rounded-full text-xs font-medium">
  Inactive
</span>
```

### Info Boxes
```vue
<div class="bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
  <p class="text-blue-900 dark:text-blue-100">Information message</p>
</div>
```

### Cards with Hover
```vue
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg dark:hover:shadow-lg transition-shadow p-6 border border-gray-200 dark:border-gray-700">
  Content
</div>
```

### Disabled States
```vue
<button disabled class="opacity-50 cursor-not-allowed bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400">
  Disabled
</button>
```

---

## Performance Tips

1. **Use `transition-colors`** instead of `transition-all` for better performance
2. **Avoid unnecessary dark: prefixes** on elements that don't need them
3. **Group related dark: classes** for readability
4. **Use CSS variables** for complex color schemes
5. **Test performance** with DevTools Lighthouse

---

## Accessibility

### Color Contrast Requirements
- **Normal text**: 4.5:1 ratio (WCAG AA)
- **Large text**: 3:1 ratio (WCAG AA)
- **Both modes**: Must meet requirements

### Testing Contrast
1. Use WebAIM Contrast Checker
2. Use Chrome DevTools color picker
3. Use Lighthouse audit
4. Test with actual users

### Focus States
```vue
<!-- Always visible focus -->
<button class="focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400">
  Focusable
</button>
```

---

## Troubleshooting

### Theme not persisting
- Check localStorage is enabled
- Verify `localStorage.setItem('theme', 'dark')` is called
- Check browser privacy settings

### Colors not changing
- Verify `dark:` prefix is used
- Check Tailwind config includes dark mode
- Verify HTML element has `dark` class
- Check CSS is compiled

### Contrast issues
- Use WebAIM Contrast Checker
- Verify color values in Tailwind config
- Test with actual users
- Use accessibility tools

### Performance issues
- Use `transition-colors` not `transition-all`
- Minimize dark: prefixes
- Use CSS variables for complex schemes
- Profile with DevTools

---

## Resources

- [Tailwind Dark Mode Docs](https://tailwindcss.com/docs/dark-mode)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WCAG Color Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [MDN Dark Mode Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)

---

**Last Updated**: April 24, 2026
**Version**: 1.0
