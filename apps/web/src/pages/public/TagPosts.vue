<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PostCard from "@/components/blog/PostCard.vue";
import type { PostListItem, PaginatedResponse } from "@/types";
import { fetchPostsByTag } from "@/api/tags";

const route = useRoute();
const router = useRouter();
const posts = ref<PostListItem[]>([]);
const loading = ref(true);
const error = ref("");
const currentPage = ref(1);
const totalPages = ref(0);
const tagSlug = ref(route.params.slug as string);

async function load(page: number) {
  loading.value = true;
  error.value = "";
  try {
    const res: PaginatedResponse<PostListItem> = await fetchPostsByTag(tagSlug.value, page);
    posts.value = res.items;
    totalPages.value = res.pages;
    currentPage.value = res.page;
  } catch {
    error.value = "加载失败，请稍后重试";
  } finally {
    loading.value = false;
  }
}

function gotoPage(p: number) {
  currentPage.value = p;
  router.replace({ query: { page: p } });
  load(p);
}

onMounted(() => {
  const page = Number(route.query.page) || 1;
  currentPage.value = page;
  load(page);
});

watch(() => route.params.slug, (slug) => {
  tagSlug.value = slug as string;
  load(1);
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-2">标签: {{ tagSlug }}</h1>
    <p class="text-sm text-gray-400 mb-8">共 {{ posts.length }} 篇文章</p>

    <div v-if="loading" class="space-y-6">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="h-5 bg-gray-200 dark:bg-gray-800 rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"></div>
      </div>
    </div>

    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load(currentPage)" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <div v-else-if="posts.length === 0" class="text-center py-16 text-gray-400">
      <p>暂无此标签下的文章</p>
    </div>

    <PostCard v-for="post in posts" :key="post.id" :post="post" />

    <nav v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="gotoPage(p)"
        :class="[
          'px-3 py-1.5 text-sm rounded-lg transition-colors',
          p === currentPage
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700',
        ]"
      >
        {{ p }}
      </button>
    </nav>
  </div>
</template>
