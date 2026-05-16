<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { AnalyticsOverview, AnalyticsTrend, Comment } from "@/types";
import {
  adminFetchAnalyticsOverview,
  adminFetchPostStats,
  adminFetchAnalyticsTrend,
  adminFetchRealtimeStats,
  adminFetchPendingComments,
  adminApproveComment,
} from "@/api/admin";
import { useFormatDate } from "@/composables/useFormatDate";
import StatCard from "@/components/ui/StatCard.vue";
import TrendChart from "@/components/ui/TrendChart.vue";

const overview = ref<AnalyticsOverview | null>(null);
const postStats = ref<{ title: string; slug: string; view_count: number }[]>([]);
const trendData = ref<AnalyticsTrend | null>(null);
const pendingComments = ref<Comment[]>([]);
const realtimeStats = ref<{ online_users: number; active_sessions: number } | null>(null);

const loading = ref(true);
const error = ref("");
const trendDays = ref(7);
const trendLoading = ref(false);

const { formatDate } = useFormatDate();

const trendLabels = computed(() => trendData.value?.labels ?? []);
const trendDatasets = computed(() => {
  if (!trendData.value) return [];
  const colors = ["#1a6ffa", "#10b981"];
  return trendData.value.datasets.map((ds, i) => ({
    ...ds,
    color: colors[i % colors.length],
  }));
});

const popularPosts = computed(() => {
  if (!overview.value?.popular_posts?.length) return [];
  return overview.value.popular_posts.slice(0, 5);
});

const topTags = computed(() => {
  if (!overview.value?.top_tags?.length) return [];
  return overview.value.top_tags;
});

const pendingList = computed(() => pendingComments.value.slice(0, 3));

const tagColors = [
  "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300",
  "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300",
  "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300",
  "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
];

async function loadOverview() {
  const [ov, ps] = await Promise.all([
    adminFetchAnalyticsOverview(),
    adminFetchPostStats(),
  ]);
  overview.value = ov;
  postStats.value = ps;
}

async function loadTrend() {
  trendLoading.value = true;
  try {
    trendData.value = await adminFetchAnalyticsTrend("pv", trendDays.value);
  } finally {
    trendLoading.value = false;
  }
}

async function loadPendingComments() {
  try {
    pendingComments.value = await adminFetchPendingComments(1);
  } catch {
    pendingComments.value = [];
  }
}

async function loadRealtime() {
  try {
    realtimeStats.value = await adminFetchRealtimeStats();
  } catch {
    realtimeStats.value = null;
  }
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    await Promise.all([loadOverview(), loadTrend(), loadPendingComments(), loadRealtime()]);
  } catch {
    error.value = "加载仪表板数据失败";
  } finally {
    loading.value = false;
  }
}

async function switchTrend(days: number) {
  trendDays.value = days;
  await loadTrend();
}

async function approveComment(id: string) {
  await adminApproveComment(id);
  pendingComments.value = pendingComments.value.filter((c) => c.id !== id);
  if (overview.value) {
    overview.value.total_comments += 1;
  }
}

