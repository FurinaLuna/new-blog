<script setup lang="ts">
import { ref, computed } from "vue";
import { changePassword } from "@/api/auth";
import { useToast } from "@/composables/useToast";

const toast = useToast();
const oldPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const submitting = ref(false);

const passwordStrength = computed(() => {
  const p = newPassword.value;
  if (!p) return 0;
  let score = 0;
  if (p.length >= 8) score++;
  if (p.length >= 12) score++;
  if (/[a-z]/.test(p) && /[A-Z]/.test(p)) score++;
  if (/\d/.test(p)) score++;
  if (/[^a-zA-Z0-9]/.test(p)) score++;
  return Math.min(score, 4);
});

const strengthLabel = computed(() => {
  const labels = ["", "弱", "较弱", "中等", "强"];
  return labels[passwordStrength.value] || "";
});

const strengthColor = computed(() => {
  const colors = ["", "bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-green-500"];
  return colors[passwordStrength.value] || "";
});

const passwordsMatch = computed(() => {
  if (!confirmPassword.value) return true;
  return newPassword.value === confirmPassword.value;
});

const canSubmit = computed(() => {
  return oldPassword.value && newPassword.value.length >= 8 && passwordsMatch.value;
});

async function onSubmit() {
  if (!canSubmit.value) return;
  submitting.value = true;
  try {
    await changePassword(oldPassword.value, newPassword.value);
    toast.success("密码修改成功");
    oldPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } catch {
    toast.error("密码修改失败，请检查旧密码是否正确");
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold mb-6">修改密码</h1>

    <div class="max-w-md">
      <form @submit.prevent="onSubmit" class="space-y-5">
        <div>
          <label class="block text-sm font-medium mb-1" for="old-password">旧密码</label>
          <input id="old-password" v-model="oldPassword" type="password" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" for="new-password">新密码</label>
          <input id="new-password" v-model="newPassword" type="password" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400" />
          <div v-if="newPassword" class="mt-2">
            <div class="flex gap-1">
              <div v-for="i in 4" :key="i" class="h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                <div v-if="i <= passwordStrength" :class="['h-full rounded-full transition-all', strengthColor]" :style="{ width: '100%' }"></div>
              </div>
            </div>
            <p class="text-xs mt-1" :class="passwordStrength >= 3 ? 'text-green-600' : 'text-gray-400'">密码强度：{{ strengthLabel }}</p>
          </div>
          <p v-if="newPassword && newPassword.length < 8" class="text-xs text-red-500 mt-1">新密码至少8位</p>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" for="confirm-password">确认新密码</label>
          <input id="confirm-password" v-model="confirmPassword" type="password" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-400" />
          <p v-if="!passwordsMatch" class="text-xs text-red-500 mt-1">两次输入的密码不一致</p>
        </div>
        <button type="submit" :disabled="!canSubmit || submitting" class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-30 transition-colors">
          {{ submitting ? '提交中...' : '修改密码' }}
        </button>
      </form>
    </div>
  </div>
</template>
