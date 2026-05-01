<template>
  <div class="w-full space-y-4">
    <div class="flex flex-col gap-3 md:flex-row md:items-end">
      <!-- Main Search Input -->
      <div class="flex-1">
        <label for="search-input" class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2 px-1">
          Keywords
        </label>
        <div class="relative group">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-gray-400 group-focus-within:text-[#0078d4] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            id="search-input"
            v-model="localQuery"
            type="text"
            placeholder="Job title, skills, or company..."
            class="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded focus:outline-none focus:ring-2 focus:ring-[#0078d4]/20 focus:border-[#0078d4] dark:text-white transition-all shadow-sm"
            @keyup.enter="handleSearch"
          />
          <button
            v-if="localQuery"
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            @click="clearSearch"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Site Selection -->
      <div class="w-full md:w-56">
        <label for="site-select" class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2 px-1">
          Source
        </label>
        <FormSelect
          id="site-select"
          v-model="localSite"
          :options="siteOptions"
          placeholder="All Sources"
        />
      </div>

      <!-- Advanced Search Toggle -->
      <FormButton
        variant="secondary"
        label="Advanced"
        class="w-full md:w-auto"
        @click="toggleAdvanced"
      >
        <svg class="w-4 h-4 transition-transform" :class="showAdvanced ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
        <span>Advanced</span>
      </FormButton>

      <!-- Search Button -->
      <FormButton
        label="Search Jobs"
        class="w-full md:w-auto"
        @click="handleSearch"
      />
    </div>

    <!-- Advanced Search Options -->
    <transition name="slide-down">
      <div v-if="showAdvanced" class="fluent-card mt-2 p-6 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800 shadow-xl">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <!-- Job Type -->
          <div class="space-y-3">
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest">Job Type</label>
            <div class="space-y-2">
              <label v-for="type in ['Full-time', 'Part-time', 'Contract', 'Internship']" :key="type" class="flex items-center group cursor-pointer">
                <input
                  v-model="filters.jobTypes"
                  type="checkbox"
                  :value="type.toLowerCase()"
                  class="w-4 h-4 text-[#0078d4] border-gray-300 rounded focus:ring-[#0078d4] transition-all cursor-pointer"
                />
                <span class="ml-2.5 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">{{ type }}</span>
              </label>
            </div>
          </div>

          <!-- Remote -->
          <div class="space-y-3">
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest">Work Mode</label>
            <div class="space-y-2">
              <label class="flex items-center group cursor-pointer">
                <input
                  v-model="filters.remote"
                  type="checkbox"
                  value="remote"
                  class="w-4 h-4 text-[#0078d4] border-gray-300 rounded focus:ring-[#0078d4] transition-all cursor-pointer"
                />
                <span class="ml-2.5 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">Remote Only</span>
              </label>
              <label class="flex items-center group cursor-pointer">
                <input
                  v-model="filters.remote"
                  type="checkbox"
                  value="hybrid"
                  class="w-4 h-4 text-[#0078d4] border-gray-300 rounded focus:ring-[#0078d4] transition-all cursor-pointer"
                />
                <span class="ml-2.5 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">Hybrid</span>
              </label>
            </div>
          </div>

          <!-- Experience Level -->
          <div class="space-y-3">
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest">Experience</label>
            <FormSelect
              v-model="filters.experienceLevel"
              :options="experienceOptions"
              placeholder="Any Level"
            />
          </div>

          <!-- Posted Date -->
          <div class="space-y-3">
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest">Date Posted</label>
            <FormSelect
              v-model="filters.postedDate"
              :options="dateOptions"
              placeholder="Anytime"
            />
          </div>
        </div>

        <!-- Advanced Footer -->
        <div class="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
          <button
            type="button"
            class="text-xs font-bold text-gray-400 hover:text-red-500 transition-colors uppercase tracking-widest"
            @click="clearFilters"
          >
            Reset all filters
          </button>
          <FormButton label="Apply Filters" size="sm" @click="handleSearch" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FormButton from '@/components/forms/FormButton.vue'
import FormSelect from '@/components/forms/FormSelect.vue'

interface SearchFilters {
  jobTypes: string[]
  remote: string[]
  experienceLevel: string
  postedDate: string
}

const props = withDefaults(
  defineProps<{
    modelValue?: string
    site?: string
    filters?: SearchFilters
  }>(),
  {
    modelValue: '',
    site: '',
    filters: () => ({
      jobTypes: [],
      remote: [],
      experienceLevel: '',
      postedDate: ''
    })
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:site': [value: string]
  'update:filters': [value: SearchFilters]
  search: [query: string, site: string, filters: SearchFilters]
}>()

const localQuery = ref(props.modelValue)
const localSite = ref(props.site)
const showAdvanced = ref(false)
const filters = ref<SearchFilters>(props.filters)

const siteOptions = [
  { value: '', label: 'All Sources' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'indeed', label: 'Indeed' },
  { value: 'wuzzuf', label: 'Wuzzuf' },
  { value: 'bayt', label: 'Bayt' }
]

const experienceOptions = [
  { value: '', label: 'Any Level' },
  { value: 'entry', label: 'Entry Level' },
  { value: 'mid', label: 'Mid Level' },
  { value: 'senior', label: 'Senior Level' }
]

const dateOptions = [
  { value: '', label: 'Anytime' },
  { value: '1', label: 'Last 24 hours' },
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' }
]

const handleSearch = () => {
  emit('update:modelValue', localQuery.value)
  emit('update:site', localSite.value)
  emit('update:filters', filters.value)
  emit('search', localQuery.value, localSite.value, filters.value)
}

const clearSearch = () => {
  localQuery.value = ''
  emit('update:modelValue', '')
}

const toggleAdvanced = () => {
  showAdvanced.value = !showAdvanced.value
}

const clearFilters = () => {
  filters.value = {
    jobTypes: [],
    remote: [],
    experienceLevel: '',
    postedDate: ''
  }
  emit('update:filters', filters.value)
}
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
