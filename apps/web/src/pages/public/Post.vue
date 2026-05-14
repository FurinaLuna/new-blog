<script setup lang="ts">
import { watch } from "vue";
import { useRoute } from "vue-router";
import "highlight.js/styles/github-dark.css";

import { usePostData } from "@/composables/usePostData";
import { useMarkdown } from "@/composables/useMarkdown";
import { useScrollTracking } from "@/composables/useScrollTracking";
import { useFormatDate } from "@/composables/useFormatDate";

import { SITE_AUTHOR } from "@/utils/constants";
import ReadingProgressBar from "@/components/blog/ReadingProgressBar.vue";
import AiSummaryBox from "@/components/blog/AiSummaryBox.vue";
import PostNavigation from "@/components/blog/PostNavigation.vue";
import CommentSection from "@/components/blog/CommentSection.vue";
import BaseSkeleton from "@/components/ui/BaseSkeleton.vue";
import BaseEmptyState from "@/components/ui/BaseEmptyState.vue";

const route = useRoute();
const { post, summary, loading, loadingSummary, error, load } = usePostData();
const { formatDate } = useFormatDate();
const renderedContent = useMarkdown(() => post.value?.content ?? "");

const postId = () => post.value?.id ?? null;
const postSlug = () => post.value?.slug ?? null;
const { scrollProgress, reset: resetTracking } = useScrollTracking(postId, postSlug);

// Initial load
load(route.params.slug as string);

// React to route changes
watch(() => route.params.slug, (slug) => {
  resetTracking();
  load(slug as string);
});
</script>

<template>
  <ReadingProgressBar :progress="scrollProgress" />

  <div class="max-w-3xl mx-auto px-4 py-8">
    <BaseSkeleton v-if="loading" />

    <BaseEmptyState
      v-else-if="error"
      icon="🏜️"
      :message="error"
      link-to="/"
      link-text="返回首页"
    />

    <article v-else-if="post" class="animate-fade-in-up">
      <header class="mb-12">
        <!-- Tags -->
        <div class="flex items-center gap-3 mb-6">
          <span
            v-for="tag in post.tags"
            :key="tag.id"
            class="text-[10px] uppercase tracking-widest font-bold bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 px-3 py-1 rounded-full border border-primary-100 dark:border-primary-800/50"
          >
            <router-link :to="`/tag/${tag.slug}`">{{ tag.name }}</router-link>
          </span>
          <span class="text-xs text-gray-400 flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
            {{ post.view_count }}
          </span>
        </div>

        <h1 class="text-4xl sm:text-5xl font-extrabold mb-6 tracking-tight text-gray-900 dark:text-white leading-[1.1]">
          {{ post.title }}
        </h1>

        <div class="flex items-center gap-4 text-sm text-gray-400 border-b border-gray-100 dark:border-gray-800 pb-8">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-400 to-primary-600"></div>
            <span class="font-medium text-gray-600 dark:text-gray-300">{{ SITE_AUTHOR }}</span>
          </div>
          <span>•</span>
          <time :datetime="post.created_at">{{ formatDate(post.created_at) }}</time>
        </div>
      </header>

      <AiSummaryBox :summary="summary" :loading="loadingSummary" />

      <div class="prose-custom dark:prose-invert" v-html="renderedContent"></div>

      <PostNavigation :prev-post="post.prev_post" :next-post="post.next_post" />

      <div class="mt-20">
        <CommentSection :post-id="post.id" />
      </div>
    </article>
  </div>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
