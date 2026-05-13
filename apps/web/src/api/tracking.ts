import { http } from "./http";
import type { TrackingEvent } from "@/types";

export async function sendTrackingEvents(events: TrackingEvent[]) {
  try {
    await http.post("/analytics/events", events);
  } catch {
    // silently ignore
  }
}
