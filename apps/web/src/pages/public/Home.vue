<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import PostCard from "@/components/blog/PostCard.vue";
import type { PostListItem, PaginatedResponse } from "@/types";
import { fetchPosts } from "@/api/posts";

const route = useRoute();
const posts = ref<PostListItem[]>([]);
const loading = ref(true);
const currentPage = ref(1);
const totalPages = ref(0);
const size = 10;

async function load(page: number) {
  loading.value = true;
  try {
    const res: PaginatedResponse<PostListItem> = await fetchPosts(page, size);
    posts.value = res.items;
    totalPages.value = res.pages;
    currentPage.value = res.page;
  } finally {
    loading.value = false;
  }
}

onMounted(() => load(1));

watch(() => route.query.page, (p) => {
  load(Number(p) || 1);
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <!-- Hero -->
    <section class="mb-12 text-center">
      <h1 class="text-3xl font-bold mb-3">My Blog</h1>
      <p class="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
        技术分享、学习笔记与生活思考
      </p>
    </section>

    <!-- Featured posts -->
    <section v-if="posts.length > 0" class="mb-8">
      <div v-if="loading" class="space-y-6">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <div class="h-5 bg-gray-200 dark:bg-gray-800 rounded w-3/4 mb-2"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/3 mt-2"></div>
        </div>
      </div>
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </section>

    <!-- Empty -->
    <div v-if="!loading && posts.length === 0" class="text-center py-16 text-gray-400">
      <p class="text-lg mb-2">暂无文章</p>
      <p class="text-sm">新文章正在路上...</p>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="load(p)"
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
