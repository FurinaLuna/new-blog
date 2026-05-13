<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import type { PostListItem, PaginatedResponse } from "@/types";
import { adminFetchPosts, adminDeletePost } from "@/api/admin";

const router = useRouter();
const posts = ref<PostListItem[]>([]);
const loading = ref(true);
const page = ref(1);
const totalPages = ref(0);
const search = ref("");

async function load() {
  loading.value = true;
  try {
    const res: PaginatedResponse<PostListItem> = await adminFetchPosts(page.value, 20, search.value || undefined);
    posts.value = res.items;
    totalPages.value = res.pages;
  } finally {
    loading.value = false;
  }
}

async function onDelete(id: string, title: string) {
  if (!confirm(`确定删除「${title}」吗？`)) return;
  await adminDeletePost(id);
  await load();
}

function onCreate() {
  router.push("/admin/posts/new");
}

function onEdit(slug: string) {
  router.push(`/admin/posts/${slug}/edit`);
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

    <div class="mb-4 flex gap-2">
      <input
        v-model="search"
        type="search"
        placeholder="搜索文章..."
        class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 w-64"
        @keyup.enter="load"
      />
      <button @click="load" class="px-4 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700">
        搜索
      </button>
    </div>

    <div v-if="loading" class="animate-pulse space-y-2">
      <div v-for="i in 5" :key="i" class="h-10 bg-gray-200 dark:bg-gray-800 rounded"></div>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
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
            class="border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-750"
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

    <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
      <button
        v-for="p in totalPages"
        :key="p"
        @click="page = p; load()"
        :class="[
          'px-3 py-1.5 text-sm rounded-lg transition-colors',
          p === page ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700',
        ]"
      >
        {{ p }}
      </button>
    </div>
  </div>
</template>
