import { http } from "./http";
import type { ChatResponse } from "@/types";

export async function sendChatMessage(question: string, sessionId?: string) {
  const { data } = await http.post<ChatResponse>("/ai/chat", { question, session_id: sessionId });
  return data;
}

export async function* streamChatMessage(question: string, sessionId?: string) {
  const response = await fetch("/api/v1/ai/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
  if (!response.ok) throw new Error("Stream request failed");
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";
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
}
