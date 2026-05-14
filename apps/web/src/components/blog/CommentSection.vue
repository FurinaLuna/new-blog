<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Comment } from "@/types";
import { fetchComments, submitComment } from "@/api/comments";

const props = defineProps<{ postId: string }>();

const comments = ref<Comment[]>([]);
const loading = ref(true);
const loadError = ref("");
const submitting = ref(false);
const author = ref("");
const email = ref("");
const content = ref("");
const message = ref("");

onMounted(async () => {
  try {
    comments.value = await fetchComments(props.postId);
  } catch {
    loadError.value = "评论加载失败";
  } finally {
    loading.value = false;
  }
});

async function onSubmit() {
  if (!author.value.trim() || !content.value.trim()) return;
  submitting.value = true;
  message.value = "";
  try {
    await submitComment({
      post_id: props.postId,
      author: author.value.trim(),
      email: email.value.trim() || undefined,
      content: content.value.trim(),
    });
    message.value = "评论已提交，审核通过后显示。";
    author.value = "";
    email.value = "";
    content.value = "";
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } };
    message.value = err?.response?.data?.detail || "评论失败，请稍后再试。";
  } finally {
    submitting.value = false;
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<template>
  <section class="mt-10 pt-8 border-t border-gray-200 dark:border-gray-800">
    <h3 class="text-lg font-semibold mb-4">评论 ({{ comments.length }})</h3>

    <!-- Existing comments -->
    <div v-if="loading" class="text-sm text-gray-400">加载中...</div>
    <div v-else-if="loadError" class="text-sm text-red-500">{{ loadError }}</div>
    <div v-else-if="comments.length === 0" class="text-sm text-gray-400">暂无评论，来抢沙发吧。</div>
    <div v-else class="space-y-4 mb-8">
      <div v-for="c in comments" :key="c.id" class="border-b border-gray-100 dark:border-gray-800 pb-4">
        <div class="flex items-center gap-2 mb-1">
          <span class="font-medium text-sm">{{ c.author }}</span>
          <span class="text-xs text-gray-400">{{ formatDate(c.created_at) }}</span>
        </div>
        <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ c.content }}</p>
      </div>
    </div>

    <!-- Comment form -->
    <h4 class="text-md font-semibold mb-3">发表评论</h4>
    <form @submit.prevent="onSubmit" class="space-y-3 max-w-lg">
      <div class="flex gap-3">
        <label class="flex-1">
          <span class="sr-only">昵称</span>
          <input
            v-model="author"
            type="text"
            required
            placeholder="昵称"
            autocomplete="nickname"
            class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
          />
        </label>
        <label class="flex-1">
          <span class="sr-only">邮箱</span>
          <input
            v-model="email"
            type="email"
            placeholder="邮箱（选填）"
            autocomplete="email"
            class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
          />
        </label>
      </div>
      <label>
        <span class="sr-only">评论内容</span>
        <textarea
          v-model="content"
          required
          rows="4"
          placeholder="写下你的想法..."
          class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400 resize-y"
        ></textarea>
      </label>
      <div class="flex items-center gap-3">
        <button
          type="submit"
          :disabled="submitting"
          class="px-5 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {{ submitting ? "提交中..." : "提交评论" }}
        </button>
        <p v-if="message" class="text-sm text-gray-500">{{ message }}</p>
      </div>
    </form>
  </section>
</template>
