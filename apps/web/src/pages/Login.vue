<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function onSubmit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    const redirect = (route.query.redirect as string) || "/admin/dashboard";
    router.push(redirect);
  } catch {
    error.value = "用户名或密码错误";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto px-4 py-20">
    <h1 class="text-2xl font-bold text-center mb-8">管理员登录</h1>

    <form @submit.prevent="onSubmit" class="space-y-4">
      <div>
        <label for="username" class="block text-sm font-medium mb-1">用户名</label>
        <input
          id="username"
          v-model="username"
          type="text"
          required
          class="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
        />
      </div>
      <div>
        <label for="password" class="block text-sm font-medium mb-1">密码</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          class="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400"
        />
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors font-medium"
      >
        {{ loading ? "登录中..." : "登录" }}
      </button>
    </form>

    <p class="text-center text-sm text-gray-400 mt-6">
      <router-link to="/" class="hover:underline">返回首页</router-link>
    </p>
  </div>
</template>
