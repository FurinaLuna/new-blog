<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import type { PostListItem, PaginatedResponse } from "@/types";
import { adminFetchPosts, adminDeletePost } from "@/api/admin";
import { useToast } from "@/composables/useToast";
import { useConfirm } from "@/composables/useConfirm";

const router = useRouter();
const toast = useToast();
const { confirm } = useConfirm();
const posts = ref<PostListItem[]>([]);
const loading = ref(true);
const error = ref("");
const page = ref(1);
const totalPages = ref(0);
const total = ref(0);
const search = ref("");

const visiblePages = computed(() => {
  const pages: (number | string)[] = [];
  const tp = totalPages.value;
  if (tp <= 7) return Array.from({ length: tp }, (_, i) => i + 1);
  pages.push(1);
  if (page.value > 3) pages.push("...");
  const start = Math.max(2, page.value - 1);
  const end = Math.min(tp - 1, page.value + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  if (page.value < tp - 2) pages.push("...");
  pages.push(tp);
  return pages;
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res: PaginatedResponse<PostListItem> = await adminFetchPosts(page.value, 20, search.value || undefined);
    posts.value = res.items;
    total.value = res.total;
    totalPages.value = res.pages;
  } catch {
    error.value = "加载文章列表失败";
  } finally {
    loading.value = false;
  }
}

async function onDelete(id: string, title: string) {
  const ok = await confirm(`确定删除「${title}」吗？`);
  if (!ok) return;
  try {
    await adminDeletePost(id);
    toast.success("文章已删除");
    await load();
  } catch {
    toast.error("删除失败");
  }
}

function onCreate() {
  router.push("/admin/posts/new");
}

function onEdit(slug: string) {
  router.push(`/admin/posts/${slug}/edit`);
}

function onSearch() {
  page.value = 1;
  load();
}

function onClearSearch() {
  search.value = "";
  page.value = 1;
  load();
}

onMounted(load);
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold">文章管理</h1>
      <button @click="onCreate" class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
        新建文章
      </button>
    </div>

    <div class="mb-4 flex gap-2 flex-wrap">
      <label class="sr-only" for="post-search">搜索文章</label>
      <input
        id="post-search"
        v-model="search"
        type="search"
        placeholder="搜索文章..."
        class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 w-64 max-w-full focus:outline-none focus:ring-2 focus:ring-primary-400"
        @keyup.enter="onSearch"
      />
      <button @click="onSearch" class="px-4 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-400">搜索</button>
      <button v-if="search" @click="onClearSearch" class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none">清除</button>
    </div>
    <p v-if="search && !loading" class="text-xs text-gray-400 mb-3">搜索 "{{ search }}" 找到 {{ total }} 篇文章</p>

    <div v-if="loading" class="animate-pulse space-y-2">
      <div v-for="i in 5" :key="i" class="h-10 bg-gray-200 dark:bg-gray-800 rounded"></div>
    </div>

    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load()" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <div v-else-if="!loading && !error" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
            <th class="text-left px-4 py-2.5 font-medium">标题</th>
            <th class="text-left px-4 py-2.5 font-medium hidden sm:table-cell">状态</th>
            <th class="text-left px-4 py-2.5 font-medium hidden md:table-cell">日期</th>
            <th class="text-right px-4 py-2.5 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="posts.length === 0">
            <td colspan="4" class="text-center py-12 text-gray-400">暂无文章</td>
          </tr>
          <tr
            v-for="post in posts"
            :key="post.id"
            class="border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <td class="px-4 py-2.5">
              <p class="font-medium truncate max-w-xs">{{ post.title }}</p>
              <p class="text-xs text-gray-400">{{ post.slug }}</p>
            </td>
            <td class="px-4 py-2.5 hidden sm:table-cell">
              <span :class="['text-xs px-2 py-0.5 rounded-full', post.published ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300']">
                {{ post.published ? '已发布' : '草稿' }}
              </span>
            </td>
            <td class="px-4 py-2.5 text-gray-400 hidden md:table-cell">{{ new Date(post.created_at).toLocaleDateString("zh-CN") }}</td>
            <td class="px-4 py-2.5 text-right">
              <div class="flex gap-2 justify-end">
                <button @click="onEdit(post.slug)" class="text-sm text-primary-600 hover:underline">编辑</button>
                <button @click="onDelete(post.id, post.title)" class="text-sm text-red-500 hover:underline">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="flex flex-col items-center gap-3 mt-6">
      <p class="text-xs text-gray-400">共 {{ total }} 篇，第 {{ page }} / {{ totalPages }} 页</p>
      <div class="flex justify-center gap-1">
        <button
          :disabled="page <= 1"
          @click="page--; load()"
          class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary-400"
        >上一页</button>
        <template v-for="p in visiblePages" :key="p">
          <span v-if="p === '...'" class="px-2 py-1.5 text-sm text-gray-400">...</span>
          <button
            v-else
            @click="page = p as number; load()"
            :class="[
              'px-3 py-1.5 text-sm rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-400',
              p === page ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700',
            ]"
          >{{ p }}</button>
        </template>
        <button
          :disabled="page >= totalPages"
          @click="page++; load()"
          class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary-400"
        >下一页</button>
      </div>
    </div>
  </div>
</template>
