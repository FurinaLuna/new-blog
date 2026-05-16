<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PostCard from "@/components/blog/PostCard.vue";
import { SITE_NAME, SITE_DESCRIPTION } from "@/utils/constants";
import { useSeo } from "@/composables/useSeo";
import type { PostListItem, Tag, PaginatedResponse } from "@/types";
import { fetchPosts } from "@/api/posts";
import { fetchTags } from "@/api/tags";

const route = useRoute();
const router = useRouter();
const posts = ref<PostListItem[]>([]);
const loading = ref(true);
const error = ref("");
const currentPage = ref(1);
const totalPages = ref(0);
const size = 10;
const popularTags = ref<Tag[]>([]);

const { setMeta } = useSeo();

const featuredPosts = computed(() => posts.value.filter((p) => p.featured));
const regularPosts = computed(() => posts.value.filter((p) => !p.featured));

const paginationRange = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages: (number | string)[] = [1];
  if (current > 3) pages.push("...");
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  if (current < total - 2) pages.push("...");
  pages.push(total);
  return pages;
});

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

async function loadTags() {
  try {
    const tags = await fetchTags();
    popularTags.value = tags
      .sort((a, b) => (b.post_count || 0) - (a.post_count || 0))
      .slice(0, 10);
  } catch {}
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
  loadTags();
  setMeta({
    title: `${SITE_NAME} — ${SITE_DESCRIPTION}`,
    description: SITE_DESCRIPTION,
    url: window.location.origin,
    type: "website",
  });
});

watch(() => route.query.page, (p) => {
  const page = Number(p) || 1;
  currentPage.value = page;
  load(page);
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <section class="mb-12 text-center">
      <h1 class="text-3xl font-bold mb-3">{{ SITE_NAME }}</h1>
      <p class="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
        {{ SITE_DESCRIPTION }}
      </p>
    </section>

    <section v-if="popularTags.length > 0" class="mb-10">
      <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        <router-link
          v-for="tag in popularTags"
          :key="tag.id"
          :to="`/tag/${tag.slug}`"
          class="shrink-0 inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all"
        >
          {{ tag.name }}
          <span class="text-xs text-gray-400 dark:text-gray-500">{{ tag.post_count || 0 }}</span>
        </router-link>
      </div>
    </section>

    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load(currentPage)" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <div v-if="loading" class="space-y-6">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="h-5 bg-gray-200 dark:bg-gray-800 rounded w-3/4 mb-2"></div>
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-full"></div>
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/3 mt-2"></div>
      </div>
    </div>

    <template v-if="!loading && !error">
      <section v-if="featuredPosts.length > 0" class="mb-10">
        <h2 class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4">精选文章</h2>
        <div class="space-y-4">
          <router-link
            v-for="fp in featuredPosts"
            :key="fp.id"
            :to="`/post/${fp.slug}`"
            class="group block rounded-2xl border border-gray-100 dark:border-gray-800 overflow-hidden hover:border-primary-200 dark:hover:border-primary-800 transition-all"
          >
            <div v-if="fp.cover_image" class="aspect-[2/1] overflow-hidden">
              <img :src="fp.cover_image" :alt="fp.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" />
            </div>
            <div class="p-6">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 px-2 py-0.5 rounded-full font-medium">精选</span>
                <router-link
                  v-for="tag in fp.tags"
                  :key="tag.id"
                  :to="`/tag/${tag.slug}`"
                  class="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                >
                  {{ tag.name }}
                </router-link>
              </div>
              <h3 class="text-xl font-bold group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors mb-2">{{ fp.title }}</h3>
              <p v-if="fp.excerpt" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{{ fp.excerpt }}</p>
            </div>
          </router-link>
        </div>
      </section>

      <section v-if="regularPosts.length > 0" class="mb-8">
        <PostCard v-for="post in regularPosts" :key="post.id" :post="post" />
      </section>

      <div v-if="posts.length === 0" class="text-center py-16 text-gray-400">
        <p class="text-lg mb-2">暂无文章</p>
        <p class="text-sm">新文章正在路上...</p>
      </div>
    </template>

    <nav v-if="totalPages > 1" class="flex justify-center items-center gap-1.5 mt-8">
      <button
        :disabled="currentPage === 1"
        @click="gotoPage(currentPage - 1)"
        class="px-2.5 py-1.5 text-sm rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <template v-for="p in paginationRange" :key="p">
        <span v-if="p === '...'" class="px-2 py-1.5 text-sm text-gray-400">...</span>
        <button
          v-else
          @click="gotoPage(p as number)"
          :class="[
            'px-3 py-1.5 text-sm rounded-lg transition-colors',
            p === currentPage
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700',
          ]"
        >
          {{ p }}
        </button>
      </template>
      <button
        :disabled="currentPage === totalPages"
        @click="gotoPage(currentPage + 1)"
        class="px-2.5 py-1.5 text-sm rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
      </button>
    </nav>
  </div>
</template>
