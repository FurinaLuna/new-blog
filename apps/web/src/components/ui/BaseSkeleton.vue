<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(defineProps<{ lines?: number }>(), { lines: 6 });

const widths = computed(() =>
  Array.from({ length: props.lines }, () => `${70 + Math.random() * 30}%`),
);
</script>

<template>
  <div class="animate-pulse space-y-4">
    <div class="h-4 bg-gray-200 dark:bg-gray-800 rounded w-1/4"></div>
    <div class="h-8 bg-gray-200 dark:bg-gray-800 rounded w-3/4"></div>
    <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/5"></div>
    <div class="h-48 bg-gray-100 dark:bg-gray-800 rounded-2xl w-full mt-4"></div>
    <div
      v-for="(width, i) in widths"
      :key="i"
      class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"
      :style="{ width }"
    ></div>
  </div>
</template>
