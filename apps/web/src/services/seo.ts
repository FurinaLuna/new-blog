import { SITE_NAME, SITE_AUTHOR, DEFAULT_OG_IMAGE } from "@/utils/constants";

interface SEOOptions {
  title: string;
  description: string;
  image?: string;
  url?: string;
  type?: "website" | "article";
  publishedTime?: string;
  tags?: string[];
}

function setMetaTag(name: string, content: string, property = false) {
  const attr = property ? "property" : "name";
  let el = document.querySelector(`meta[${attr}="${name}"]`) as HTMLMetaElement | null;
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, name);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function setLdJson(script: object) {
  const id = "ld-json-seo";
  let el = document.getElementById(id) as HTMLScriptElement | null;
  if (!el) {
    el = document.createElement("script");
    el.id = id;
    el.type = "application/ld+json";
    document.head.appendChild(el);
  }
  el.textContent = JSON.stringify(script);
}

export function useSEO() {
  const setMeta = (options: SEOOptions) => {
    const { title, description, image, url, type = "website", publishedTime, tags } = options;
    const fullTitle = `${title} — ${SITE_NAME}`;
    const imageUrl = image || DEFAULT_OG_IMAGE;

    document.title = fullTitle;

    setMetaTag("description", description);
    setMetaTag("og:title", fullTitle, true);
    setMetaTag("og:description", description, true);
    setMetaTag("og:image", imageUrl, true);
    setMetaTag("og:type", type, true);
    setMetaTag("og:url", url || window.location.href, true);
    setMetaTag("twitter:card", "summary_large_image");
    setMetaTag("twitter:title", fullTitle);
    setMetaTag("twitter:description", description);
    setMetaTag("twitter:image", imageUrl);

    setLdJson({
      "@context": "https://schema.org",
      "@type": type === "article" ? "BlogPosting" : "WebSite",
      headline: title,
      description,
      image: imageUrl,
      datePublished: publishedTime,
      keywords: tags?.join(", "),
      author: { "@type": "Person", name: SITE_AUTHOR },
    });
  };

  return { setMeta };
}
