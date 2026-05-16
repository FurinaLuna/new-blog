<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { Comment, PaginatedResponse } from "@/types";
import { adminFetchComments, adminApproveComment, adminDeleteComment, adminBatchApproveComments, adminBatchDeleteComments, adminReplyComment } from "@/api/admin";
import { useToast } from "@/composables/useToast";
import { useConfirm } from "@/composables/useConfirm";
import { useFormatDate } from "@/composables/useFormatDate";

const toast = useToast();
const { confirm } = useConfirm();
const { formatDate } = useFormatDate();
const comments = ref<Comment[]>([]);
const loading = ref(true);
const error = ref("");
const approving = ref<string[]>([]);
const deleting = ref<string[]>([]);
const selectedIds = ref<string[]>([]);
const statusFilter = ref<"pending" | "approved" | "all">("pending");
const page = ref(1);
const totalPages = ref(0);
const total = ref(0);
const replyingId = ref<string | null>(null);
const replyContent = ref("");
const submittingReply = ref(false);

const pendingCount = computed(() => comments.value.filter((c) => c.status === "pending" || !c.status).length);
const approvedCount = computed(() => comments.value.filter((c) => c.status === "approved").length);
const allCount = computed(() => comments.value.length);

const allSelected = computed(() => comments.value.length > 0 && selectedIds.value.length === comments.value.length);
const someSelected = computed(() => selectedIds.value.length > 0 && !allSelected.value);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const statusParam = statusFilter.value === "all" ? undefined : statusFilter.value;
    const res: PaginatedResponse<Comment> = await adminFetchComments(statusParam, page.value);
    comments.value = res.items;
    total.value = res.total;
    totalPages.value = res.pages;
    selectedIds.value = [];
  } catch {
    error.value = "加载评论列表失败";
  } finally {
    loading.value = false;
  }
}

function toggleSelect(id: string) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((i) => i !== id);
  } else {
    selectedIds.value.push(id);
  }
}

function toggleAll() {
  if (allSelected.value) {
    selectedIds.value = [];
  } else {
    selectedIds.value = comments.value.map((c) => c.id);
  }
}

async function onApprove(id: string) {
  approving.value.push(id);
  try {
    await adminApproveComment(id);
    toast.success("评论已通过审核");
    await load();
  } catch {
    toast.error("操作失败");
  } finally {
    approving.value = approving.value.filter((i) => i !== id);
  }
}

async function onDelete(id: string) {
  const ok = await confirm("确定删除这条评论吗？");
  if (!ok) return;
  deleting.value.push(id);
  try {
    await adminDeleteComment(id);
    toast.success("评论已删除");
    await load();
  } catch {
    toast.error("删除失败");
  } finally {
    deleting.value = deleting.value.filter((i) => i !== id);
  }
}

async function onBatchApprove() {
  if (selectedIds.value.length === 0) return;
  const ok = await confirm(`确定通过审核选中的 ${selectedIds.value.length} 条评论吗？`);
  if (!ok) return;
  try {
    await adminBatchApproveComments({ ids: selectedIds.value });
    toast.success("批量审核成功");
    await load();
  } catch {
    toast.error("批量审核失败");
  }
}

async function onBatchDelete() {
  if (selectedIds.value.length === 0) return;
  const ok = await confirm(`确定删除选中的 ${selectedIds.value.length} 条评论吗？此操作不可撤销。`);
  if (!ok) return;
  try {
    await adminBatchDeleteComments({ ids: selectedIds.value });
    toast.success("批量删除成功");
    await load();
  } catch {
    toast.error("批量删除失败");
  }
}

function startReply(id: string) {
  replyingId.value = id;
  replyContent.value = "";
}

function cancelReply() {
  replyingId.value = null;
  replyContent.value = "";
}

async function submitReply(commentId: string) {
  if (!replyContent.value.trim()) return;
  submittingReply.value = true;
  try {
    await adminReplyComment(commentId, replyContent.value.trim());
    toast.success("回复成功");
    cancelReply();
    await load();
  } catch {
    toast.error("回复失败");
  } finally {
    submittingReply.value = false;
  }
}

function getPostTitle(comment: Comment) {
  return comment.post_title || "未知文章";
}

function changePage(newPage: number) {
  page.value = newPage;
  load();
}

