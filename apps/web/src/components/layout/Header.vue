<script setup lang="ts">
import { ref } from "vue";
import { useThemeStore } from "@/stores/theme";
import { useRouter } from "vue-router";
import { SITE_NAME } from "@/utils/constants";

const theme = useThemeStore();
const router = useRouter();
const searchQuery = ref("");
const mobileMenuOpen = ref(false);

function onSearch() {
  const q = searchQuery.value.trim();
  if (q) {
    router.push({ name: "search", query: { q } });
    searchQuery.value = "";
  }
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value;
}
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b border-gray-100 dark:border-gray-800 bg-white/70 dark:bg-gray-950/70 backdrop-blur-xl transition-all duration-300"
  >
    <nav class="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-2 group">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg shadow-primary-500/20 group-hover:rotate-12 transition-transform duration-300">
           <span class="text-white font-bold text-lg">Z</span>
        </div>
        <span class="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400">
          {{ SITE_NAME }}
        </span>
      </router-link>

      <!-- Desktop nav -->
      <div class="hidden md:flex items-center gap-8 text-sm font-medium">
        <router-link 
          v-for="link in [
            { name: '首页', path: '/' },
            { name: '标签', path: '/tags' },
            { name: '关于', path: '/about' }
          ]" 
          :key="link.path"
          :to="link.path" 
          class="relative py-1 text-gray-500 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400 transition-colors group"
        >
          {{ link.name }}
          <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-primary-500 transition-all duration-300 group-[.router-link-active]:w-full"></span>
        </router-link>

        <div class="h-4 w-[1px] bg-gray-200 dark:bg-gray-800"></div>

        <form @submit.prevent="onSearch" class="relative group">
          <input
            v-model="searchQuery"
            type="search"
            placeholder="搜索..."
            class="w-32 focus:w-48 px-4 py-1.5 text-xs rounded-full border border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-300"
          />
        </form>
        
        <button
          @click="theme.toggle()"
          class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-all active:scale-90"
        >
          <svg v-if="!theme.isDark" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
        </button>
      </div>

      <!-- Mobile controls -->
      <div class="flex md:hidden items-center gap-2">
        <button @click="theme.toggle()" class="p-2">
           <svg v-if="!theme.isDark" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
           <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
        </button>
        <button @click="toggleMobileMenu" class="p-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>
    </nav>

    <!-- Mobile menu -->
    <Transition name="mobile-menu">
      <div v-if="mobileMenuOpen" @keydown.escape="mobileMenuOpen = false" class="md:hidden border-t border-gray-100 dark:border-gray-800 bg-white/90 dark:bg-gray-950/90 backdrop-blur-xl px-6 py-6 space-y-4">
        <form @submit.prevent="onSearch">
          <input
            v-model="searchQuery"
            type="search"
            placeholder="搜索文章..."
            class="w-full px-4 py-3 text-sm rounded-2xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </form>
        <div class="flex flex-col gap-2">
          <router-link @click="mobileMenuOpen=false" to="/" class="px-4 py-2 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">首页</router-link>
          <router-link @click="mobileMenuOpen=false" to="/tags" class="px-4 py-2 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">标签</router-link>
          <router-link @click="mobileMenuOpen=false" to="/about" class="px-4 py-2 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">关于</router-link>
        </div>
      </div>
    </Transition>
  </header>
</template>

<style scoped>
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.3s ease;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
