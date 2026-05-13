<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Tag } from "@/types";
import { fetchTags } from "@/api/tags";
import TagCloud from "@/components/blog/TagCloud.vue";

const tags = ref<Tag[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    tags.value = await fetchTags();
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-12">
    <h1 class="text-2xl font-bold mb-8">标签</h1>
    <div v-if="loading" class="animate-pulse space-y-2">
      <div class="h-8 bg-gray-200 dark:bg-gray-800 rounded w-1/3"></div>
    </div>
    <TagCloud v-else :tags="tags" />
    <div v-if="!loading && tags.length === 0" class="text-center py-8 text-gray-400">
      暂无标签
    </div>
  </div>
</template>
