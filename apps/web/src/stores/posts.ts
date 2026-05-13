import { defineStore } from "pinia";
import { ref } from "vue";
import type { PostListItem } from "@/types";
import { fetchPosts } from "@/api/posts";

export const usePostsStore = defineStore("posts", () => {
  const posts = ref<PostListItem[]>([]);
  const total = ref(0);
  const loading = ref(false);

  async function load(page = 1, size = 10, tag?: string) {
    loading.value = true;
    try {
      const res = await fetchPosts(page, size, tag);
      posts.value = res.items;
      total.value = res.total;
    } finally {
      loading.value = false;
    }
  }

  return { posts, total, loading, load };
});
