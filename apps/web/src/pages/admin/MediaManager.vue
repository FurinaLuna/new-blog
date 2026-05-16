<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import type { MediaItem } from "@/types";
import { adminFetchMedia, adminUploadMedia, adminDeleteMedia } from "@/api/admin";
import { useToast } from "@/composables/useToast";
import { useConfirm } from "@/composables/useConfirm";

const toast = useToast();
const { confirm } = useConfirm();
const items = ref<MediaItem[]>([]);
const loading = ref(true);
const error = ref("");
const uploading = ref(false);
const page = ref(1);
const totalPages = ref(0);
const typeFilter = ref<"all" | "image" | "document" | "other">("all");
const previewItem = ref<MediaItem | null>(null);
const dragOver = ref(false);
const uploadProgress = ref<{ name: string; progress: number }[]>([]);

const filteredItems = computed(() => {
  if (typeFilter.value === "image") return items.value.filter((i) => i.mime_type.startsWith("image/"));
  if (typeFilter.value === "document") return items.value.filter((i) => i.mime_type.startsWith("application/"));
  if (typeFilter.value === "other") return items.value.filter((i) => !i.mime_type.startsWith("image/") && !i.mime_type.startsWith("application/"));
  return items.value;
});

const imageCount = computed(() => items.value.filter((i) => i.mime_type.startsWith("image/")).length);
const documentCount = computed(() => items.value.filter((i) => i.mime_type.startsWith("application/")).length);
const otherCount = computed(() => items.value.filter((i) => !i.mime_type.startsWith("image/") && !i.mime_type.startsWith("application/")).length);

async function load(p = page.value) {
  loading.value = true;
  error.value = "";
  try {
    const res = await adminFetchMedia(p, 20);
    items.value = res.items;
    totalPages.value = res.pages;
    page.value = p;
  } catch {
    error.value = "加载媒体列表失败";
  } finally {
    loading.value = false;
  }
}

async function uploadFile(file: File) {
  uploading.value = true;
  const entry = { name: file.name, progress: 0 };
  uploadProgress.value.push(entry);
  try {
    await adminUploadMedia(file);
    entry.progress = 100;
    toast.success(`${file.name} 上传成功`);
    await load();
  } catch {
    toast.error(`${file.name} 上传失败`);
  } finally {
    uploading.value = false;
    setTimeout(() => {
      uploadProgress.value = uploadProgress.value.filter((p) => p.name !== entry.name);
    }, 1000);
  }
}

async function onUpload(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  await uploadFile(file);
  target.value = "";
}

async function onDrop(e: DragEvent) {
  e.preventDefault();
  dragOver.value = false;
  const files = e.dataTransfer?.files;
  if (!files || files.length === 0) return;
  for (const file of Array.from(files)) {
    await uploadFile(file);
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault();
  dragOver.value = true;
}

function onDragLeave() {
  dragOver.value = false;
}

async function onDelete(id: string) {
  const ok = await confirm("确定删除这个文件吗？");
  if (!ok) return;
  try {
    await adminDeleteMedia(id);
    toast.success("已删除");
    await load();
  } catch {
    toast.error("删除失败");
  }
}

function openPreview(item: MediaItem) {
  previewItem.value = item;
}

function closePreview() {
  previewItem.value = null;
}

function onPreviewOverlayClick(e: MouseEvent) {
  if (e.target === e.currentTarget) closePreview();
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function copyUrl(url: string) {
  navigator.clipboard.writeText(url).then(() => toast.success("已复制URL"));
}

onMounted(() => load());
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold">媒体管理</h1>
      <label :class="['px-4 py-2 text-sm rounded-lg transition-colors focus-within:ring-2 focus-within:ring-primary-400', uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-primary-600 text-white hover:bg-primary-700 cursor-pointer']">
        {{ uploading ? "上传中..." : "上传文件" }}
        <input type="file" accept="image/*" @change="onUpload" class="hidden" :disabled="uploading" multiple />
      </label>
    </div>

    <div
      :class="[
        'mb-6 border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
        dragOver
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500',
      ]"
      @drop="onDrop"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
      <p class="text-sm text-gray-500 dark:text-gray-400">拖拽文件到此处上传，或点击上方按钮选择文件</p>
      <p class="text-xs text-gray-400 mt-1">支持多文件同时上传</p>
    </div>

    <div v-if="uploadProgress.length > 0" class="mb-4 space-y-2">
      <div v-for="p in uploadProgress" :key="p.name" class="flex items-center gap-3 px-4 py-2 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <span class="text-sm truncate flex-1">{{ p.name }}</span>
        <div class="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div class="h-full bg-primary-600 rounded-full transition-all" :style="{ width: p.progress + '%' }"></div>
        </div>
        <span class="text-xs text-gray-400">{{ p.progress }}%</span>
      </div>
    </div>

    <div class="mb-4 flex gap-1 border-b border-gray-200 dark:border-gray-700">
      <button
        @click="typeFilter = 'all'"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', typeFilter === 'all' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >全部 ({{ items.length }})</button>
      <button
        @click="typeFilter = 'image'"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', typeFilter === 'image' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >图片 ({{ imageCount }})</button>
      <button
        @click="typeFilter = 'document'"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', typeFilter === 'document' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >文档 ({{ documentCount }})</button>
      <button
        @click="typeFilter = 'other'"
        :class="['px-4 py-2 text-sm border-b-2 transition-colors', typeFilter === 'other' ? 'border-primary-600 text-primary-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300']"
      >其他 ({{ otherCount }})</button>
    </div>

    <div v-if="loading" class="animate-pulse grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="aspect-square bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
    </div>

    <div v-if="error" class="text-center py-16 text-red-500">
      <p>{{ error }}</p>
      <button @click="load()" class="mt-4 text-sm text-primary-600 hover:underline">重试</button>
    </div>

    <div v-else-if="filteredItems.length === 0 && !loading" class="text-center py-16 text-gray-400">
      <p class="mb-2">暂无上传的文件</p>
      <p class="text-sm">点击上方按钮上传图片</p>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="group border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white dark:bg-gray-800"
      >
        <div class="aspect-square bg-gray-100 dark:bg-gray-900 flex items-center justify-center overflow-hidden cursor-pointer" @click="openPreview(item)">
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

    <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
      <button :disabled="page <= 1" @click="load(page - 1)" class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-400">上一页</button>
      <span class="px-3 py-1.5 text-sm text-gray-400">{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="load(page + 1)" class="px-3 py-1.5 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-400">下一页</button>
    </div>

    <Teleport to="body">
      <div
        v-if="previewItem"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
        @click="onPreviewOverlayClick"
      >
        <div class="relative max-w-4xl max-h-[90vh] w-full mx-4 bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-2xl" @click.stop>
          <button @click="closePreview" class="absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
          <div class="flex items-center justify-center bg-gray-100 dark:bg-gray-900 max-h-[70vh] overflow-auto">
            <img
              v-if="previewItem.mime_type.startsWith('image/')"
              :src="previewItem.url"
              :alt="previewItem.filename"
              class="max-w-full max-h-[70vh] object-contain"
            />
            <div v-else class="p-16 text-center text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
              <p>无法预览此文件类型</p>
            </div>
          </div>
          <div class="p-4 border-t border-gray-200 dark:border-gray-700">
            <p class="font-medium text-sm truncate">{{ previewItem.filename }}</p>
            <div class="flex gap-4 mt-1 text-xs text-gray-400">
              <span>{{ formatSize(previewItem.size) }}</span>
              <span>{{ previewItem.mime_type }}</span>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