onMounted(load);
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold">评论管理</h1>
      <div v-if="someSelected || allSelected" class="flex gap-2">
        <button @click="onBatchApprove" class="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          批量通过 ({{ selectedIds.length }})
        </button>
        <button @click="onBatchDelete" class="px-3 py-1.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
          批量删除 ({{ selectedIds.length }})
        </button>
      </div>
    </div>

    <div class="mb-4 flex gap-1 border-b border-gray-200 dark:border-gray-700">
      <button
        @click="statusFilter = 'pending'; page = 1; load()"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', statusFilter === 'pending' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >待审核 ({{ pendingCount }})</button>
      <button
        @click="statusFilter = 'approved'; page = 1; load()"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', statusFilter === 'approved' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >已审核 ({{ approvedCount }})</button>
      <button
        @click="statusFilter = 'all'; page = 1; load()"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', statusFilter === 'all' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >全部 ({{ allCount }})</button>
    </div>

    <div v-if="loading" class="animate-pulse space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
    </div>

    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load()" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <div v-else-if="comments.length === 0" class="text-center py-16 text-gray-400">
      <p>暂无评论</p>
    </div>

    <div v-else-if="!loading && !error" class="space-y-4">
      <div class="flex items-center gap-3 px-4 py-2 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <input
          type="checkbox"
          :checked="allSelected"
          :indeterminate="someSelected"
          @change="toggleAll"
          class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        <span class="text-xs text-gray-500">全选</span>
      </div>

      <div
        v-for="c in comments"
        :key="c.id"
        :class="[
          'border rounded-lg p-4 transition-colors',
          selectedIds.includes(c.id)
            ? 'border-primary-400 dark:border-primary-600 bg-primary-50 dark:bg-primary-900/10'
            : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
        ]"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <input
              type="checkbox"
              :checked="selectedIds.includes(c.id)"
              @change="toggleSelect(c.id)"
              class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="font-medium text-sm">{{ c.author }}</span>
            <span class="text-xs text-gray-400">{{ formatDate(c.created_at) }}</span>
            <span class="text-xs text-gray-400">- {{ getPostTitle(c) }}</span>
          </div>
          <div class="flex gap-2">
            <button v-if="statusFilter !== 'approved'" @click="onApprove(c.id)" :disabled="approving.includes(c.id)" class="text-sm text-green-600 hover:underline disabled:opacity-30 focus:outline-none focus:ring-2 focus:ring-green-400 rounded px-1">通过</button>
            <button @click="startReply(c.id)" class="text-sm text-primary-600 hover:underline focus:outline-none focus:ring-2 focus:ring-primary-400 rounded px-1">回复</button>
            <button @click="onDelete(c.id)" :disabled="deleting.includes(c.id)" class="text-sm text-red-500 hover:underline disabled:opacity-30 focus:outline-none focus:ring-2 focus:ring-red-400 rounded px-1">删除</button>
          </div>
        </div>
        <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ c.content }}</p>

        <div v-if="replyingId === c.id" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <textarea
            v-model="replyContent"
            rows="3"
            placeholder="输入回复内容..."
            class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400 resize-none"
          ></textarea>
          <div class="flex gap-2 mt-2">
            <button
              @click="submitReply(c.id)"
              :disabled="submittingReply || !replyContent.trim()"
              class="px-3 py-1.5 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >{{ submittingReply ? '提交中...' : '提交回复' }}</button>
            <button @click="cancelReply" class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors">取消</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="flex flex-col items-center gap-3 mt-6">
      <p class="text-xs text-gray-400">共 {{ total }} 条，第 {{ page }} / {{ totalPages }} 页</p>
      <div class="flex justify-center gap-1">
        <button
          :disabled="page <= 1"
          @click="changePage(page - 1)"
          class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary-400"
        >上一页</button>
        <button
          v-for="p in totalPages"
          :key="p"
          @click="changePage(p)"
          :class="[
            'px-3 py-1.5 text-sm rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-400',
            p === page ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700',
          ]"
        >{{ p }}</button>
        <button
          :disabled="page >= totalPages"
          @click="changePage(page + 1)"
          class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary-400"
        >下一页</button>
      </div>
    </div>
  </div>
</template>
