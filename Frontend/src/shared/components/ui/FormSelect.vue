<template>
  <div :class="label ? 'mb-4' : ''" class="relative" ref="dropdownRef">
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <div class="relative">
      <button
        type="button"
        :id="id"
        :disabled="disabled"
        class="fluent-select-trigger"
        :class="[
          error ? 'border-red-500 ring-red-500/20' : '',
          isOpen ? 'ring-2 ring-[#0078d4]/20 border-[#0078d4]' : ''
        ]"
        @click="toggleDropdown"
      >
        <div class="flex items-center truncate">
          <!-- Icon for the selected value -->
          <component 
            v-if="selectedOption?.icon" 
            :is="selectedOption.icon" 
            class="w-4 h-4 mr-2.5 text-gray-400 group-hover:text-[#0078d4]"
          />
          <span :class="!selectedLabel ? 'text-gray-400' : 'text-gray-900 dark:text-gray-100'">
            {{ selectedLabel || placeholder }}
          </span>
        </div>
        <svg
          class="w-4 h-4 text-gray-400 transition-transform duration-200"
          :class="isOpen ? 'rotate-180' : ''"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Custom Dropdown Menu -->
      <transition name="dropdown">
        <div
          v-if="isOpen"
          class="absolute z-[100] w-full mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-xl overflow-hidden py-1 max-h-60 overflow-y-auto"
        >
          <div
            v-for="option in normalizedOptions"
            :key="option.value"
            class="px-3 py-2 text-sm cursor-pointer flex items-center transition-colors group"
            :class="[
              modelValue === option.value 
                ? 'bg-[#0078d4]/10 text-[#0078d4] font-semibold' 
                : 'text-gray-700 dark:text-gray-300 hover:bg-[#0078d4] hover:text-white'
            ]"
            @click="selectOption(option)"
          >
            <!-- Site/Date Icon in Option -->
            <div v-if="option.icon" class="mr-3">
              <component :is="option.icon" class="w-4 h-4" />
            </div>
            <span class="flex-1">{{ option.label }}</span>
            <svg v-if="modelValue === option.value" class="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </transition>
    </div>

    <!-- Error/Hint messages -->
    <p v-if="error" class="mt-1 text-sm text-red-500 dark:text-red-400">{{ error }}</p>
    <p v-if="hint && !error" class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h, defineComponent } from 'vue'

interface Option {
  value: string | number
  label: string
  icon?: any
}

type OptionType = Option | string | number

interface Props {
  modelValue: string | number
  options: OptionType[]
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  placeholder: 'Select option',
  id: () => `select-${Math.random().toString(36).substr(2, 9)}`
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: []
  focus: []
}>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

// Normalize options to always have value, label, and optional icon logic
const normalizedOptions = computed(() => {
  return props.options.map(option => {
    let opt: Option;
    if (typeof option === 'object' && option !== null && 'value' in option) {
      opt = { ...option as Option };
    } else {
      opt = {
        value: option as string | number,
        label: String(option)
      }
    }

    // Auto-assign icons for specific known values (Sources/Dates)
    if (!opt.icon) {
      const val = String(opt.value).toLowerCase()
      if (val.includes('linkedin')) opt.icon = LinkedInIcon
      if (val.includes('indeed')) opt.icon = IndeedIcon
      if (val.includes('glassdoor')) opt.icon = GlassdoorIcon
      if (val.includes('google')) opt.icon = GoogleIcon
      if (val.includes('zip_recruiter')) opt.icon = ZipIcon
      if (val === '1' || val === '7' || val === '30') opt.icon = CalendarIcon
    }

    return opt
  })
})

const selectedOption = computed(() => {
  return normalizedOptions.value.find(opt => opt.value === props.modelValue)
})

const selectedLabel = computed(() => {
  return selectedOption.value?.label || ''
})

const toggleDropdown = () => {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
    if (isOpen.value) emit('focus')
  }
}

const selectOption = (option: Option) => {
  emit('update:modelValue', option.value)
  isOpen.value = false
  emit('blur')
}

// Click outside logic
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})

// --- Embedded SVG Components for premium look ---
const LinkedInIcon = defineComponent({ render() { return h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z' })]) } })
const IndeedIcon = defineComponent({ render() { return h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M2.39 24L.43 21.05l4.31-3.4c2.29-1.8 3.32-3.1 3.32-5.18 0-1.87-1.12-2.9-2.9-2.9-1.93 0-3.14 1.25-3.32 3.33H0C.18 8.87 2.47 6.44 5.34 6.44c3.34 0 5.48 2.37 5.48 5.63 0 3.32-2 5.56-5.18 8.07L3.44 22H11v2H2.39zM24 8h-2V0h-2v8h-2v2h2v14h2V10h2V8z' })]) } })
const GlassdoorIcon = defineComponent({ render() { return h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zM7 10h10v4H7z' })]) } })
const GoogleIcon = defineComponent({ render() { return h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z' })]) } })
const ZipIcon = defineComponent({ render() { return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z' })]) } })
const CalendarIcon = defineComponent({ render() { return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2', ry: '2' }), h('line', { x1: '16', y1: '2', x2: '16', y2: '6' }), h('line', { x1: '8', y1: '2', x2: '8', y2: '6' }), h('line', { x1: '3', y1: '10', x2: '21', y2: '10' })]) } })
</script>

<style scoped>
.fluent-select-trigger {
  @apply w-full flex items-center justify-between pl-4 pr-3 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none transition-all cursor-pointer appearance-none shadow-sm font-medium;
}

.fluent-select-trigger:disabled {
  @apply bg-gray-50 dark:bg-gray-800/50 text-gray-400 cursor-not-allowed opacity-60;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

/* Custom scrollbar for dropdown */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-200 dark:bg-gray-700 rounded-full;
}
</style>
