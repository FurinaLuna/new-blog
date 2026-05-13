<script setup lang="ts">
defineProps<{
  summary: string;
  loading: boolean;
}>();
</script>

<template>
  <Transition name="fade">
    <div v-if="summary || loading" class="mb-12 relative group">
      <div class="absolute -inset-1 bg-gradient-to-r from-primary-500 to-primary-400 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-500"></div>
      <div class="relative bg-white dark:bg-gray-900 border border-primary-100 dark:border-primary-800/50 rounded-2xl p-6 shadow-sm overflow-hidden">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-primary-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 015.25-2.906z" />
            </svg>
          </div>
          <h4 class="text-xs font-bold uppercase tracking-[0.2em] text-primary-600 dark:text-primary-400">AI 内容摘要</h4>
          <div v-if="loading" class="flex gap-1 ml-auto">
            <span class="w-1 h-1 bg-primary-400 rounded-full animate-ping"></span>
            <span class="w-1 h-1 bg-primary-400 rounded-full animate-ping [animation-delay:0.2s]"></span>
          </div>
        </div>
        <p
          class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed italic"
          :class="{ 'animate-pulse bg-gray-100 dark:bg-gray-800 h-12 rounded': loading }"
        >
          {{ summary }}
        </p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
