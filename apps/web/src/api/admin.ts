import { http } from "./http";
import type {
  PaginatedResponse,
  PostListItem,
  Comment,
  AnalyticsOverview,
  AnalyticsTrend,
  RealtimeStats,
  Tag,
  MediaItem,
  AdminPostListItem,
  PostCreate,
  PostUpdate,
  TagCreatePayload,
  TagUpdatePayload,
  BatchActionPayload,
} from "@/types";

export async function adminFetchPosts(
  page = 1,
  size = 20,
  search?: string,
): Promise<PaginatedResponse<AdminPostListItem>> {
  const { data } = await http.get<PaginatedResponse<AdminPostListItem>>("/admin/posts", {
    params: { page, size, search },
  });
  return data;
}

export async function adminCreatePost(post: PostCreate): Promise<PostListItem> {
  const { data } = await http.post<PostListItem>("/admin/posts", post);
  return data;
}

export async function adminUpdatePost(id: string, post: PostUpdate): Promise<PostListItem> {
  const { data } = await http.put<PostListItem>(`/admin/posts/${id}`, post);
  return data;
}

export async function adminDeletePost(id: string): Promise<void> {
  await http.delete(`/admin/posts/${id}`);
}

export async function adminReindexPost(id: string): Promise<{ indexed_chunks: number }> {
  const { data } = await http.post<{ indexed_chunks: number }>(`/admin/posts/${id}/reindex`);
  return data;
}

export async function adminUploadMedia(file: File): Promise<MediaItem> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await http.post<MediaItem>("/admin/media/upload", form);
  return data;
}

export async function adminFetchMedia(
  page = 1,
  size = 20,
): Promise<PaginatedResponse<MediaItem>> {
  const { data } = await http.get<PaginatedResponse<MediaItem>>("/admin/media", {
    params: { page, size },
  });
  return data;
}

export async function adminDeleteMedia(id: string): Promise<void> {
  await http.delete(`/admin/media/${id}`);
}

export async function adminBatchPublishPosts(
  ids: string[],
): Promise<{ updated: number }> {
  const { data } = await http.post<{ updated: number }>("/admin/posts/batch-publish", { ids });
  return data;
}

export async function adminBatchUnpublishPosts(
  ids: string[],
): Promise<{ updated: number }> {
  const { data } = await http.post<{ updated: number }>("/admin/posts/batch-unpublish", { ids });
  return data;
}

export async function adminFetchComments(
  status?: string,
  page?: number,
): Promise<PaginatedResponse<Comment>> {
  const { data } = await http.get<PaginatedResponse<Comment>>("/admin/comments", {
    params: { status, page },
  });
  return data;
}

export async function adminReplyComment(
  commentId: string,
  content: string,
): Promise<Comment> {
  const { data } = await http.post<Comment>(`/admin/comments/${commentId}/reply`, { content });
  return data;
}

export async function adminFetchPendingComments(page = 1): Promise<Comment[]> {
  const { data } = await http.get<Comment[]>("/admin/comments/pending", { params: { page } });
  return data;
}

export async function adminApproveComment(id: string): Promise<Comment> {
  const { data } = await http.put<Comment>(`/admin/comments/${id}/approve`);
  return data;
}

export async function adminDeleteComment(id: string): Promise<void> {
  await http.delete(`/admin/comments/${id}`);
}

export async function adminBatchApproveComments(
  payload: BatchActionPayload,
): Promise<{ approved: Comment[]; count: number }> {
  const { data } = await http.post<{ approved: Comment[]; count: number }>(
    "/admin/comments/batch-approve",
    payload,
  );
  return data;
}

export async function adminBatchDeleteComments(
  payload: BatchActionPayload,
): Promise<{ deleted: number }> {
  const { data } = await http.post<{ deleted: number }>("/admin/comments/batch-delete", payload);
  return data;
}

export async function adminFetchTags(): Promise<Tag[]> {
  const { data } = await http.get<Tag[]>("/admin/tags");
  return data;
}

export async function adminCreateTag(tag: TagCreatePayload): Promise<Tag> {
  const { data } = await http.post<Tag>("/admin/tags", tag);
  return data;
}

export async function adminUpdateTag(id: string, tag: TagUpdatePayload): Promise<Tag> {
  const { data } = await http.put<Tag>(`/admin/tags/${id}`, tag);
  return data;
}

export async function adminDeleteTag(id: string): Promise<void> {
  await http.delete(`/admin/tags/${id}`);
}

export async function adminFetchAnalyticsOverview(): Promise<AnalyticsOverview> {
  const { data } = await http.get<AnalyticsOverview>("/admin/analytics/overview");
  return data;
}

export async function adminFetchPostStats(): Promise<
  { title: string; slug: string; view_count: number }[]
> {
  const { data } = await http.get<{ title: string; slug: string; view_count: number }[]>(
    "/admin/analytics/posts",
  );
  return data;
}

export async function adminFetchAnalyticsTrend(
  metric: string,
  days: number,
): Promise<AnalyticsTrend> {
  const { data } = await http.get<AnalyticsTrend>("/admin/analytics/trend", {
    params: { metric, days },
  });
  return data;
}

export async function adminFetchRealtimeStats(): Promise<RealtimeStats> {
  const { data } = await http.get<RealtimeStats>("/admin/analytics/realtime");
  return data;
}
