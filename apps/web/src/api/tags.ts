import { http } from "./http";
import type { Tag, PaginatedResponse, PostListItem } from "@/types";

export async function fetchTags() {
  const { data } = await http.get<Tag[]>("/tags");
  return data;
}

export async function fetchPostsByTag(slug: string, page = 1, size = 10) {
  const { data } = await http.get<PaginatedResponse<PostListItem>>(`/tags/${slug}/posts`, { params: { page, size } });
  return data;
}
