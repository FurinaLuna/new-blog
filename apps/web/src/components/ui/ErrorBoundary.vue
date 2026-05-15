<script setup lang="ts">
import { ref, onErrorCaptured } from "vue";

const hasError = ref(false);
const errorMessage = ref("");

onErrorCaptured((err) => {
  hasError.value = true;
  errorMessage.value = err.message || "组件渲染出错";
  return false;
});

function retry() {
  hasError.value = false;
  errorMessage.value = "";
}
</script>

<template>
  <div v-if="hasError" class="text-center py-20">
    <div class="text-6xl mb-6">⚠️</div>
    <p class="text-xl font-medium text-gray-500 mb-6">{{ errorMessage }}</p>
    <button
      @click="retry"
      class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-500/20"
    >
      重试
    </button>
  </div>
  <slot v-else />
</template>
