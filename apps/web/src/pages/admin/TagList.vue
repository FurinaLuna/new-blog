<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Tag } from "@/types";
import { adminFetchTags, adminCreateTag, adminUpdateTag, adminDeleteTag } from "@/api/admin";
import { useToast } from "@/composables/useToast";
import { useConfirm } from "@/composables/useConfirm";

const toast = useToast();
const { confirm } = useConfirm();
const tags = ref<Tag[]>([]);
const loading = ref(true);
const error = ref("");

const showCreateDialog = ref(false);
const showEditDialog = ref(false);
const editingTag = ref<Tag | null>(null);
const formName = ref("");
const formSlug = ref("");
const submitting = ref(false);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    tags.value = await adminFetchTags();
  } catch {
    error.value = "加载标签列表失败";
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  formName.value = "";
  formSlug.value = "";
  showCreateDialog.value = true;
}

function openEdit(tag: Tag) {
  editingTag.value = tag;
  formName.value = tag.name;
  formSlug.value = tag.slug;
  showEditDialog.value = true;
}

async function onCreate() {
  submitting.value = true;
  try {
    await adminCreateTag({ name: formName.value, slug: formSlug.value });
    toast.success("标签创建成功");
    showCreateDialog.value = false;
    await load();
  } catch {
    toast.error("创建失败");
  } finally {
    submitting.value = false;
  }
}

async function onUpdate() {
  if (!editingTag.value) return;
  submitting.value = true;
  try {
    await adminUpdateTag(editingTag.value.id, { name: formName.value, slug: formSlug.value });
    toast.success("标签更新成功");
    showEditDialog.value = false;
    await load();
  } catch {
    toast.error("更新失败");
  } finally {
    submitting.value = false;
  }
}

async function onDelete(tag: Tag) {
  if (tag.post_count && tag.post_count > 0) {
    toast.error(`该标签下有 ${tag.post_count} 篇关联文章，无法删除`);
    return;
  }
  const ok = await confirm(`确定删除标签「${tag.name}」吗？`);
  if (!ok) return;
  try {
    await adminDeleteTag(tag.id);
    toast.success("标签已删除");
    await load();
  } catch {
    toast.error("删除失败");
  }
}

onMounted(load);
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold">标签管理</h1>
      <button @click="openCreate" class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
        创建标签
      </button>
    </div>

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
            <th class="text-left px-4 py-2.5 font-medium">名称</th>
            <th class="text-left px-4 py-2.5 font-medium">Slug</th>
            <th class="text-left px-4 py-2.5 font-medium">文章数</th>
            <th class="text-right px-4 py-2.5 font-medium">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="tags.length === 0">
            <td colspan="4" class="text-center py-12 text-gray-400">暂无标签</td>
          </tr>
          <tr
            v-for="tag in tags"
            :key="tag.id"
            class="border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <td class="px-4 py-2.5 font-medium">{{ tag.name }}</td>
            <td class="px-4 py-2.5 text-gray-500">{{ tag.slug }}</td>
            <td class="px-4 py-2.5">
              <span :class="['text-xs px-2 py-0.5 rounded-full', tag.post_count ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-500']">
                {{ tag.post_count || 0 }}
              </span>
            </td>
            <td class="px-4 py-2.5 text-right">
              <div class="flex gap-2 justify-end">
                <button @click="openEdit(tag)" class="text-sm text-primary-600 hover:underline">编辑</button>
                <button @click="onDelete(tag)" class="text-sm text-red-500 hover:underline">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showCreateDialog || showEditDialog" class="fixed inset-0 z-50 flex items-center justify-center" @click.self="showCreateDialog = false; showEditDialog = false">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
          <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
            <h2 class="text-lg font-bold mb-4">{{ showEditDialog ? '编辑标签' : '创建标签' }}</h2>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-1" for="tag-name">名称</label>
                <input id="tag-name" v-model="formName" type="text" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1" for="tag-slug">Slug</label>
                <input id="tag-slug" v-model="formSlug" type="text" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400" />
              </div>
            </div>
            <div class="flex justify-end gap-3 mt-6">
              <button @click="showCreateDialog = false; showEditDialog = false" class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">取消</button>
              <button @click="showEditDialog ? onUpdate() : onCreate()" :disabled="submitting" class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-30 transition-colors">
                {{ submitting ? '提交中...' : '确定' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
