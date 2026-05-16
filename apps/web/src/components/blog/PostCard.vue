<script setup lang="ts">
import type { PostListItem } from "@/types";
import { useFormatDate } from "@/composables/useFormatDate";

defineProps<{ post: PostListItem }>();

const { formatDate } = useFormatDate();
</script>

<template>
  <article
    class="group border-b border-gray-100 dark:border-gray-800 py-6 first:pt-0 last:border-0 hover:bg-gray-50/50 dark:hover:bg-gray-900/50 -mx-4 px-4 rounded-lg transition-colors"
  >
    <div class="flex items-start gap-2 flex-wrap mb-2">
      <span
        v-if="post.featured"
        class="text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 px-2 py-0.5 rounded-full font-medium"
      >
        精选
      </span>
      <router-link
        v-for="tag in post.tags"
        :key="tag.id"
        :to="`/tag/${tag.slug}`"
        class="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      >
        {{ tag.name }}
      </router-link>
    </div>
    <router-link :to="`/post/${post.slug}`" class="block">
      <h2 class="text-lg font-semibold group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors mb-1.5">
        {{ post.title }}
      </h2>
      <p v-if="post.excerpt" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
        {{ post.excerpt }}
      </p>
    </router-link>
    <div class="flex items-center gap-3 text-xs text-gray-400 dark:text-gray-500">
      <time :datetime="post.created_at">{{ formatDate(post.created_at) }}</time>
      <span>{{ post.view_count }} 阅读</span>
    </div>
  </article>
</template>
