<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { AnalyticsOverview } from "@/types";
import { adminFetchAnalyticsOverview, adminFetchPostStats } from "@/api/admin";

const overview = ref<AnalyticsOverview | null>(null);
const postStats = ref<{ title: string; slug: string; view_count: number }[]>([]);
const loading = ref(true);

onMounted(async () => {
  try {
    [overview.value, postStats.value] = await Promise.all([
      adminFetchAnalyticsOverview(),
      adminFetchPostStats(),
    ]);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div>
    <h1 class="text-xl font-bold mb-6">仪表板</h1>

    <div v-if="loading" class="animate-pulse space-y-4">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="h-24 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
      </div>
    </div>

    <template v-else-if="overview">
      <!-- Stats cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500">今日访问</p>
          <p class="text-2xl font-bold mt-1">{{ overview.today_page_views }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500">总访问量</p>
          <p class="text-2xl font-bold mt-1">{{ overview.total_page_views }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500">文章数</p>
          <p class="text-2xl font-bold mt-1">{{ overview.total_posts }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-500">评论数</p>
          <p class="text-2xl font-bold mt-1">{{ overview.total_comments }}</p>
        </div>
      </div>

      <!-- Popular posts -->
      <div class="mb-8">
        <h2 class="text-lg font-semibold mb-3">热门文章</h2>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <th class="text-left px-4 py-2 font-medium">文章</th>
                <th class="text-right px-4 py-2 font-medium">阅读量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="postStats.length === 0">
                <td colspan="2" class="text-center py-8 text-gray-400">暂无数据</td>
              </tr>
              <tr
                v-for="post in postStats"
                :key="post.slug"
                class="border-b border-gray-100 dark:border-gray-700 last:border-0"
              >
                <td class="px-4 py-2.5">
                  <a :href="`/post/${post.slug}`" target="_blank" class="hover:text-primary-600">{{ post.title }}</a>
                </td>
                <td class="px-4 py-2.5 text-right">{{ post.view_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent events -->
      <div>
        <h2 class="text-lg font-semibold mb-3">最近事件</h2>
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <th class="text-left px-4 py-2 font-medium">类型</th>
                <th class="text-left px-4 py-2 font-medium">页面</th>
                <th class="text-right px-4 py-2 font-medium">时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="overview.recent_events.length === 0">
                <td colspan="3" class="text-center py-8 text-gray-400">暂无事件</td>
              </tr>
              <tr
                v-for="ev in overview.recent_events"
                :key="ev.created_at"
                class="border-b border-gray-100 dark:border-gray-700 last:border-0"
              >
                <td class="px-4 py-2.5">
                  <span class="bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded text-xs">{{ ev.event_type }}</span>
                </td>
                <td class="px-4 py-2.5 text-gray-500 max-w-xs truncate">{{ ev.source_page }}</td>
                <td class="px-4 py-2.5 text-right text-gray-400 text-xs">{{ new Date(ev.created_at).toLocaleString("zh-CN") }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
