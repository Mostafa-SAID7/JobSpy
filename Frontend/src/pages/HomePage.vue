<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <section class="text-center py-16">
      <h1 class="text-5xl font-bold text-gray-900 dark:text-white mb-4">
        Find your ideal job
      </h1>
      <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">
        A comprehensive platform gathering the best job opportunities from top global and regional job boards
      </p>

      <!-- Search Bar -->
      <div class="max-w-2xl mx-auto">
        <div class="flex gap-2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search for a job..."
            class="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            @keyup.enter="handleSearch"
          />
          <button
            @click="handleSearch"
            class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Search
          </button>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <StatsCard
        label="Total Jobs"
        :value="totalJobs"
        subtitle="available jobs"
        :trend="12"
        trend-label="increase this month"
      />
      <StatsCard
        label="Registered Companies"
        :value="totalCompanies"
        subtitle="trusted companies"
        :trend="8"
        trend-label="new companies"
      />
      <StatsCard
        label="Job Seekers"
        :value="totalUsers"
        subtitle="active users"
        :trend="15"
        trend-label="new users"
      />
    </section>

    <!-- Features Section -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow">
        <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Advanced Search</h3>
        <p class="text-gray-600 dark:text-gray-400">
          Search for jobs using advanced criteria like salary, location, and experience
        </p>
      </div>

      <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow">
        <div class="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h6a2 2 0 012 2v12a2 2 0 01-2 2H7a2 2 0 01-2-2V5z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Save Jobs</h3>
        <p class="text-gray-600 dark:text-gray-400">
          Save your favorite jobs and return to them anytime
        </p>
      </div>

      <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md hover:shadow-lg transition-shadow">
        <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Smart Alerts</h3>
        <p class="text-gray-600 dark:text-gray-400">
          Get instant alerts when new jobs matching your criteria are posted
        </p>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="bg-blue-600 dark:bg-blue-700 text-white rounded-lg p-12 text-center">
      <h2 class="text-3xl font-bold mb-4">Start Searching Now</h2>
      <p class="text-lg mb-8">
        Join thousands of job seekers who found their ideal jobs
      </p>
      <RouterLink
        to="/jobs"
        class="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition-colors font-semibold"
      >
        Explore Jobs
      </RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StatsCard from '@/components/cards/StatsCard.vue'

const searchQuery = ref('')
const router = useRouter()

// Mock stats data
const totalJobs = ref(15234)
const totalCompanies = ref(892)
const totalUsers = ref(45678)

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'JobSearch',
      query: { q: searchQuery.value },
    })
  }
}
</script>
