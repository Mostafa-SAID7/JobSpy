<template>
  <div class="space-y-16 py-8">
    <!-- Hero Section -->
    <section class="relative overflow-hidden py-20 px-6 text-center">
      <div class="absolute inset-0 -z-10 bg-gradient-to-b from-blue-50 to-transparent dark:from-blue-900/10 dark:to-transparent"></div>
      <div class="max-w-4xl mx-auto space-y-8">
        <h1 class="text-4xl md:text-6xl font-extrabold text-gray-900 dark:text-white tracking-tight leading-tight">
          Find your next career <span class="text-[#0078d4]">breakthrough</span>
        </h1>
        <p class="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
          The most comprehensive job aggregation platform. We gather the best opportunities from global and regional job boards so you don't have to.
        </p>

        <!-- Search Bar -->
        <div class="max-w-2xl mx-auto pt-4">
          <div class="flex flex-col sm:flex-row gap-3 p-2 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800 shadow-lg focus-within:ring-2 focus-within:ring-[#0078d4]/20 transition-all">
            <div class="flex-1 flex items-center px-4 gap-3">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Job title, keywords, or company"
                class="w-full py-2 bg-transparent border-none focus:ring-0 text-gray-900 dark:text-white text-base"
                @keyup.enter="handleSearch"
              />
            </div>
            <FormButton
              label="Search"
              @click="handleSearch"
              class="w-full sm:w-auto"
            />
          </div>
          <div class="flex flex-wrap justify-center gap-2 mt-4 text-xs text-gray-500 font-medium uppercase tracking-widest">
            <span>Trending:</span>
            <button @click="searchQuery = 'Frontend Developer'; handleSearch()" class="hover:text-[#0078d4] underline underline-offset-4 decoration-gray-300 transition-colors">Frontend</button>
            <button @click="searchQuery = 'Backend Engineer'; handleSearch()" class="hover:text-[#0078d4] underline underline-offset-4 decoration-gray-300 transition-colors">Backend</button>
            <button @click="searchQuery = 'Product Manager'; handleSearch()" class="hover:text-[#0078d4] underline underline-offset-4 decoration-gray-300 transition-colors">Product</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="grid grid-cols-1 md:grid-cols-3 gap-6 px-4">
      <StatsCard
        label="Active Listings"
        :value="totalJobs.toLocaleString()"
        subtitle="Jobs updated in real-time"
        :trend="12"
      />
      <StatsCard
        label="Trusted Companies"
        :value="totalCompanies.toLocaleString()"
        subtitle="Across 45+ industries"
        :trend="8"
        variant="success"
      />
      <StatsCard
        label="Active Seekers"
        :value="totalUsers.toLocaleString()"
        subtitle="People found jobs this week"
        :trend="15"
        variant="info"
      />
    </section>

    <!-- Features Section -->
    <section class="py-12 space-y-12 px-4">
      <div class="text-center max-w-2xl mx-auto space-y-4">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white">Why professionals choose JobSpy</h2>
        <p class="text-gray-600 dark:text-gray-400">Our tools are designed to make your job search faster, smarter, and more effective.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="fluent-card bg-white dark:bg-gray-900 p-8 rounded border border-gray-200 dark:border-gray-800 transition-all space-y-4">
          <div class="w-12 h-12 bg-blue-50 dark:bg-blue-900/30 rounded flex items-center justify-center">
            <svg class="w-6 h-6 text-[#0078d4]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Global Search</h3>
          <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
            Access millions of job listings from thousands of sites, all in one centralized search engine.
          </p>
        </div>

        <div class="fluent-card bg-white dark:bg-gray-900 p-8 rounded border border-gray-200 dark:border-gray-800 transition-all space-y-4">
          <div class="w-12 h-12 bg-green-50 dark:bg-green-900/30 rounded flex items-center justify-center">
            <svg class="w-6 h-6 text-[#107c10]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h6a2 2 0 012 2v12a2 2 0 01-2 2H7a2 2 0 01-2-2V5z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Job Tracking</h3>
          <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
            Save interesting opportunities and track your application status across multiple platforms.
          </p>
        </div>

        <div class="fluent-card bg-white dark:bg-gray-900 p-8 rounded border border-gray-200 dark:border-gray-800 transition-all space-y-4">
          <div class="w-12 h-12 bg-purple-50 dark:bg-purple-900/30 rounded flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Instant Alerts</h3>
          <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
            Never miss an opening. Get notified immediately when a job matches your specific career goals.
          </p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="relative bg-[#0078d4] dark:bg-blue-700 text-white rounded p-12 text-center overflow-hidden">
      <div class="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-white/10 to-transparent"></div>
      <h2 class="text-3xl md:text-4xl font-bold mb-6">Ready to take the next step?</h2>
      <p class="text-lg text-blue-50 mb-10 max-w-xl mx-auto">
        Join over 45,000 professionals finding their ideal roles every day. Your future is waiting.
      </p>
      <div class="flex flex-col sm:flex-row justify-center gap-4">
        <RouterLink
          to="/auth/register"
          class="px-8 py-3 bg-white text-[#0078d4] rounded hover:bg-gray-100 transition-all font-bold shadow-md active:scale-95"
        >
          Create Free Account
        </RouterLink>
        <RouterLink
          to="/jobs"
          class="px-8 py-3 bg-blue-500/30 hover:bg-blue-500/50 text-white border border-white/30 rounded transition-all font-bold backdrop-blur-sm active:scale-95"
        >
          Explore Jobs
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StatsCard from '@/components/cards/StatsCard.vue'
import FormButton from '@/components/forms/FormButton.vue'

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
