<script setup lang="ts">
import { useConfirm } from "@/composables/useConfirm";

const { state, onConfirm, onCancel } = useConfirm();
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div v-if="state.message" class="fixed inset-0 z-[200] flex items-center justify-center" @click.self="onCancel">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 max-w-sm w-full mx-4">
          <p class="text-sm text-gray-700 dark:text-gray-300 mb-6">{{ state.message }}</p>
          <div class="flex justify-end gap-3">
            <button @click="onCancel" class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400">取消</button>
            <button @click="onConfirm" class="px-4 py-2 text-sm rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-400">确定</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.confirm-enter-active { transition: all 0.2s ease; }
.confirm-leave-active { transition: all 0.15s ease; }
.confirm-enter-from { opacity: 0; }
.confirm-enter-from > :last-child { transform: scale(0.95); }
.confirm-leave-to { opacity: 0; }
</style>
