import { ref } from "vue";
import type { PostDetail } from "@/types";
import { fetchPost, fetchPostSummary } from "@/api/posts";
import { SITE_NAME } from "@/utils/constants";

export function usePostData() {
  const post = ref<PostDetail | null>(null);
  const summary = ref("");
  const loading = ref(true);
  const loadingSummary = ref(false);
  const error = ref("");
  let currentSlug = "";

  async function load(slug: string) {
    currentSlug = slug;
    loading.value = true;
    error.value = "";
    summary.value = "";
    loadingSummary.value = false;
    try {
      post.value = await fetchPost(slug);
      if (currentSlug !== slug) return;
      document.title = `${post.value.title} — ${SITE_NAME}`;
      loadingSummary.value = true;
      const res = await fetchPostSummary(slug);
      if (currentSlug === slug) summary.value = res.summary;
    } catch {
      if (currentSlug === slug) {
        error.value = "文章不存在或未发布。";
        document.title = `文章不存在 — ${SITE_NAME}`;
      }
    } finally {
      if (currentSlug === slug) {
        loading.value = false;
        loadingSummary.value = false;
      }
    }
  }

  return { post, summary, loading, loadingSummary, error, load };
}
