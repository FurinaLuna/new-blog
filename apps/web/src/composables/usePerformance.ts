import { track } from "@/tracking";

interface PerformanceMetrics {
  dns: number;
  tcp: number;
  ssl: number;
  ttfb: number;
  domInteractive: number;
  domComplete: number;
  loadComplete: number;
  fp: number | null;
  fcp: number | null;
  lcp: number | null;
  cls: number | null;
}

function getNavigationTiming(): Partial<PerformanceMetrics> | null {
  const entries = performance.getEntriesByType("navigation") as PerformanceNavigationTiming[];
  if (!entries.length) return null;
  const nav = entries[0];
  return {
    dns: nav.domainLookupEnd - nav.domainLookupStart,
    tcp: nav.connectEnd - nav.connectStart,
    ssl: nav.secureConnectionStart > 0 ? nav.connectEnd - nav.secureConnectionStart : 0,
    ttfb: nav.responseStart - nav.requestStart,
    domInteractive: nav.domInteractive - nav.fetchStart,
    domComplete: nav.domComplete - nav.fetchStart,
    loadComplete: nav.loadEventEnd - nav.fetchStart,
  };
}

function getPaintMetrics(): Pick<PerformanceMetrics, "fp" | "fcp"> {
  const entries = performance.getEntriesByType("paint") as PerformanceEntry[];
  let fp: number | null = null;
  let fcp: number | null = null;
  for (const entry of entries) {
    if (entry.name === "first-paint") fp = entry.startTime;
    if (entry.name === "first-contentful-paint") fcp = entry.startTime;
  }
  return { fp, fcp };
}

function observeLCP(): Promise<number | null> {
  return new Promise((resolve) => {
    if (!("PerformanceObserver" in window)) {
      resolve(null);
      return;
    }
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        if (entries.length > 0) {
          resolve(entries[entries.length - 1].startTime);
          observer.disconnect();
        }
      });
      observer.observe({ type: "largest-contentful-paint", buffered: true });
      setTimeout(() => {
        observer.disconnect();
        resolve(null);
      }, 5000);
    } catch {
      resolve(null);
    }
  });
}

function observeCLS(): Promise<number | null> {
  return new Promise((resolve) => {
    if (!("PerformanceObserver" in window)) {
      resolve(null);
      return;
    }
    try {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
      });
      observer.observe({ type: "layout-shift", buffered: true });
      setTimeout(() => {
        observer.disconnect();
        resolve(clsValue || null);
      }, 5000);
    } catch {
      resolve(null);
    }
  });
}

export function usePerformance() {
  async function reportMetrics() {
    const navTiming = getNavigationTiming();
    const paintMetrics = getPaintMetrics();
    const lcp = await observeLCP();
    const cls = await observeCLS();

    const metrics: Record<string, unknown> = {
      ...navTiming,
      ...paintMetrics,
      lcp,
      cls,
      url: window.location.href,
      timestamp: Date.now(),
    };

    track("performance_metrics", metrics);
  }

  function init() {
    if (document.readyState === "complete") {
      setTimeout(reportMetrics, 0);
    } else {
      window.addEventListener("load", () => {
        setTimeout(reportMetrics, 0);
      });
    }
  }

  return { reportMetrics, init };
}
