import type { TrackingEvent } from "@/types";
import { sendTrackingEvents } from "@/api/tracking";

let sessionId = sessionStorage.getItem("blog_session_id");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  sessionStorage.setItem("blog_session_id", sessionId);
}

const eventQueue: TrackingEvent[] = [];
let flushTimer: ReturnType<typeof setTimeout> | null = null;

function flush() {
  if (eventQueue.length === 0) return;
  const batch = eventQueue.splice(0, eventQueue.length);
  if (navigator.sendBeacon) {
    const blob = new Blob([JSON.stringify(batch)], { type: "application/json" });
    navigator.sendBeacon("/api/v1/analytics/events", blob);
  } else {
    sendTrackingEvents(batch);
  }
}

function scheduleFlush() {
  if (flushTimer) clearTimeout(flushTimer);
  flushTimer = setTimeout(flush, 5000);
}

export function track(eventType: string, eventData: Record<string, unknown> = {}) {
  eventQueue.push({
    event_type: eventType,
    event_data: eventData,
    source_page: window.location.pathname,
    session_id: sessionId!,
  });

  if (eventQueue.length >= 10) {
    flush();
  } else {
    scheduleFlush();
  }
}

export function trackPageView() {
  track("page_view", {
    path: window.location.pathname,
    referrer: document.referrer || "",
    title: document.title,
  });
}

// Flush on page hide
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") flush();
});
window.addEventListener("beforeunload", flush);
