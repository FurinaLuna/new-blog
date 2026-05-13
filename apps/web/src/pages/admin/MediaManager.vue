<script setup lang="ts">
import { ref, onMounted } from "vue";
import { adminFetchMedia, adminUploadMedia, adminDeleteMedia } from "@/api/admin";

interface MediaItem {
  id: string;
  filename: string;
  url: string;
  mime_type: string;
  size: number;
  created_at: string;
}

const items = ref<MediaItem[]>([]);
const loading = ref(true);
const uploading = ref(false);

async function load() {
  loading.value = true;
  try {
    const res = await adminFetchMedia(1, 100);
    items.value = res.items;
  } finally {
    loading.value = false;
  }
}

async function onUpload(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  uploading.value = true;
  try {
    await adminUploadMedia(file);
    await load();
  } finally {
    uploading.value = false;
  }
}

async function onDelete(id: string) {
  if (!confirm("确定删除？")) return;
  await adminDeleteMedia(id);
  await load();
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function copyUrl(url: string) {
  navigator.clipboard.writeText(url).then(() => alert("已复制URL"));
}

onMounted(load);
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold">媒体管理</h1>
      <label class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors cursor-pointer">
        {{ uploading ? "上传中..." : "上传文件" }}
        <input type="file" accept="image/*" @change="onUpload" class="hidden" :disabled="uploading" />
      </label>
    </div>

    <div v-if="loading" class="animate-pulse grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="aspect-square bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
    </div>

    <div v-else-if="items.length === 0" class="text-center py-16 text-gray-400">
      <p class="mb-2">暂无上传的文件</p>
      <p class="text-sm">点击上方按钮上传图片</p>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="group border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white dark:bg-gray-800"
      >
        <div class="aspect-square bg-gray-100 dark:bg-gray-900 flex items-center justify-center overflow-hidden">
          <img
            v-if="item.mime_type.startsWith('image/')"
            :src="item.url"
            :alt="item.filename"
            class="w-full h-full object-cover"
          />
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
        </div>
        <div class="p-2">
          <p class="text-xs truncate mb-1" :title="item.filename">{{ item.filename }}</p>
          <p class="text-xs text-gray-400 mb-2">{{ formatSize(item.size) }}</p>
          <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click="copyUrl(item.url)" class="text-xs text-primary-600 hover:underline">复制URL</button>
            <button @click="onDelete(item.id)" class="text-xs text-red-500 hover:underline">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
