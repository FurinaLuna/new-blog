<script setup lang="ts">
defineProps<{
  icon?: string;
  message: string;
  linkTo?: string;
  linkText?: string;
}>();
</script>

<template>
  <div class="text-center py-20">
    <div v-if="icon" class="text-6xl mb-6">{{ icon }}</div>
    <p class="text-xl font-medium text-gray-500 mb-6">{{ message }}</p>
    <router-link
      v-if="linkTo"
      :to="linkTo"
      class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-500/20"
    >
      {{ linkText || "返回首页" }}
    </router-link>
  </div>
</template>
