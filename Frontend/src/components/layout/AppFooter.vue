<template>
  <footer class="bg-gray-900 dark:bg-black text-gray-300 dark:text-gray-400 mt-16 transition-colors">
    <div class="w-full max-w-7xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        <!-- About -->
        <div>
          <h3 class="text-white dark:text-white font-bold mb-4">About JobSpy</h3>
          <p class="text-sm text-gray-400 dark:text-gray-500">
            A comprehensive job search platform gathering opportunities from top global job boards.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-white dark:text-white font-bold mb-4">Quick Links</h3>
          <ul class="space-y-2 text-sm">
            <li>
              <RouterLink to="/jobs" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
                Search Jobs
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/about" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
                About Us
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/contact" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
                Contact Us
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Support -->
        <div>
          <h3 class="text-white dark:text-white font-bold mb-4">Support</h3>
          <ul class="space-y-2 text-sm">
            <li>
              <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
                Help Center
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
                FAQ
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
                Privacy Policy
              </a>
            </li>
          </ul>
        </div>

        <!-- Social -->
        <div>
          <h3 class="text-white dark:text-white font-bold mb-4">Follow Us</h3>
          <div class="flex gap-4">
            <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
            <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2s9 5 20 5a9.5 9.5 0 00-9-5.5c4.75 2.25 7-7 7-7" />
              </svg>
            </a>
            <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.475-2.236-1.986-2.236-1.081 0-1.722.722-2.004 1.418-.103.249-.129.597-.129.946v5.441h-3.554s.05-8.81 0-9.728h3.554v1.375c.427-.659 1.191-1.595 2.897-1.595 2.117 0 3.704 1.385 3.704 4.362v5.586zM5.337 9.433c-1.144 0-1.915-.758-1.915-1.707 0-.955.77-1.708 1.963-1.708 1.192 0 1.915.753 1.938 1.708 0 .949-.746 1.707-1.986 1.707zm1.946 11.019H3.391V9.724h3.892v10.728zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z" />
              </svg>
            </a>
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-700 dark:border-gray-800 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-sm text-gray-400 dark:text-gray-500">© 2024 JobSpy. All rights reserved.</p>
          <div class="flex gap-6 mt-4 md:mt-0 text-sm">
            <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">Terms of Use</a>
            <a href="#" class="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-white transition-colors">Contact Us</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// Footer component
</script>
