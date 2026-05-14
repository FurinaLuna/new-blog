import { http } from "./http";
import { STORAGE_KEY_TOKEN } from "@/utils/constants";
import type { ChatResponse } from "@/types";

export async function sendChatMessage(question: string, sessionId?: string) {
  const { data } = await http.post<ChatResponse>("/ai/chat", { question, session_id: sessionId });
  return data;
}

export async function* streamChatMessage(question: string, sessionId?: string) {
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const controller = new AbortController();
  const response = await fetch("/api/v1/ai/chat/stream", {
    method: "POST",
    headers,
    body: JSON.stringify({ question, session_id: sessionId }),
    signal: controller.signal,
  });
  if (!response.ok) throw new Error("Stream request failed");
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") return;
          yield JSON.parse(data);
        }
      }
    }
  } finally {
    controller.abort();
  }
}
