<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PostCard from "@/components/blog/PostCard.vue";
import type { PostListItem, PaginatedResponse } from "@/types";
import { searchPosts } from "@/api/posts";
import { track } from "@/tracking";

const route = useRoute();
const router = useRouter();
const query = ref((route.query.q as string) || "");
const posts = ref<PostListItem[]>([]);
const loading = ref(false);
const searched = ref(false);
const currentPage = ref(1);
const totalPages = ref(0);
const total = ref(0);

async function doSearch(page = 1) {
  const q = query.value.trim();
  if (!q) return;

  loading.value = true;
  searched.value = true;
  try {
    const res: PaginatedResponse<PostListItem> = await searchPosts(q, page);
    posts.value = res.items;
    totalPages.value = res.pages;
    total.value = res.total;
    currentPage.value = res.page;
    router.replace({ query: { q } });
    track("search", { query: q, results_count: res.total });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (query.value) doSearch();
});

watch(() => route.query.q, (q) => {
  query.value = (q as string) || "";
  if (query.value) doSearch();
});

function onSubmit() {
  doSearch(1);
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">搜索文章</h1>

    <form @submit.prevent="onSubmit" class="mb-8">
      <div class="flex gap-2">
        <input
          v-model="query"
          type="search"
          placeholder="输入关键词搜索..."
          class="flex-1 px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
        />
        <button
          type="submit"
          class="px-6 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          搜索
        </button>
      </div>
    </form>

    <div v-if="loading" class="space-y-6">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="h-5 bg-gray-200 dark:bg-gray-800 rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"></div>
      </div>
    </div>

    <div v-else-if="searched">
      <p class="text-sm text-gray-400 mb-6">搜索 "{{ query }}" 找到 {{ total }} 篇相关文章</p>
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
      <div v-if="posts.length === 0" class="text-center py-12 text-gray-400">
        <p>未找到相关文章</p>
      </div>

      <nav v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="doSearch(p)"
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
  </div>
</template>
