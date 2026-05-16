import { computed } from "vue";
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js/lib/core";
import javascript from "highlight.js/lib/languages/javascript";
import typescript from "highlight.js/lib/languages/typescript";
import python from "highlight.js/lib/languages/python";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";
import json from "highlight.js/lib/languages/json";
import bash from "highlight.js/lib/languages/bash";
import sql from "highlight.js/lib/languages/sql";
import markdown from "highlight.js/lib/languages/markdown";
import DOMPurify from "dompurify";

hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("python", python);
hljs.registerLanguage("css", css);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("json", json);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("markdown", markdown);

DOMPurify.addHook("uponSanitizeElement", (node, data) => {
  if (data.tagName === "code" && node instanceof HTMLElement) {
    const cls = node.getAttribute("class");
    if (cls) {
      node.setAttribute("class", cls);
    }
  }
});

const purifyConfig = {
  ADD_ATTR: ["class", "id"],
};

let initialized = false;

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fff]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function setup() {
  if (initialized) return;
  const renderer = {
    heading({ text, depth }: { text: string; depth: number }) {
      const rawText = text.replace(/<[^>]*>/g, "");
      const id = slugify(rawText);
      return `<h${depth} id="${id}">${text}</h${depth}>`;
    },
  };
  marked.use(
    { renderer },
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
