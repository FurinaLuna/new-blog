<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Comment } from "@/types";
import { adminFetchPendingComments, adminApproveComment, adminDeleteComment } from "@/api/admin";

const comments = ref<Comment[]>([]);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    comments.value = await adminFetchPendingComments();
  } finally {
    loading.value = false;
  }
}

async function onApprove(id: string) {
  await adminApproveComment(id);
  await load();
}

async function onDelete(id: string) {
  if (!confirm("确定删除？")) return;
  await adminDeleteComment(id);
  await load();
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString("zh-CN");
}

onMounted(load);
</script>

<template>
  <div>
    <h1 class="text-xl font-bold mb-6">评论管理 (待审核)</h1>

    <div v-if="loading" class="animate-pulse space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
    </div>

    <div v-else-if="comments.length === 0" class="text-center py-16 text-gray-400">
      <p>暂无待审核评论</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="c in comments"
        :key="c.id"
        class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="font-medium text-sm">{{ c.author }}</span>
            <span class="text-xs text-gray-400">{{ formatDate(c.created_at) }}</span>
          </div>
          <div class="flex gap-2">
            <button @click="onApprove(c.id)" class="text-sm text-green-600 hover:underline">通过</button>
            <button @click="onDelete(c.id)" class="text-sm text-red-500 hover:underline">删除</button>
          </div>
        </div>
        <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ c.content }}</p>
      </div>
    </div>
  </div>
</template>
