<script setup lang="ts">
const year = new Date().getFullYear();
</script>

<template>
  <footer class="border-t border-gray-200 dark:border-gray-800 py-8 mt-16">
    <div class="max-w-5xl mx-auto px-4 text-center text-sm text-gray-500 dark:text-gray-400">
      <p>&copy; {{ year }} My Blog. Built with Vue 3 + FastAPI.</p>
      <p class="mt-1">
        <a href="/api/v1/rss" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">RSS Feed</a>
      </p>
    </div>
  </footer>
</template>
