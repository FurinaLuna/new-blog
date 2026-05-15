<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";
import { SITE_NAME } from "@/utils/constants";
import ToastContainer from "@/components/ui/ToastContainer.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const theme = useThemeStore();

const collapsed = ref(false);
const mobileDrawerOpen = ref(false);

const breadcrumbLabels: Record<string, string> = {
  dashboard: "仪表板",
  posts: "文章管理",
  new: "新建文章",
  edit: "编辑文章",
  media: "媒体管理",
  comments: "评论管理",
  tags: "标签管理",
  "change-password": "修改密码",
};

const breadcrumbs = computed(() => {
  const crumbs: { label: string; path?: string }[] = [];
  const parts = route.path.split("/").filter(Boolean);
  let accum = "";
  for (let i = 0; i < parts.length; i++) {
    accum += "/" + parts[i];
    const label = i === 0 ? "管理后台" : (breadcrumbLabels[parts[i]] || parts[i]);
    crumbs.push({ label, path: i < parts.length - 1 ? accum : undefined });
  }
  if (crumbs.length > 1 && route.meta.title) {
    crumbs[crumbs.length - 1].label = route.meta.title as string;
  }
  if (crumbs.length === 1) crumbs.shift(); // remove bare "管理后台" on dashboard
  return crumbs;
});

function logout() {
  auth.logout();
  router.push("/");
}

function closeDrawer() {
  mobileDrawerOpen.value = false;
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value;
}

const navItems = [
  { path: "/admin/dashboard", label: "仪表板", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm12 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" },
  { path: "/admin/posts", label: "文章管理", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { path: "/admin/media", label: "媒体管理", icon: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" },
  { path: "/admin/comments", label: "评论管理", icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" },
  { path: "/admin/tags", label: "标签管理", icon: "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" },
  { path: "/admin/change-password", label: "修改密码", icon: "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" },
];

function isActive(path: string) {
  return route.path.startsWith(path);
}

const sidebarWidth = computed(() => collapsed.value ? "w-16" : "w-56");
</script>

<template>
  <div class="min-h-screen flex bg-gray-50 dark:bg-gray-950">
    <!-- Desktop sidebar -->
    <aside
      :class="[
        sidebarWidth,
        'hidden md:flex flex-col border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex-shrink-0 transition-all duration-300',
      ]"
    >
      <!-- Logo area -->
      <div :class="['flex items-center gap-3 border-b border-gray-200 dark:border-gray-800 transition-all duration-300', collapsed ? 'px-3 py-4 justify-center' : 'px-4 py-4']">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shrink-0">
          <span class="text-white font-bold text-sm">Z</span>
        </div>
        <Transition name="fade">
          <div v-if="!collapsed" class="min-w-0 overflow-hidden">
            <router-link to="/" class="text-sm font-semibold whitespace-nowrap">{{ SITE_NAME }}</router-link>
            <p class="text-[10px] text-gray-400 whitespace-nowrap">管理后台</p>
          </div>
        </Transition>
      </div>

      <!-- Nav -->
      <nav :class="['flex-1 py-3 space-y-0.5', collapsed ? 'px-2' : 'px-3']">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 rounded-lg text-sm transition-all duration-200 group relative',
            collapsed ? 'justify-center px-2 py-2.5' : 'px-3 py-2.5',
            isActive(item.path)
              ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
          ]"
          :title="collapsed ? item.label : undefined"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
          </svg>
          <Transition name="fade">
            <span v-if="!collapsed" class="whitespace-nowrap">{{ item.label }}</span>
          </Transition>
        </router-link>
      </nav>

      <!-- Bottom bar -->
      <div :class="['border-t border-gray-200 dark:border-gray-800 transition-all duration-300', collapsed ? 'p-2 flex flex-col items-center gap-2' : 'p-3 flex items-center justify-between']">
        <button
          @click="theme.toggle()"
          class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors"
          aria-label="切换主题"
        >
          <svg v-if="!theme.isDark" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
        </button>
        <template v-if="!collapsed">
          <a href="/" class="text-xs text-gray-400 hover:underline" target="_blank" rel="noopener noreferrer">查看博客</a>
          <button @click="logout" class="text-xs text-red-500 hover:underline">退出</button>
        </template>
        <template v-else>
          <button @click="logout" class="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500 transition-colors" title="退出">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
          </button>
        </template>
      </div>
    </aside>

    <!-- Mobile sidebar drawer overlay -->
    <Teleport to="body">
      <Transition name="drawer-fade">
        <div
          v-if="mobileDrawerOpen"
          class="md:hidden fixed inset-0 z-50"
          @click="closeDrawer"
        >
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
        </div>
      </Transition>
      <Transition name="drawer-slide">
        <div
          v-if="mobileDrawerOpen"
          class="md:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col"
        >
          <div class="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-800">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                <span class="text-white font-bold text-sm">Z</span>
              </div>
              <span class="text-sm font-semibold">{{ SITE_NAME }}</span>
            </div>
            <button @click="closeDrawer" class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800" aria-label="关闭菜单">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <nav class="flex-1 p-3 space-y-0.5">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              @click="closeDrawer"
              :class="[
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                isActive(item.path)
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
              ]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
              </svg>
              {{ item.label }}
            </router-link>
          </nav>
          <div class="p-3 border-t border-gray-200 dark:border-gray-800 flex items-center gap-3">
            <a href="/" class="text-xs text-gray-400 hover:underline" target="_blank" rel="noopener noreferrer" @click="closeDrawer">查看博客</a>
            <button @click="theme.toggle()" class="text-xs text-gray-400 hover:underline">切换主题</button>
            <button @click="logout" class="text-xs text-red-500 hover:underline ml-auto">退出</button>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Main content area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top bar: collapse toggle + breadcrumbs -->
      <header class="h-12 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-center gap-3 px-4 md:px-6 shrink-0">
        <!-- Collapse toggle (desktop) -->
        <button
          @click="toggleCollapsed"
          class="hidden md:flex p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors shrink-0"
          aria-label="折叠侧边栏"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>

        <!-- Mobile menu trigger -->
        <button
          @click="mobileDrawerOpen = true"
          class="md:hidden p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 shrink-0"
          aria-label="菜单"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>

        <!-- Breadcrumbs -->
        <nav class="flex items-center gap-1.5 text-xs min-w-0 overflow-x-auto">
          <template v-for="(crumb, i) in breadcrumbs" :key="i">
            <span v-if="i > 0" class="text-gray-300 dark:text-gray-600 shrink-0">/</span>
            <router-link
              v-if="crumb.path"
              :to="crumb.path"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors whitespace-nowrap"
            >{{ crumb.label }}</router-link>
            <span v-else class="text-gray-700 dark:text-gray-200 font-medium whitespace-nowrap">{{ crumb.label }}</span>
          </template>
        </nav>

        <!-- Right actions (slot for page-level actions) -->
        <div class="ml-auto flex items-center gap-2">
          <slot name="actions" />
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 md:p-6 overflow-auto">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <ToastContainer />
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.3s ease;
}
.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(-100%);
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
