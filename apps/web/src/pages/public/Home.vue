<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PostCard from "@/components/blog/PostCard.vue";
import { SITE_NAME, SITE_DESCRIPTION } from "@/utils/constants";
import type { PostListItem, PaginatedResponse } from "@/types";
import { fetchPosts } from "@/api/posts";

const route = useRoute();
const router = useRouter();
const posts = ref<PostListItem[]>([]);
const loading = ref(true);
const error = ref("");
const currentPage = ref(1);
const totalPages = ref(0);
const size = 10;

async function load(page: number) {
  loading.value = true;
  error.value = "";
  try {
    const res: PaginatedResponse<PostListItem> = await fetchPosts(page, size);
    posts.value = res.items;
    totalPages.value = res.pages;
    currentPage.value = res.page;
  } catch {
    error.value = "加载文章失败，请稍后重试";
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

watch(() => route.query.page, (p) => {
  const page = Number(p) || 1;
  currentPage.value = page;
  load(page);
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <!-- Hero -->
    <section class="mb-12 text-center">
      <h1 class="text-3xl font-bold mb-3">{{ SITE_NAME }}</h1>
      <p class="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
        {{ SITE_DESCRIPTION }}
      </p>
    </section>

    <!-- Error -->
    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load(currentPage)" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-6">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="h-5 bg-gray-200 dark:bg-gray-800 rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"></div>
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/3 mt-2"></div>
      </div>
    </div>

    <!-- Posts -->
    <section v-if="!loading && !error && posts.length > 0" class="mb-8">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </section>

    <!-- Empty -->
    <div v-if="!loading && !error && posts.length === 0" class="text-center py-16 text-gray-400">
      <p class="text-lg mb-2">暂无文章</p>
      <p class="text-sm">新文章正在路上...</p>
    </div>

    <!-- Pagination -->
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
