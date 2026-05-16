import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import PostCard from "@/components/blog/PostCard.vue";
import { createRouter, createMemoryHistory } from "vue-router";

const mockPost = {
  id: "1",
  title: "Test Post Title",
  slug: "test-post",
  excerpt: "This is a test excerpt for the post.",
  cover_image: null,
  published: true,
  featured: false,
  view_count: 42,
  created_at: "2024-06-15T00:00:00Z",
  updated_at: "2024-06-15T00:00:00Z",
  tags: [
    { id: "t1", name: "Vue", slug: "vue" },
    { id: "t2", name: "TypeScript", slug: "typescript" },
  ],
};

const mockFeaturedPost = {
  ...mockPost,
  featured: true,
};

async function mountWithRouter(component: any, props: any) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div/>" } },
      { path: "/post/:slug", component: { template: "<div/>" } },
      { path: "/tag/:slug", component: { template: "<div/>" } },
    ],
  });
  router.push("/");
  await router.isReady();
  return mount(component, {
    props,
    global: {
      plugins: [router],
    },
  });
}

describe("PostCard", () => {
  it("should render post title", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockPost });
    expect(wrapper.text()).toContain("Test Post Title");
  });

  it("should render post excerpt", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockPost });
    expect(wrapper.text()).toContain("This is a test excerpt for the post.");
  });

  it("should render tags", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockPost });
    expect(wrapper.text()).toContain("Vue");
    expect(wrapper.text()).toContain("TypeScript");
  });

  it("should render view count", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockPost });
    expect(wrapper.text()).toContain("42 阅读");
  });

  it("should not show featured badge when not featured", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockPost });
    expect(wrapper.text()).not.toContain("精选");
  });

  it("should show featured badge when featured", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockFeaturedPost });
    expect(wrapper.text()).toContain("精选");
  });

  it("should render date in time element", async () => {
    const wrapper = await mountWithRouter(PostCard, { post: mockPost });
    const timeEl = wrapper.find("time");
    expect(timeEl.exists()).toBe(true);
    expect(timeEl.attributes("datetime")).toBe("2024-06-15T00:00:00Z");
  });
});
