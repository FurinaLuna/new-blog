<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Comment } from "@/types";
import { adminFetchPendingComments, adminApproveComment, adminDeleteComment } from "@/api/admin";
import { useToast } from "@/composables/useToast";
import { useConfirm } from "@/composables/useConfirm";

const toast = useToast();
const { confirm } = useConfirm();
const comments = ref<Comment[]>([]);
const loading = ref(true);
const error = ref("");
const approving = ref<Set<string>>(new Set());
const deleting = ref<Set<string>>(new Set());

async function load() {
  loading.value = true;
  error.value = "";
  try {
    comments.value = await adminFetchPendingComments();
  } catch {
    error.value = "加载评论列表失败";
  } finally {
    loading.value = false;
  }
}

async function onApprove(id: string) {
  approving.value.add(id);
  try {
    await adminApproveComment(id);
    toast.success("评论已通过审核");
    await load();
  } catch {
    toast.error("操作失败");
  } finally {
    approving.value.delete(id);
  }
}

async function onDelete(id: string) {
  const ok = await confirm("确定删除这条评论吗？");
  if (!ok) return;
  deleting.value.add(id);
  try {
    await adminDeleteComment(id);
    toast.success("评论已删除");
    await load();
  } catch {
    toast.error("删除失败");
  } finally {
    deleting.value.delete(id);
  }
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

    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load()" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <div v-else-if="comments.length === 0" class="text-center py-16 text-gray-400">
      <p>暂无待审核评论</p>
    </div>

    <div v-else-if="!loading && !error" class="space-y-4">
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
            <button @click="onApprove(c.id)" :disabled="approving.has(c.id)" class="text-sm text-green-600 hover:underline disabled:opacity-30 focus:outline-none focus:ring-2 focus:ring-green-400 rounded px-1">通过</button>
            <button @click="onDelete(c.id)" :disabled="deleting.has(c.id)" class="text-sm text-red-500 hover:underline disabled:opacity-30 focus:outline-none focus:ring-2 focus:ring-red-400 rounded px-1">删除</button>
          </div>
        </div>
        <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ c.content }}</p>
      </div>
    </div>
  </div>
</template>
