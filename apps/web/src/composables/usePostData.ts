import { ref } from "vue";
import type { PostDetail } from "@/types";
import { fetchPost, fetchPostSummary } from "@/api/posts";

export function usePostData() {
  const post = ref<PostDetail | null>(null);
  const summary = ref("");
  const loading = ref(true);
  const loadingSummary = ref(false);
  const error = ref("");

  async function load(slug: string) {
    loading.value = true;
    error.value = "";
    summary.value = "";
    try {
      post.value = await fetchPost(slug);
      document.title = `${post.value.title} — My Blog`;
      loadSummary(slug);
    } catch {
      error.value = "文章不存在或未发布。";
      document.title = "文章不存在 — My Blog";
    } finally {
      loading.value = false;
    }
  }

  async function loadSummary(slug: string) {
    loadingSummary.value = true;
    try {
      const res = await fetchPostSummary(slug);
      summary.value = res.summary;
    } catch {
      summary.value = "";
    } finally {
      loadingSummary.value = false;
    }
  }

  return { post, summary, loading, loadingSummary, error, load };
}
