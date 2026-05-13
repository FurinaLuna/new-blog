import { ref, onMounted, onUnmounted } from "vue";
import { track } from "@/tracking";

export function useScrollTracking(
  postId: () => string | null,
  postSlug: () => string | null,
) {
  const scrollProgress = ref(0);
  const hasTrackedRead = ref(false);

  function onScroll() {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    if (total <= 0) return;
    scrollProgress.value = Math.min(100, Math.max(0, (window.scrollY / total) * 100));

    if (hasTrackedRead.value || !postId()) return;
    if (scrollProgress.value >= 80) {
      hasTrackedRead.value = true;
      track("post_read", {
        post_id: postId()!,
        post_slug: postSlug()!,
        scroll_depth: "80%",
      });
    }
  }

  function reset() {
    hasTrackedRead.value = false;
    scrollProgress.value = 0;
  }

  onMounted(() => window.addEventListener("scroll", onScroll, { passive: true }));
  onUnmounted(() => window.removeEventListener("scroll", onScroll));

  return { scrollProgress, reset };
}
