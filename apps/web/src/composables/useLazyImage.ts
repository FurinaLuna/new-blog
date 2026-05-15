import type { Directive, DirectiveBinding } from "vue";

interface LazyState {
  loaded: boolean;
  error: boolean;
}

const observerMap = new WeakMap<Element, IntersectionObserver>();
const stateMap = new WeakMap<Element, LazyState>();

const defaultPlaceholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%23f3f4f6' width='400' height='300'/%3E%3C/svg%3E";

function createObserver(el: HTMLImageElement, binding: DirectiveBinding) {
  const src = binding.value as string;
  const placeholder = binding.arg || defaultPlaceholder;

  el.src = placeholder;
  stateMap.set(el, { loaded: false, error: false });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const tempImg = new Image();
          tempImg.src = src;
          tempImg.onload = () => {
            img.src = src;
            const state = stateMap.get(img);
            if (state) state.loaded = true;
            img.classList.remove("lazy-loading");
            img.classList.add("lazy-loaded");
          };
          tempImg.onerror = () => {
            const state = stateMap.get(img);
            if (state) state.error = true;
            img.classList.remove("lazy-loading");
            img.classList.add("lazy-error");
          };
          img.classList.add("lazy-loading");
          observer.unobserve(img);
          observerMap.delete(img);
        }
      });
    },
    { rootMargin: "200px" }
  );

  observer.observe(el);
  observerMap.set(el, observer);
}

export const vLazy: Directive<HTMLImageElement, string> = {
  mounted(el, binding) {
    createObserver(el, binding);
  },
  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      const oldObserver = observerMap.get(el);
      if (oldObserver) {
        oldObserver.disconnect();
        observerMap.delete(el);
      }
      createObserver(el, binding);
    }
  },
  unmounted(el) {
    const observer = observerMap.get(el);
    if (observer) {
      observer.disconnect();
      observerMap.delete(el);
    }
    stateMap.delete(el);
  },
};

export function useLazyImage() {
  return { vLazy };
}
