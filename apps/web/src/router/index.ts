import { createRouter, createWebHistory } from "vue-router";
import { trackPageView } from "@/tracking";
import { STORAGE_KEY_TOKEN, SITE_NAME } from "@/utils/constants";

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    return { top: 0 };
  },
  routes: [
    {
      path: "/",
      component: () => import("@/layouts/PublicLayout.vue"),
      children: [
        {
          path: "",
          name: "home",
          component: () => import("@/pages/public/Home.vue"),
          meta: { title: "首页" },
        },
        {
          path: "post/:slug",
          name: "post",
          component: () => import("@/pages/public/Post.vue"),
          meta: { title: "文章" },
        },
        {
          path: "tags",
          name: "tags",
          component: () => import("@/pages/public/Tags.vue"),
          meta: { title: "标签" },
        },
        {
          path: "tag/:slug",
          name: "tag",
          component: () => import("@/pages/public/TagPosts.vue"),
          meta: { title: "标签文章" },
        },
        {
          path: "search",
          name: "search",
          component: () => import("@/pages/public/Search.vue"),
          meta: { title: "搜索" },
        },
        {
          path: "about",
          name: "about",
          component: () => import("@/pages/public/About.vue"),
          meta: { title: "关于" },
        },
      ],
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/pages/Login.vue"),
      meta: { title: "登录" },
    },
    {
      path: "/admin",
      component: () => import("@/layouts/AdminLayout.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          redirect: "/admin/dashboard",
        },
        {
          path: "dashboard",
          name: "dashboard",
          component: () => import("@/pages/admin/Dashboard.vue"),
          meta: { title: "仪表板" },
        },
        {
          path: "posts",
          name: "admin-posts",
          component: () => import("@/pages/admin/PostList.vue"),
          meta: { title: "文章管理" },
        },
        {
          path: "posts/new",
          name: "admin-post-new",
          component: () => import("@/pages/admin/PostEditor.vue"),
          meta: { title: "新建文章" },
        },
        {
          path: "posts/:slug/edit",
          name: "admin-post-edit",
          component: () => import("@/pages/admin/PostEditor.vue"),
          meta: { title: "编辑文章" },
        },
        {
          path: "media",
          name: "admin-media",
          component: () => import("@/pages/admin/MediaManager.vue"),
          meta: { title: "媒体管理" },
        },
        {
          path: "comments",
          name: "admin-comments",
          component: () => import("@/pages/admin/CommentList.vue"),
          meta: { title: "评论管理" },
        },
      ],
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("@/pages/public/NotFound.vue"),
      meta: { title: "404" },
    },
  ],
});

router.afterEach((to) => {
  const title = to.meta.title ? `${to.meta.title} — ${SITE_NAME}` : SITE_NAME;
  document.title = title;
  trackPageView();
});

router.beforeEach((to, from, next) => {
  if (to.matched.some((r) => r.meta.requiresAuth)) {
    const token = localStorage.getItem(STORAGE_KEY_TOKEN);
    if (!token) {
      next({ name: "login", query: { redirect: to.fullPath } });
      return;
    }
  }
  next();
});

router.onError((error) => {
  console.error("Router error:", error);
});

export default router;
