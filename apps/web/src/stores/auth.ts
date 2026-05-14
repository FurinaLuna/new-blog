import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login as apiLogin } from "@/api/auth";
import { STORAGE_KEY_TOKEN } from "@/utils/constants";

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem(STORAGE_KEY_TOKEN) || "");
  const isLoggedIn = computed(() => !!token.value);

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password);
    token.value = res.access_token;
    localStorage.setItem(STORAGE_KEY_TOKEN, res.access_token);
  }

  function logout() {
    token.value = "";
    localStorage.removeItem(STORAGE_KEY_TOKEN);
  }

  return { token, isLoggedIn, login, logout };
});
