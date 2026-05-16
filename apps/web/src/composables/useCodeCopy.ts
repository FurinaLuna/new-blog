import { onUnmounted, type Ref } from "vue";

export function useCodeCopy(contentRef: Ref<HTMLElement | null>) {
  const buttons: HTMLButtonElement[] = [];

  function addCopyButtons() {
    if (!contentRef.value) return;
    const blocks = contentRef.value.querySelectorAll("pre");
    blocks.forEach((pre) => {
      const code = pre.querySelector("code");
      if (!code) return;

      pre.style.position = "relative";

      const btn = document.createElement("button");
      btn.textContent = "复制";
      btn.className =
        "absolute top-2 right-2 px-2 py-1 text-xs rounded-md bg-white/10 hover:bg-white/20 text-gray-400 hover:text-gray-200 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100";
      pre.classList.add("group");

      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(code.textContent || "");
          btn.textContent = "已复制!";
          btn.classList.add("text-green-400");
          setTimeout(() => {
            btn.textContent = "复制";
            btn.classList.remove("text-green-400");
          }, 2000);
        } catch {
          btn.textContent = "失败";
          setTimeout(() => {
            btn.textContent = "复制";
          }, 2000);
        }
      });

      pre.appendChild(btn);
      buttons.push(btn);
    });
  }

  function removeCopyButtons() {
    buttons.forEach((btn) => {
      if (btn.parentNode) btn.parentNode.removeChild(btn);
    });
    buttons.length = 0;
  }

  onUnmounted(() => {
    removeCopyButtons();
  });

  return { addCopyButtons, removeCopyButtons };
}
