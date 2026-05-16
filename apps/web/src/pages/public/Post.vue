<script setup lang="ts">
import { ref, watch, nextTick, computed } from "vue";
import { useRoute } from "vue-router";
import "highlight.js/styles/github-dark.css";

import { usePostData } from "@/composables/usePostData";
import { useMarkdown } from "@/composables/useMarkdown";
import { useScrollTracking } from "@/composables/useScrollTracking";
import { useFormatDate } from "@/composables/useFormatDate";
import { useToc } from "@/composables/useToc";
import { useCodeCopy } from "@/composables/useCodeCopy";
import { useSeo } from "@/composables/useSeo";

import { SITE_NAME, SITE_AUTHOR } from "@/utils/constants";
import ReadingProgressBar from "@/components/blog/ReadingProgressBar.vue";
import AiSummaryBox from "@/components/blog/AiSummaryBox.vue";
import PostNavigation from "@/components/blog/PostNavigation.vue";
import CommentSection from "@/components/blog/CommentSection.vue";
import ShareButtons from "@/components/blog/ShareButtons.vue";
import BaseSkeleton from "@/components/ui/BaseSkeleton.vue";
import BaseEmptyState from "@/components/ui/BaseEmptyState.vue";

const route = useRoute();
const { post, summary, loading, loadingSummary, error, load } = usePostData();
const { formatDate } = useFormatDate();
const renderedContent = useMarkdown(() => post.value?.content ?? "");
const { setMeta } = useSeo();

const contentEl = ref<HTMLElement | null>(null);
const { headings, activeHeading, scrollToHeading } = useToc(contentEl);
const { addCopyButtons } = useCodeCopy(contentEl);

const showTocMobile = ref(false);
const pageUrl = computed(() => `${window.location.origin}/post/${post.value?.slug ?? ""}`);

const postId = () => post.value?.id ?? null;
const postSlug = () => post.value?.slug ?? null;
const { scrollProgress, reset: resetTracking } = useScrollTracking(postId, postSlug);

load(route.params.slug as string);

watch(() => route.params.slug, (slug) => {
  resetTracking();
  load(slug as string);
});

watch(renderedContent, () => {
  nextTick(() => {
    addCopyButtons();
  });
});

watch(post, (p) => {
  if (p) {
    setMeta({
      title: `${p.title} — ${SITE_NAME}`,
      description: p.excerpt || p.title,
      image: p.cover_image || undefined,
      url: `${window.location.origin}/post/${p.slug}`,
      type: "article",
    });
  }
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

      <div class="lg:flex lg:gap-8">
        <div class="prose-custom dark:prose-invert min-w-0 flex-1" ref="contentEl" v-html="renderedContent"></div>

        <aside v-if="headings.length > 0" class="hidden lg:block w-56 shrink-0">
          <nav class="sticky top-24">
            <h4 class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4">目录</h4>
            <ul class="space-y-1.5 border-l border-gray-200 dark:border-gray-800 pl-3">
              <li v-for="h in headings" :key="h.id">
                <button
                  @click="scrollToHeading(h.id)"
                  :class="[
                    'block text-left text-sm transition-colors leading-snug py-0.5',
                    h.level === 3 ? 'pl-3' : '',
                    activeHeading === h.id
                      ? 'text-primary-600 dark:text-primary-400 font-medium'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                  ]"
                >
                  {{ h.text }}
                </button>
              </li>
            </ul>
          </nav>
        </aside>
      </div>

      <div class="mt-10 pt-6 border-t border-gray-100 dark:border-gray-800">
        <ShareButtons :url="pageUrl" :title="post.title" />
      </div>

      <PostNavigation :prev-post="post.prev_post" :next-post="post.next_post" />

      <div class="mt-20">
        <CommentSection :post-id="post.id" />
      </div>
    </article>
  </div>

  <button
    v-if="headings.length > 0"
    @click="showTocMobile = !showTocMobile"
    class="lg:hidden fixed bottom-6 right-6 z-40 w-12 h-12 rounded-full bg-primary-600 text-white shadow-lg flex items-center justify-center hover:bg-primary-700 transition-colors"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h10M4 18h7"/></svg>
  </button>

  <Teleport to="body">
    <Transition name="toc-slide">
      <div
        v-if="showTocMobile"
        class="fixed inset-0 z-50 lg:hidden"
      >
        <div class="absolute inset-0 bg-black/40" @click="showTocMobile = false"></div>
        <div class="absolute right-0 top-0 bottom-0 w-72 bg-white dark:bg-gray-900 shadow-2xl p-6 overflow-y-auto">
          <div class="flex items-center justify-between mb-6">
            <h4 class="text-sm font-bold uppercase tracking-widest text-gray-400">目录</h4>
            <button @click="showTocMobile = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <ul class="space-y-2">
            <li v-for="h in headings" :key="h.id">
              <button
                @click="scrollToHeading(h.id); showTocMobile = false"
                :class="[
                  'block text-left text-sm transition-colors leading-snug py-1',
                  h.level === 3 ? 'pl-4' : '',
                  activeHeading === h.id
                    ? 'text-primary-600 dark:text-primary-400 font-medium'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                ]"
              >
                {{ h.text }}
              </button>
            </li>
          </ul>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.toc-slide-enter-active,
.toc-slide-leave-active {
  transition: opacity 0.2s ease;
}
.toc-slide-enter-from,
.toc-slide-leave-to {
  opacity: 0;
}
</style>
