import { onUnmounted } from "vue";

interface SeoOptions {
  title?: string;
  description?: string;
  image?: string;
  url?: string;
  type?: string;
}

function getOrCreateMeta(attr: string, name: string): HTMLMetaElement {
  let el = document.querySelector(`meta[${attr}="${name}"]`) as HTMLMetaElement | null;
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, name);
    document.head.appendChild(el);
  }
  return el;
}

const managedTags: string[] = [];

function setMetaContent(attr: string, name: string, content: string) {
  const el = getOrCreateMeta(attr, name);
  el.setAttribute("content", content);
  if (!managedTags.includes(name)) managedTags.push(name);
}

export function useSeo() {
  let jsonLdEl: HTMLScriptElement | null = null;

  function setMeta(options: SeoOptions) {
    const { title, description, image, url, type = "website" } = options;
    const pageUrl = url || window.location.href;

    if (title) document.title = title;
    if (description) {
      setMetaContent("name", "description", description);
      setMetaContent("property", "og:description", description);
      setMetaContent("name", "twitter:description", description);
    }
    if (title) {
      setMetaContent("property", "og:title", title);
      setMetaContent("name", "twitter:title", title);
    }
    if (image) {
      setMetaContent("property", "og:image", image);
      setMetaContent("name", "twitter:image", image);
    }
    setMetaContent("property", "og:url", pageUrl);
    setMetaContent("property", "og:type", type);
    setMetaContent("name", "twitter:card", "summary_large_image");
  }

  function setJsonLd(data: object) {
    if (!jsonLdEl) {
      jsonLdEl = document.createElement("script");
      jsonLdEl.type = "application/ld+json";
      jsonLdEl.id = "seo-json-ld";
      document.head.appendChild(jsonLdEl);
    }
    jsonLdEl.textContent = JSON.stringify(data);
  }

  function cleanup() {
    managedTags.forEach((name) => {
      const el = document.querySelector(`meta[name="${name}"]`) || document.querySelector(`meta[property="${name}"]`);
      if (el) el.remove();
    });
    managedTags.length = 0;
    if (jsonLdEl) {
      jsonLdEl.remove();
      jsonLdEl = null;
    }
  }

  onUnmounted(cleanup);

  return { setMeta, setJsonLd };
}
