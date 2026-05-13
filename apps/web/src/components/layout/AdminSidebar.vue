<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const theme = useThemeStore();

function logout() {
  auth.logout();
  router.push("/");
}

const navItems = [
  { path: "/admin/dashboard", label: "仪表板", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm12 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" },
  { path: "/admin/posts", label: "文章管理", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { path: "/admin/media", label: "媒体管理", icon: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" },
  { path: "/admin/comments", label: "评论管理", icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" },
];
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <aside class="w-56 border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 flex-shrink-0 hidden md:flex flex-col">
      <div class="p-4 border-b border-gray-200 dark:border-gray-800">
        <router-link to="/" class="text-lg font-bold">My Blog</router-link>
        <p class="text-xs text-gray-400 mt-0.5">管理后台</p>
      </div>
      <nav class="flex-1 p-3 space-y-1">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors',
            route.path.startsWith(item.path)
              ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
          ]"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
          </svg>
          {{ item.label }}
        </router-link>
      </nav>
      <div class="p-3 border-t border-gray-200 dark:border-gray-800 flex items-center justify-between">
        <button
          @click="theme.toggle()"
          class="p-1.5 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500"
        >
          <svg v-if="!theme.isDark" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
        </button>
        <a href="/" class="text-xs text-gray-400 hover:underline" target="_blank">查看博客</a>
        <button @click="logout" class="text-xs text-red-500 hover:underline">退出</button>
      </div>
    </aside>

    <!-- Mobile header -->
    <div class="flex-1 flex flex-col min-w-0">
      <div class="md:hidden flex items-center justify-between px-4 h-12 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
        <div class="flex items-center gap-3">
          <router-link to="/admin/dashboard" class="text-sm font-bold">后台</router-link>
          <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="text-xs text-gray-500">
            {{ item.label }}
          </router-link>
        </div>
        <button @click="logout" class="text-xs text-red-500">退出</button>
      </div>

      <!-- Page content -->
      <div class="flex-1 p-4 md:p-6 overflow-auto">
        <router-view />
      </div>
    </div>
  </div>
</template>
