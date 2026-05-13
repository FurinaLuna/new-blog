<script setup lang="ts">
defineProps<{ lines?: number }>();
</script>

<template>
  <div class="animate-pulse space-y-4">
    <div class="h-4 bg-gray-200 dark:bg-gray-800 rounded w-1/4"></div>
    <div class="h-8 bg-gray-200 dark:bg-gray-800 rounded w-3/4"></div>
    <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/5"></div>
    <div class="h-48 bg-gray-100 dark:bg-gray-800 rounded-2xl w-full mt-4"></div>
    <div
      v-for="i in (lines ?? 6)"
      :key="i"
      class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"
      :style="{ width: `${70 + Math.random() * 30}%` }"
    ></div>
  </div>
</template>
