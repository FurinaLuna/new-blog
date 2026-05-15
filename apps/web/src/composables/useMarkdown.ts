import { computed } from "vue";
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
import DOMPurify from "dompurify";

DOMPurify.addHook("uponSanitizeElement", (node, data) => {
  if (data.tagName === "code" && node instanceof HTMLElement) {
    const cls = node.getAttribute("class");
    if (cls) {
      node.setAttribute("class", cls);
    }
  }
});

const purifyConfig = {
  ADD_ATTR: ["class"],
};

let initialized = false;

function setup() {
  if (initialized) return;
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
  initialized = true;
}

export function useMarkdown(content: () => string) {
  setup();
  return computed(() => DOMPurify.sanitize(marked(content()) as string, purifyConfig));
}
