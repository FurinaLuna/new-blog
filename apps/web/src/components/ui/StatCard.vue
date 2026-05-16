<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  title: string;
  value: string | number;
  icon: string;
  trend?: number;
  trendLabel?: string;
  loading?: boolean;
}>();

const iconSvg = computed(() => {
  const icons: Record<string, string> = {
    eye: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>',
    "file-text":
      '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>',
    "message-circle":
      '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>',
    edit: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>',
  };
  return icons[props.icon] || icons["eye"];
});

const trendUp = computed(() => props.trend !== undefined && props.trend >= 0);
</script>

<template>
  <div
    class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 transition-shadow hover:shadow-md"
  >
    <div v-if="loading" class="animate-pulse flex items-center gap-4">
      <div class="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
      <div class="flex-1 space-y-2">
        <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
        <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
      </div>
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
    </div>

    <div v-else class="flex items-center gap-4">
      <div
        class="w-10 h-10 rounded-lg flex items-center justify-center bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 shrink-0"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" v-html="iconSvg"></svg>
      </div>

      <div class="flex-1 min-w-0">
        <p class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ title }}</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-0.5">{{ value }}</p>
      </div>

      <div v-if="trend !== undefined" class="shrink-0 text-right">
        <div
          :class="[
            'inline-flex items-center gap-0.5 text-sm font-medium',
            trendUp ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400',
          ]"
        >
          <svg v-if="trendUp" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          {{ Math.abs(trend) }}%
        </div>
        <p v-if="trendLabel" class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ trendLabel }}</p>
      </div>
    </div>
  </div>
</template>
