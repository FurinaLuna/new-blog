import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { usePostsStore } from "@/stores/posts";

vi.mock("@/api/posts", () => ({
  fetchPosts: vi.fn(),
}));

import { fetchPosts } from "@/api/posts";

const mockPosts = [
  {
    id: "1",
    title: "Test Post",
    slug: "test-post",
    excerpt: "An excerpt",
    cover_image: null,
    published: true,
    featured: false,
    view_count: 10,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    tags: [],
  },
];

describe("usePostsStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("should start with empty posts and loading false", () => {
    const store = usePostsStore();
    expect(store.posts).toHaveLength(0);
    expect(store.total).toBe(0);
    expect(store.loading).toBe(false);
  });

  it("should load posts and set loading state", async () => {
    vi.mocked(fetchPosts).mockResolvedValue({
      items: mockPosts,
      total: 1,
      page: 1,
      size: 10,
      pages: 1,
    });
    const store = usePostsStore();
    const promise = store.load();
    expect(store.loading).toBe(true);
    await promise;
    expect(store.posts).toHaveLength(1);
    expect(store.posts[0].title).toBe("Test Post");
    expect(store.total).toBe(1);
    expect(store.loading).toBe(false);
  });

  it("should set loading to false even on error", async () => {
    vi.mocked(fetchPosts).mockRejectedValue(new Error("Network error"));
    const store = usePostsStore();
    await expect(store.load()).rejects.toThrow("Network error");
    expect(store.loading).toBe(false);
  });

  it("should pass page, size, and tag params to fetchPosts", async () => {
    vi.mocked(fetchPosts).mockResolvedValue({
      items: [],
      total: 0,
      page: 2,
      size: 5,
      pages: 0,
    });
    const store = usePostsStore();
    await store.load(2, 5, "vue");
    expect(fetchPosts).toHaveBeenCalledWith(2, 5, "vue");
  });
});
