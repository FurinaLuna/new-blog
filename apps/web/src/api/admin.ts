import { http } from "./http";
import type { PaginatedResponse, PostListItem, Comment, AnalyticsOverview } from "@/types";

// Posts
export async function adminFetchPosts(page = 1, size = 20, search?: string) {
  const { data } = await http.get<PaginatedResponse<PostListItem>>("/admin/posts", { params: { page, size, search } });
  return data;
}

export async function adminCreatePost(post: Record<string, unknown>) {
  const { data } = await http.post<PostListItem>("/admin/posts", post);
  return data;
}

export async function adminUpdatePost(id: string, post: Record<string, unknown>) {
  const { data } = await http.put<PostListItem>(`/admin/posts/${id}`, post);
  return data;
}

export async function adminDeletePost(id: string) {
  await http.delete(`/admin/posts/${id}`);
}

export async function adminReindexPost(id: string) {
  const { data } = await http.post<{ indexed_chunks: number }>(`/admin/posts/${id}/reindex`);
  return data;
}

// Media
export async function adminUploadMedia(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await http.post("/admin/media/upload", form);
  return data;
}

export async function adminFetchMedia(page = 1, size = 20) {
  const { data } = await http.get("/admin/media", { params: { page, size } });
  return data;
}

export async function adminDeleteMedia(id: string) {
  await http.delete(`/admin/media/${id}`);
}

// Comments
export async function adminFetchPendingComments(page = 1) {
  const { data } = await http.get<Comment[]>("/admin/comments/pending", { params: { page } });
  return data;
}

export async function adminApproveComment(id: string) {
  const { data } = await http.put<Comment>(`/admin/comments/${id}/approve`);
  return data;
}

export async function adminDeleteComment(id: string) {
  await http.delete(`/admin/comments/${id}`);
}

// Analytics
export async function adminFetchAnalyticsOverview() {
  const { data } = await http.get<AnalyticsOverview>("/admin/analytics/overview");
  return data;
}

export async function adminFetchPostStats() {
  const { data } = await http.get<{ title: string; slug: string; view_count: number }[]>("/admin/analytics/posts");
  return data;
}
