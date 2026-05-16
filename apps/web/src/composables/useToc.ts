import { ref, watch, onMounted, onUnmounted, type Ref } from "vue";

export interface TocHeading {
  id: string;
  text: string;
  level: number;
}

export function useToc(contentRef: Ref<HTMLElement | null>) {
  const headings = ref<TocHeading[]>([]);
  const activeHeading = ref("");
  let observer: IntersectionObserver | null = null;

  function extractHeadings() {
    if (!contentRef.value) {
      headings.value = [];
      return;
    }
    const elements = contentRef.value.querySelectorAll("h2, h3");
    headings.value = Array.from(elements).map((el) => ({
      id: el.id,
      text: el.textContent || "",
      level: Number(el.tagName[1]),
    }));
  }

  function setupObserver() {
    if (observer) observer.disconnect();
    if (!contentRef.value || headings.value.length === 0) return;

    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            activeHeading.value = entry.target.id;
          }
        }
      },
      { rootMargin: "-80px 0px -60% 0px", threshold: 0.1 }
    );

    headings.value.forEach((h) => {
      const el = contentRef.value!.querySelector(`#${CSS.escape(h.id)}`);
      if (el) observer!.observe(el);
    });
  }

  function scrollToHeading(id: string) {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      activeHeading.value = id;
    }
  }

  onMounted(() => {
    extractHeadings();
    setupObserver();
  });

  watch(contentRef, () => {
    setTimeout(() => {
      extractHeadings();
      setupObserver();
    }, 100);
  });

  onUnmounted(() => {
    if (observer) observer.disconnect();
  });

  return { headings, activeHeading, scrollToHeading };
}
