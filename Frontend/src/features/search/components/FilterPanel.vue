<template>
  <div class="fluent-card bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-sm overflow-hidden">
    <!-- Panel Header -->
    <div class="px-6 py-4 bg-gray-50/50 dark:bg-gray-800/30 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
      <h2 class="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-widest flex items-center">
        <svg class="w-4 h-4 mr-2 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        Filters
      </h2>
      <button
        v-if="hasActiveFilters"
        type="button"
        class="text-xs font-bold text-[#0078d4] hover:text-[#005a9e] uppercase tracking-widest transition-colors"
        @click="resetFilters"
      >
        Reset
      </button>
    </div>

    <div class="p-6 space-y-8">
      <!-- Location Search -->
      <div class="space-y-3">
        <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-1">Location</label>
        <div class="relative group">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="w-4 h-4 text-gray-400 group-focus-within:text-[#0078d4] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <input
            v-model="location"
            type="text"
            placeholder="City, State or Remote"
            class="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-transparent focus:border-[#0078d4] rounded text-sm focus:ring-4 focus:ring-[#0078d4]/10 dark:text-white transition-all shadow-inner"
            @input="updateLocation"
          />
        </div>
      </div>

      <!-- Salary Range -->
      <div class="space-y-4">
        <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-1">Salary Range</label>
        <div class="px-2 pt-2">
          <div class="flex justify-between text-xs font-medium mb-4">
            <span class="text-[#0078d4]">{{ formatCurrency(minSalary) }}</span>
            <span class="text-gray-400 dark:text-gray-500">to</span>
            <span class="text-[#0078d4]">{{ formatCurrency(maxSalary) }}</span>
          </div>
          <div class="space-y-6">
            <div class="relative h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
              <input
                v-model.number="minSalary"
                type="range"
                min="0"
                max="500000"
                step="5000"
                class="absolute inset-0 w-full h-1.5 opacity-0 cursor-pointer z-20"
                @input="updateSalaryRange"
              />
              <div class="absolute h-full bg-[#0078d4] rounded-full z-10" :style="{ left: '0', width: (minSalary / 500000 * 100) + '%' }"></div>
            </div>
            <div class="relative h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full">
              <input
                v-model.number="maxSalary"
                type="range"
                min="0"
                max="500000"
                step="5000"
                class="absolute inset-0 w-full h-1.5 opacity-0 cursor-pointer z-20"
                @input="updateSalaryRange"
              />
              <div class="absolute h-full bg-[#0078d4] rounded-full z-10" :style="{ left: '0', width: (maxSalary / 500000 * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Job Type -->
      <div class="space-y-3">
        <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-1">Job Type</label>
        <div class="grid grid-cols-1 gap-2">
          <label v-for="type in [
            { id: 'full-time', label: 'Full Time' },
            { id: 'part-time', label: 'Part Time' },
            { id: 'contract', label: 'Contract' },
            { id: 'internship', label: 'Internship' }
          ]" :key="type.id" class="flex items-center p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-800 group cursor-pointer transition-colors">
            <input
              v-model="jobTypes"
              type="checkbox"
              :value="type.id"
              class="w-4 h-4 text-[#0078d4] border-gray-300 rounded focus:ring-[#0078d4] cursor-pointer"
              @change="updateJobTypes"
            />
            <span class="ml-3 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">{{ type.label }}</span>
          </label>
        </div>
      </div>

      <!-- Experience Level -->
      <div class="space-y-3">
        <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-1">Experience</label>
        <div class="grid grid-cols-1 gap-2">
          <label v-for="level in [
            { id: '', label: 'Any Level' },
            { id: 'entry', label: 'Entry Level' },
            { id: 'mid', label: 'Mid Level' },
            { id: 'senior', label: 'Senior Level' }
          ]" :key="level.id" class="flex items-center p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-800 group cursor-pointer transition-colors">
            <input
              v-model="experienceLevel"
              type="radio"
              :value="level.id"
              class="w-4 h-4 text-[#0078d4] border-gray-300 focus:ring-[#0078d4] cursor-pointer"
              @change="updateExperience"
            />
            <span class="ml-3 text-sm text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200 transition-colors">{{ level.label }}</span>
          </label>
        </div>
      </div>

      <!-- Posted Date -->
      <div class="space-y-3">
        <label class="block text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-1">Date Posted</label>
        <FormSelect
          v-model="postedDate"
          :options="dateOptions"
          placeholder="Anytime"
          @update:model-value="updatePostedDate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import FormSelect from '@/shared/components/ui/FormSelect.vue'

interface FilterState {
  minSalary: number
  maxSalary: number
  location: string
  jobTypes: string[]
  remote: string[]
  experienceLevel: string
  postedDate: string
  companySizes: string[]
}

const props = withDefaults(
  defineProps<{
    filters?: FilterState
  }>(),
  {
    filters: () => ({
      minSalary: 0,
      maxSalary: 500000,
      location: '',
      jobTypes: [],
      remote: [],
      experienceLevel: '',
      postedDate: '',
      companySizes: []
    })
  }
)

const emit = defineEmits<{
  'update:filters': [value: FilterState]
  'filter-change': [value: FilterState]
}>()

const minSalary = ref(props.filters.minSalary)
const maxSalary = ref(props.filters.maxSalary)
const location = ref(props.filters.location)
const jobTypes = ref(props.filters.jobTypes)
const remoteOptions = ref(props.filters.remote)
const experienceLevel = ref(props.filters.experienceLevel)
const postedDate = ref(props.filters.postedDate)
const companySizes = ref(props.filters.companySizes)

const dateOptions = [
  { value: '', label: 'Anytime' },
  { value: '1', label: 'Last 24 hours' },
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' }
]

const hasActiveFilters = computed(() => {
  return (
    minSalary.value > 0 ||
    maxSalary.value < 500000 ||
    location.value !== '' ||
    jobTypes.value.length > 0 ||
    remoteOptions.value.length > 0 ||
    experienceLevel.value !== '' ||
    postedDate.value !== '' ||
    companySizes.value.length > 0
  )
})

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0
  }).format(value)
}

const emitFilterChange = () => {
  const filters: FilterState = {
    minSalary: minSalary.value,
    maxSalary: maxSalary.value,
    location: location.value,
    jobTypes: jobTypes.value,
    remote: remoteOptions.value,
    experienceLevel: experienceLevel.value,
    postedDate: postedDate.value,
    companySizes: companySizes.value
  }
  emit('update:filters', filters)
  emit('filter-change', filters)
}

const updateSalaryRange = () => {
  if (minSalary.value > maxSalary.value) {
    ;[minSalary.value, maxSalary.value] = [maxSalary.value, minSalary.value]
  }
  emitFilterChange()
}

const updateLocation = () => {
  emitFilterChange()
}

const updateJobTypes = () => {
  emitFilterChange()
}

const updateExperience = () => {
  emitFilterChange()
}

const updatePostedDate = () => {
  emitFilterChange()
}

const resetFilters = () => {
  minSalary.value = 0
  maxSalary.value = 500000
  location.value = ''
  jobTypes.value = []
  remoteOptions.value = []
  experienceLevel.value = ''
  postedDate.value = ''
  companySizes.value = []
  emitFilterChange()
}
</script>
