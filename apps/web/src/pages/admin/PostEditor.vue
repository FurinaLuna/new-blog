<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";
import { adminCreatePost, adminUpdatePost, adminFetchPosts, adminReindexPost, adminUploadMedia } from "@/api/admin";
import { fetchPost } from "@/api/posts";
import { fetchTags } from "@/api/tags";
import type { Tag } from "@/types";

marked.use(
  markedHighlight({
    highlight(code: string, lang: string) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    },
  })
);

const route = useRoute();
const router = useRouter();
const isEdit = computed(() => !!route.params.slug);
const saving = ref(false);

const title = ref("");
const slug = ref("");
const content = ref("");
const excerpt = ref("");
const coverImage = ref("");
const published = ref(false);
const featured = ref(false);
const selectedTags = ref<string[]>([]);

const allTags = ref<Tag[]>([]);
const newTagName = ref("");
const newTagSlug = ref("");
const previewMode = ref(false);

const previewHtml = computed(() => marked(content.value) as string);

onMounted(async () => {
  allTags.value = await fetchTags();

  if (isEdit.value) {
    const editSlug = route.params.slug as string;
    const post = await fetchPost(editSlug);
    title.value = post.title;
    slug.value = post.slug;
    content.value = post.content;
    excerpt.value = post.excerpt || "";
    coverImage.value = post.cover_image || "";
    selectedTags.value = post.tags.map((t) => t.id);
    // The public fetchPost doesn't return published/featured; they default to false for safety
  }
});

function generateSlug() {
  if (!slug.value && title.value) {
    slug.value = title.value
      .toLowerCase()
      .replace(/[^a-z0-9一-龥]+/g, "-")
      .replace(/^-|-$/g, "");
  }
}

function toggleTag(tagId: string) {
  const idx = selectedTags.value.indexOf(tagId);
  if (idx >= 0) selectedTags.value.splice(idx, 1);
  else selectedTags.value.push(tagId);
}

async function onUploadImage(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  const res = await adminUploadMedia(file);
  content.value += `\n![${res.filename}](${res.url})\n`;
}

async function onSave() {
  saving.value = true;
  try {
    const payload = {
      title: title.value,
      slug: slug.value,
      content: content.value,
      excerpt: excerpt.value || null,
      cover_image: coverImage.value || null,
      published: published.value,
      featured: featured.value,
      tag_ids: selectedTags.value,
    };

    if (isEdit.value) {
      const originalSlug = route.params.slug as string;
      const res = await adminFetchPosts(1, 200, originalSlug);
      const adminPost = res.items.find((p) => p.slug === originalSlug);
      if (adminPost) {
        await adminUpdatePost(adminPost.id, payload);
        try { await adminReindexPost(adminPost.id); } catch { /* optional */ }
      }
    } else {
      await adminCreatePost(payload);
    }
    router.push("/admin/posts");
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold">{{ isEdit ? "编辑文章" : "新建文章" }}</h1>
      <div class="flex gap-2">
        <button
          @click="previewMode = !previewMode"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          {{ previewMode ? "编辑" : "预览" }}
        </button>
        <button
          @click="onSave"
          :disabled="saving"
          class="px-4 py-1.5 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {{ saving ? "保存中..." : "保存" }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main editor -->
      <div class="lg:col-span-2 space-y-4">
        <div>
          <input
            v-model="title"
            @blur="generateSlug"
            type="text"
            placeholder="文章标题"
            class="w-full px-4 py-3 text-lg font-bold rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
          />
        </div>
        <div>
          <input
            v-model="slug"
            type="text"
            placeholder="slug (URL标识)"
            class="w-full px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400 font-mono"
          />
        </div>

        <div v-if="previewMode" class="prose-custom min-h-[400px] border border-gray-300 dark:border-gray-600 rounded-lg p-4 bg-white dark:bg-gray-900" v-html="previewHtml"></div>
        <textarea
          v-else
          v-model="content"
          rows="18"
          placeholder="Markdown 内容..."
          class="w-full px-4 py-3 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400 font-mono resize-y"
        ></textarea>

        <div>
          <label class="block text-sm font-medium mb-1">上传图片</label>
          <input type="file" accept="image/*" @change="onUploadImage" class="text-sm" />
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-4">
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
          <h3 class="font-semibold text-sm mb-3">发布设置</h3>
          <label class="flex items-center gap-2 mb-2 cursor-pointer">
            <input v-model="published" type="checkbox" class="rounded" />
            <span class="text-sm">发布</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="featured" type="checkbox" class="rounded" />
            <span class="text-sm">精选</span>
          </label>
        </div>

        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
          <h3 class="font-semibold text-sm mb-3">摘要</h3>
          <textarea
            v-model="excerpt"
            rows="3"
            placeholder="文章摘要..."
            class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400 resize-y"
          ></textarea>
        </div>

        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
          <h3 class="font-semibold text-sm mb-3">封面图 URL</h3>
          <input
            v-model="coverImage"
            type="text"
            placeholder="https://..."
            class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
          />
        </div>

        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800">
          <h3 class="font-semibold text-sm mb-3">标签</h3>
          <div class="flex flex-wrap gap-1.5 mb-3">
            <button
              v-for="tag in allTags"
              :key="tag.id"
              @click="toggleTag(tag.id)"
              :class="[
                'text-xs px-2 py-1 rounded-full transition-colors',
                selectedTags.includes(tag.id)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600',
              ]"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
