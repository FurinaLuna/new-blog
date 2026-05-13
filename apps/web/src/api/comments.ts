import { http } from "./http";
import type { Comment } from "@/types";

export async function fetchComments(postId: string) {
  const { data } = await http.get<Comment[]>(`/comments/${postId}`);
  return data;
}

export async function submitComment(comment: { post_id: string; author: string; email?: string; content: string }) {
  const { data } = await http.post<Comment>("/comments", comment);
  return data;
}
