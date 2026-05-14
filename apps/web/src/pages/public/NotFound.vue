<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-24 text-center">
    <h1 class="text-6xl font-bold text-gray-200 dark:text-gray-800 mb-4">404</h1>
    <p class="text-lg text-gray-500 dark:text-gray-400 mb-8">页面不存在</p>
    <button
      @click="router.push('/')"
      class="px-6 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
    >
      返回首页
    </button>
  </div>
</template>
