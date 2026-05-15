import { SITE_NAME, SITE_AUTHOR, DEFAULT_OG_IMAGE } from "@/utils/constants";

interface SEOOptions {
  title: string;
  description: string;
  image?: string;
  url?: string;
  type?: "website" | "article";
  publishedTime?: string;
  tags?: string[];
  articleBody?: string;
  noindex?: boolean;
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

function removeMetaTag(name: string, property = false) {
  const attr = property ? "property" : "name";
  const el = document.querySelector(`meta[${attr}="${name}"]`);
  if (el) el.remove();
}

function setCanonical(url: string) {
  let el = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
  if (!el) {
    el = document.createElement("link");
    el.rel = "canonical";
    document.head.appendChild(el);
  }
  el.href = url;
}

function removeCanonical() {
  const el = document.querySelector('link[rel="canonical"]');
  if (el) el.remove();
}

function setNoindex(noindex: boolean) {
  const id = "meta-robots-noindex";
  let el = document.getElementById(id) as HTMLMetaElement | null;
  if (noindex) {
    if (!el) {
      el = document.createElement("meta");
      el.id = id;
      el.name = "robots";
      el.content = "noindex, nofollow";
      document.head.appendChild(el);
    }
  } else {
    if (el) el.remove();
  }
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
    const { title, description, image, url, type = "website", publishedTime, tags, articleBody, noindex = false } = options;
    const fullTitle = `${title} — ${SITE_NAME}`;
    const imageUrl = image || DEFAULT_OG_IMAGE;
    const pageUrl = url || window.location.href;

    document.title = fullTitle;

    setMetaTag("description", description);
    setMetaTag("og:title", fullTitle, true);
    setMetaTag("og:description", description, true);
    setMetaTag("og:image", imageUrl, true);
    setMetaTag("og:type", type, true);
    setMetaTag("og:url", pageUrl, true);
    setMetaTag("twitter:card", "summary_large_image");
    setMetaTag("twitter:title", fullTitle);
    setMetaTag("twitter:description", description);
    setMetaTag("twitter:image", imageUrl);

    setCanonical(pageUrl);
    setNoindex(noindex);

    const ldJson: Record<string, unknown> = {
      "@context": "https://schema.org",
      "@type": type === "article" ? "BlogPosting" : "WebSite",
      headline: title,
      description,
      image: imageUrl,
      datePublished: publishedTime,
      keywords: tags?.join(", "),
      author: { "@type": "Person", name: SITE_AUTHOR },
    };

    if (type === "article" && articleBody) {
      ldJson.articleBody = articleBody;
    }

    setLdJson(ldJson);
  };

  const clearNoindex = () => setNoindex(false);

  return { setMeta, clearNoindex };
}
