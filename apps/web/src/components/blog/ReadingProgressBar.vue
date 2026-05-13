<script setup lang="ts">
defineProps<{ progress: number }>();
</script>

<template>
  <div class="fixed top-0 left-0 w-full h-1 z-50 bg-transparent">
    <div
      class="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-150 shadow-[0_0_10px_rgba(26,111,250,0.5)]"
      :style="{ width: `${progress}%` }"
    ></div>
  </div>
</template>
