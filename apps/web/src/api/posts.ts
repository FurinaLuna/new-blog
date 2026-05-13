import { http } from "./http";
import type { PaginatedResponse, PostListItem, PostDetail } from "@/types";

export async function fetchPosts(page = 1, size = 10, tag?: string) {
  const { data } = await http.get<PaginatedResponse<PostListItem>>("/posts", { params: { page, size, tag } });
  return data;
}

export async function searchPosts(q: string, page = 1, size = 10) {
  const { data } = await http.get<PaginatedResponse<PostListItem>>("/posts/search", { params: { q, page, size } });
  return data;
}

export async function fetchPost(slug: string) {
  const { data } = await http.get<PostDetail>(`/posts/${slug}`);
  return data;
}

export async function fetchPostSummary(slug: string) {
  const { data } = await http.get<{ slug: string; summary: string }>(`/posts/${slug}/summary`);
  return data;
}
