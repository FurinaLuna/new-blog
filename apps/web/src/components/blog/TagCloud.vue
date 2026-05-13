<script setup lang="ts">
import type { Tag } from "@/types";

defineProps<{ tags: Tag[] }>();
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <router-link
      v-for="tag in tags"
      :key="tag.id"
      :to="`/tag/${tag.slug}`"
      class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all"
    >
      {{ tag.name }}
      <span class="text-xs text-gray-400 dark:text-gray-500">({{ tag.post_count || 0 }})</span>
    </router-link>
  </div>
</template>
