<script setup lang="ts">
import type { PostListItem } from "@/types";

defineProps<{
  prevPost: PostListItem | null;
  nextPost: PostListItem | null;
}>();
</script>

<template>
  <nav class="mt-20 pt-10 border-t border-gray-100 dark:border-gray-800 grid grid-cols-1 sm:grid-cols-2 gap-6">
    <router-link
      v-if="prevPost"
      :to="`/post/${prevPost.slug}`"
      class="group p-6 rounded-2xl border border-gray-100 dark:border-gray-800 hover:border-primary-200 dark:hover:border-primary-800 hover:bg-primary-50/30 dark:hover:bg-primary-900/10 transition-all"
    >
      <span class="text-[10px] font-bold uppercase tracking-widest text-gray-400 group-hover:text-primary-500 transition-colors">Previous Article</span>
      <p class="mt-2 font-bold text-gray-700 dark:text-gray-200 group-hover:text-primary-600 transition-colors">{{ prevPost.title }}</p>
    </router-link>
    <div v-else></div>

    <router-link
      v-if="nextPost"
      :to="`/post/${nextPost.slug}`"
      class="group p-6 rounded-2xl border border-gray-100 dark:border-gray-800 hover:border-primary-200 dark:hover:border-primary-800 hover:bg-primary-50/30 dark:hover:bg-primary-900/10 transition-all text-right"
    >
      <span class="text-[10px] font-bold uppercase tracking-widest text-gray-400 group-hover:text-primary-500 transition-colors">Next Article</span>
      <p class="mt-2 font-bold text-gray-700 dark:text-gray-200 group-hover:text-primary-600 transition-colors">{{ nextPost.title }}</p>
    </router-link>
  </nav>
</template>
