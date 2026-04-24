<template>
  <div class="w-full">
    <div class="flex flex-col gap-4 md:flex-row md:items-end">
      <!-- Main Search Input -->
      <div class="flex-1">
        <label for="search-input" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('search.keyword') || 'Search Jobs' }}
        </label>
        <div class="relative">
          <input
            id="search-input"
            v-model="localQuery"
            type="text"
            :placeholder="$t('search.placeholder') || 'Job title, company, or keyword...'"
            class="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            @keyup.enter="handleSearch"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            @click="clearSearch"
          >
            <svg v-if="localQuery" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Site Selection -->
      <div class="w-full md:w-48">
        <label for="site-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('search.site') || 'Job Site' }}
        </label>
        <select
          id="site-select"
          v-model="localSite"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value="">{{ $t('search.allSites') || 'All Sites' }}</option>
          <option value="linkedin">LinkedIn</option>
          <option value="indeed">Indeed</option>
          <option value="wuzzuf">Wuzzuf</option>
          <option value="bayt">Bayt</option>
        </select>
      </div>

      <!-- Advanced Search Toggle -->
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 border border-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
        @click="toggleAdvanced"
      >
        {{ showAdvanced ? $t('search.hideAdvanced') || 'Hide Advanced' : $t('search.showAdvanced') || 'Advanced' }}
      </button>

      <!-- Search Button -->
      <button
        type="button"
        class="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors"
        @click="handleSearch"
      >
        {{ $t('search.search') || 'Search' }}
      </button>
    </div>

    <!-- Advanced Search Options -->
    <transition name="slide-down">
      <div v-if="showAdvanced" class="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Job Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('search.jobType') || 'Job Type' }}
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="filters.jobTypes"
                  type="checkbox"
                  value="full-time"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('search.fullTime') || 'Full Time' }}</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="filters.jobTypes"
                  type="checkbox"
                  value="part-time"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('search.partTime') || 'Part Time' }}</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="filters.jobTypes"
                  type="checkbox"
                  value="contract"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('search.contract') || 'Contract' }}</span>
              </label>
            </div>
          </div>

          <!-- Remote -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('search.remote') || 'Remote' }}
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="filters.remote"
                  type="checkbox"
                  value="remote"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('search.remoteOnly') || 'Remote Only' }}</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="filters.remote"
                  type="checkbox"
                  value="hybrid"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('search.hybrid') || 'Hybrid' }}</span>
              </label>
            </div>
          </div>

          <!-- Experience Level -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('search.experience') || 'Experience Level' }}
            </label>
            <select
              v-model="filters.experienceLevel"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">{{ $t('search.any') || 'Any' }}</option>
              <option value="entry">{{ $t('search.entry') || 'Entry Level' }}</option>
              <option value="mid">{{ $t('search.mid') || 'Mid Level' }}</option>
              <option value="senior">{{ $t('search.senior') || 'Senior' }}</option>
            </select>
          </div>

          <!-- Posted Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('search.postedDate') || 'Posted Date' }}
            </label>
            <select
              v-model="filters.postedDate"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">{{ $t('search.anytime') || 'Anytime' }}</option>
              <option value="1">{{ $t('search.last24h') || 'Last 24 hours' }}</option>
              <option value="7">{{ $t('search.last7d') || 'Last 7 days' }}</option>
              <option value="30">{{ $t('search.last30d') || 'Last 30 days' }}</option>
            </select>
          </div>
        </div>

        <!-- Clear Filters Button -->
        <div class="mt-4 flex justify-end">
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            @click="clearFilters"
          >
            {{ $t('search.clearFilters') || 'Clear Filters' }}
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
