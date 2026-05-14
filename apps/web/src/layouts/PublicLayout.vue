<script setup lang="ts">
import Header from "@/components/layout/Header.vue";
import Footer from "@/components/layout/Footer.vue";
import AiChat from "@/components/ai/AiChat.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <Header />
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Footer />
    <AiChat />
    <ToastContainer />
    <ConfirmDialog />
  </div>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
