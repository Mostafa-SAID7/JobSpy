<template>
  <footer class="bg-[#f3f2f1] dark:bg-[#11100f] border-t border-gray-200 dark:border-gray-800 mt-20 transition-all">
    <div class="w-full max-w-6xl mx-auto px-6 py-16">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12 mb-12">
        <!-- Brand -->
        <div class="space-y-4">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-[#0078d4] rounded flex items-center justify-center">
              <span class="text-white font-bold text-xs">JS</span>
            </div>
            <span class="text-lg font-bold text-gray-900 dark:text-white tracking-tight">JobSpy</span>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Connecting professionals with global opportunities through intelligent job aggregation and tracking.
          </p>
        </div>

        <!-- Explore -->
        <div>
          <h3 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-widest mb-5">Explore</h3>
          <ul class="space-y-3">
            <li>
              <RouterLink to="/jobs" class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors">
                Search Jobs
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/saved-jobs" class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors">
                Saved Jobs
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/alerts" class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors">
                Alerts
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Resources -->
        <div>
          <h3 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-widest mb-5">Resources</h3>
          <ul class="space-y-3">
            <li>
              <a href="#" class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors">
                Help Center
              </a>
            </li>
            <li>
              <a href="#" class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors">
                Privacy Policy
              </a>
            </li>
            <li>
              <a href="#" class="text-sm text-gray-600 dark:text-gray-400 hover:text-[#0078d4] dark:hover:text-blue-400 transition-colors">
                Terms of Service
              </a>
            </li>
          </ul>
        </div>

        <!-- Connect -->
        <div>
          <h3 class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-widest mb-5">Connect</h3>
          <div class="flex gap-4">
            <a href="#" class="w-10 h-10 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400 hover:text-[#0078d4] hover:border-[#0078d4] transition-all shadow-sm">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
            <a href="#" class="w-10 h-10 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-400 hover:text-[#0078d4] hover:border-[#0078d4] transition-all shadow-sm">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2s9 5 20 5a9.5 9.5 0 00-9-5.5c4.75 2.25 7-7 7-7" />
              </svg>
            </a>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-200 dark:border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <p class="text-xs text-gray-500 dark:text-gray-500 font-medium tracking-tight">
          © 2024 JobSpy. Designed with Fluent principles.
        </p>
        <div class="flex gap-8 text-xs font-medium text-gray-500 dark:text-gray-500">
          <a href="#" class="hover:text-[#0078d4] transition-colors">Privacy</a>
          <a href="#" class="hover:text-[#0078d4] transition-colors">Terms</a>
          <a href="#" class="hover:text-[#0078d4] transition-colors">Cookie Policy</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// Footer component
</script>
