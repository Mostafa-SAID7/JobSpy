<template>
  <div class="w-full bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ $t('filters.title') || 'Filters' }}
      </h2>
      <button
        v-if="hasActiveFilters"
        type="button"
        class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
        @click="resetFilters"
      >
        {{ $t('filters.reset') || 'Reset All' }}
      </button>
    </div>

    <div class="space-y-6">
      <!-- Salary Range -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.salary') || 'Salary Range' }}
        </h3>
        <div class="space-y-3">
          <div>
            <label class="text-xs text-gray-600 dark:text-gray-400">
              {{ $t('filters.min') || 'Minimum' }}: {{ formatCurrency(minSalary) }}
            </label>
            <input
              v-model.number="minSalary"
              type="range"
              min="0"
              max="500000"
              step="10000"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              @input="updateSalaryRange"
            />
          </div>
          <div>
            <label class="text-xs text-gray-600 dark:text-gray-400">
              {{ $t('filters.max') || 'Maximum' }}: {{ formatCurrency(maxSalary) }}
            </label>
            <input
              v-model.number="maxSalary"
              type="range"
              min="0"
              max="500000"
              step="10000"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              @input="updateSalaryRange"
            />
          </div>
        </div>
      </div>

      <!-- Location -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.location') || 'Location' }}
        </h3>
        <input
          v-model="location"
          type="text"
          :placeholder="$t('filters.locationPlaceholder') || 'Enter city or country...'"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          @input="updateLocation"
        />
      </div>

      <!-- Job Type -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.jobType') || 'Job Type' }}
        </h3>
        <div class="space-y-2">
          <label class="flex items-center">
            <input
              v-model="jobTypes"
              type="checkbox"
              value="full-time"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateJobTypes"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.fullTime') || 'Full Time' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="jobTypes"
              type="checkbox"
              value="part-time"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateJobTypes"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.partTime') || 'Part Time' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="jobTypes"
              type="checkbox"
              value="contract"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateJobTypes"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.contract') || 'Contract' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="jobTypes"
              type="checkbox"
              value="temporary"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateJobTypes"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.temporary') || 'Temporary' }}</span>
          </label>
        </div>
      </div>

      <!-- Remote Work -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.workArrangement') || 'Work Arrangement' }}
        </h3>
        <div class="space-y-2">
          <label class="flex items-center">
            <input
              v-model="remoteOptions"
              type="checkbox"
              value="remote"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateRemote"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.remoteOnly') || 'Remote Only' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="remoteOptions"
              type="checkbox"
              value="hybrid"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateRemote"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.hybrid') || 'Hybrid' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="remoteOptions"
              type="checkbox"
              value="onsite"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateRemote"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.onsite') || 'On-site' }}</span>
          </label>
        </div>
      </div>

      <!-- Experience Level -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.experience') || 'Experience Level' }}
        </h3>
        <div class="space-y-2">
          <label class="flex items-center">
            <input
              v-model="experienceLevel"
              type="radio"
              value=""
              class="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
              @change="updateExperience"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.any') || 'Any' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="experienceLevel"
              type="radio"
              value="entry"
              class="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
              @change="updateExperience"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.entry') || 'Entry Level' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="experienceLevel"
              type="radio"
              value="mid"
              class="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
              @change="updateExperience"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.mid') || 'Mid Level' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="experienceLevel"
              type="radio"
              value="senior"
              class="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
              @change="updateExperience"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.senior') || 'Senior' }}</span>
          </label>
        </div>
      </div>

      <!-- Posted Date -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.postedDate') || 'Posted Date' }}
        </h3>
        <select
          v-model="postedDate"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          @change="updatePostedDate"
        >
          <option value="">{{ $t('filters.anytime') || 'Anytime' }}</option>
          <option value="1">{{ $t('filters.last24h') || 'Last 24 hours' }}</option>
          <option value="7">{{ $t('filters.last7d') || 'Last 7 days' }}</option>
          <option value="30">{{ $t('filters.last30d') || 'Last 30 days' }}</option>
          <option value="90">{{ $t('filters.last90d') || 'Last 90 days' }}</option>
        </select>
      </div>

      <!-- Company Size -->
      <div>
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          {{ $t('filters.companySize') || 'Company Size' }}
        </h3>
        <div class="space-y-2">
          <label class="flex items-center">
            <input
              v-model="companySizes"
              type="checkbox"
              value="startup"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateCompanySize"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.startup') || 'Startup' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="companySizes"
              type="checkbox"
              value="small"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateCompanySize"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.small') || 'Small (1-50)' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="companySizes"
              type="checkbox"
              value="medium"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateCompanySize"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.medium') || 'Medium (51-500)' }}</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="companySizes"
              type="checkbox"
              value="large"
              class="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              @change="updateCompanySize"
            />
            <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ $t('filters.large') || 'Large (500+)' }}</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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

const updateRemote = () => {
  emitFilterChange()
}

const updateExperience = () => {
  emitFilterChange()
}

const updatePostedDate = () => {
  emitFilterChange()
}

const updateCompanySize = () => {
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
