<template>
  <aside
    class="fixed left-0 top-16 h-[calc(100vh-64px)] w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto transition-transform duration-300"
    :class="{ '-translate-x-full': !isOpen }"
  >
    <div class="p-6">
      <!-- Sidebar Header -->
      <h2 class="text-lg font-semibold text-gray-900 mb-6">Filters</h2>

      <!-- Search Filters -->
      <div class="space-y-6">
        <!-- Job Type Filter -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3">Job Type</h3>
          <div class="space-y-2">
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="filters.jobType"
                value="fulltime"
                class="w-4 h-4 text-blue-600 rounded"
              />
              <span class="ml-3 text-sm text-gray-700">Full-time</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="filters.jobType"
                value="parttime"
                class="w-4 h-4 text-blue-600 rounded"
              />
              <span class="ml-3 text-sm text-gray-700">Part-time</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="filters.jobType"
                value="internship"
                class="w-4 h-4 text-blue-600 rounded"
              />
              <span class="ml-3 text-sm text-gray-700">Internship</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="filters.jobType"
                value="contract"
                class="w-4 h-4 text-blue-600 rounded"
              />
              <span class="ml-3 text-sm text-gray-700">Contract</span>
            </label>
          </div>
        </div>

        <!-- Remote Filter -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3">Work Type</h3>
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="filters.isRemote"
              class="w-4 h-4 text-blue-600 rounded"
            />
            <span class="ml-3 text-sm text-gray-700">Remote</span>
          </label>
        </div>

        <!-- Salary Range Filter -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3">Salary Range</h3>
          <div class="space-y-3">
            <div>
              <label class="text-xs text-gray-600">Minimum</label>
              <input
                type="number"
                v-model.number="filters.salaryMin"
                placeholder="0"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label class="text-xs text-gray-600">Maximum</label>
              <input
                type="number"
                v-model.number="filters.salaryMax"
                placeholder="999999"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
          </div>
        </div>

        <!-- Location Filter -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3">Location</h3>
          <input
            type="text"
            v-model="filters.location"
            placeholder="Enter location"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>

        <!-- Posted Date Filter -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3">Posted Date</h3>
          <select v-model="filters.postedDate" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">All</option>
            <option value="24">Last 24 hours</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-2 pt-4">
          <button
            @click="applyFilters"
            class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Apply
          </button>
          <button
            @click="clearFilters"
            class="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  </aside>

  <!-- Overlay for mobile -->
  <div
    v-if="!isOpen"
    @click="$emit('close')"
    class="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Filters {
  jobType: string[]
  isRemote: boolean
  salaryMin: number | null
  salaryMax: number | null
  location: string
  postedDate: string
}

defineProps({
  isOpen: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['apply-filters', 'clear-filters', 'close'])

const filters = ref<Filters>({
  jobType: [],
  isRemote: false,
  salaryMin: null,
  salaryMax: null,
  location: '',
  postedDate: ''
})

const applyFilters = () => {
  emit('apply-filters', filters.value)
}

const clearFilters = () => {
  filters.value = {
    jobType: [],
    isRemote: false,
    salaryMin: null,
    salaryMax: null,
    location: '',
    postedDate: ''
  }
  emit('clear-filters')
}
</script>