onMounted(load);
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">欢迎回来!</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          <span v-if="realtimeStats">
            当前在线 {{ realtimeStats.online_users }} 人 · 活跃会话 {{ realtimeStats.active_sessions }}
          </span>
          <span v-else>这里是你的博客数据概览</span>
        </p>
      </div>
      <button
        @click="load()"
        :disabled="loading"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
      >
        <svg
          class="w-4 h-4"
          :class="{ 'animate-spin': loading }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        刷新
      </button>
    </div>

    <div v-if="error" class="text-center py-12 text-red-500 bg-red-50 dark:bg-red-900/20 rounded-xl mb-6">
      <p class="text-base">{{ error }}</p>
      <button
        @click="load()"
        class="mt-3 text-sm text-red-600 dark:text-red-400 hover:underline font-medium"
      >
        重试
      </button>
    </div>

    <div v-if="loading" class="animate-pulse space-y-6">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="h-24 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
      </div>
      <div class="h-80 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 h-64 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
        <div class="h-64 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
      </div>
    </div>

    <template v-if="!loading && !error && overview">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="今日 PV"
          :value="overview.today_page_views"
          icon="eye"
          :trend="overview.pv_trend"
          trend-label="vs 昨日"
        />
        <StatCard
          title="今日 UV"
          :value="overview.today_unique_visitors"
          icon="eye"
          :trend="overview.uv_trend"
          trend-label="vs 昨日"
        />
        <StatCard
          title="文章总数"
          :value="overview.total_posts"
          icon="file-text"
          :trend="overview.posts_trend"
          trend-label="vs 昨日"
        />
        <StatCard
          title="评论总数"
          :value="overview.total_comments"
          icon="message-circle"
          :trend="overview.comments_trend"
          trend-label="vs 昨日"
        />
      </div>

      <div class="mb-6">
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">访问趋势</h3>
            <div class="flex gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-0.5">
              <button
                @click="switchTrend(7)"
                :class="[
                  'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                  trendDays === 7
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300',
                ]"
              >
                7天
              </button>
              <button
                @click="switchTrend(30)"
                :class="[
                  'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                  trendDays === 30
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300',
                ]"
              >
                30天
              </button>
            </div>
          </div>
          <div v-if="trendLoading" class="animate-pulse h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
          <div v-else-if="trendData" class="relative" style="height: 280px">
            <TrendChart
              :labels="trendLabels"
              :datasets="trendDatasets"
            />
          </div>
          <div v-else class="flex items-center justify-center h-64 text-gray-400 dark:text-gray-500 text-sm">
            暂无趋势数据
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
            <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">热门文章 Top5</h3>
            </div>
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
                  <th class="text-left px-5 py-2.5 font-medium text-gray-500 dark:text-gray-400">文章</th>
                  <th class="text-right px-5 py-2.5 font-medium text-gray-500 dark:text-gray-400">阅读量</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="popularPosts.length === 0">
                  <td colspan="2" class="text-center py-8 text-gray-400 dark:text-gray-500">暂无数据</td>
                </tr>
                <tr
                  v-for="post in popularPosts"
                  :key="post.slug"
                  class="border-b border-gray-100 dark:border-gray-700/50 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                >
                  <td class="px-5 py-3">
                    <a
                      :href="`/post/${post.slug}`"
                      target="_blank"
                      class="text-gray-900 dark:text-gray-100 hover:text-primary-600 dark:hover:text-primary-400 font-medium"
                    >
                      {{ (post as any).title || post.slug }}
                    </a>
                  </td>
                  <td class="px-5 py-3 text-right text-gray-500 dark:text-gray-400">
                    {{ post.views.toLocaleString() }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
            <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">热门标签</h3>
            <div v-if="topTags.length === 0" class="text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
              暂无标签
            </div>
            <div v-else class="flex flex-wrap gap-2">
              <router-link
                v-for="(tag, index) in topTags"
                :key="tag.slug"
                :to="`/admin/tags`"
                :class="[
                  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors hover:opacity-80',
                  tagColors[index % tagColors.length],
                ]"
              >
                {{ tag.name }}
                <span class="opacity-70 text-xs">{{ tag.post_count }}</span>
              </router-link>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
            <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">快捷操作</h3>
            <div class="grid grid-cols-2 gap-3">
              <router-link
                to="/admin/posts/new"
                class="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors group"
              >
                <svg class="w-6 h-6 text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">新建文章</span>
              </router-link>
              <router-link
                to="/admin/tags"
                class="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors group"
              >
                <svg class="w-6 h-6 text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">管理标签</span>
              </router-link>
              <router-link
                to="/admin/media"
                class="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors group"
              >
                <svg class="w-6 h-6 text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">媒体管理</span>
              </router-link>
              <router-link
                to="/admin/comments"
                class="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors group"
              >
                <svg class="w-6 h-6 text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span class="text-xs font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">评论管理</span>
              </router-link>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">待审核评论</h3>
              <router-link
                v-if="pendingComments.length > 0"
                to="/admin/comments"
                class="text-xs text-primary-600 dark:text-primary-400 hover:underline"
              >
                查看全部
              </router-link>
            </div>
            <div v-if="pendingList.length === 0" class="text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
              暂无待审核评论
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="comment in pendingList"
                :key="comment.id"
                class="p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ comment.author }}</span>
                  <span class="text-xs text-gray-400 dark:text-gray-500">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">{{ comment.content }}</p>
                <button
                  @click="approveComment(comment.id)"
                  class="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300"
                >
                  通过审核
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
