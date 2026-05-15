import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login as apiLogin } from "@/api/auth";
import { http } from "@/api/http";
import { STORAGE_KEY_TOKEN } from "@/utils/constants";

const REFRESH_TOKEN_KEY = "refresh_token";

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem(STORAGE_KEY_TOKEN) || "");
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || "");
  const isLoggedIn = computed(() => !!token.value && !isTokenExpired(token.value));

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password);
    token.value = res.access_token;
    localStorage.setItem(STORAGE_KEY_TOKEN, res.access_token);
    if ((res as any).refresh_token) {
      refreshToken.value = (res as any).refresh_token;
      localStorage.setItem(REFRESH_TOKEN_KEY, (res as any).refresh_token);
    }
  }

  async function refreshAccessToken(): Promise<string | null> {
    const rt = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!rt) return null;
    try {
      const { data } = await http.post("/auth/refresh", { refresh_token: rt });
      token.value = data.access_token;
      localStorage.setItem(STORAGE_KEY_TOKEN, data.access_token);
      if (data.refresh_token) {
        refreshToken.value = data.refresh_token;
        localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
      }
      return data.access_token;
    } catch {
      return null;
    }
  }

  async function logout() {
    try {
      const rt = localStorage.getItem(REFRESH_TOKEN_KEY);
      await http.post("/auth/logout", { refresh_token: rt || undefined });
    } catch {}
    token.value = "";
    refreshToken.value = "";
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  function isTokenExpiringSoon(): boolean {
    if (!token.value) return true;
    try {
      const payload = JSON.parse(atob(token.value.split(".")[1]));
      return payload.exp * 1000 - Date.now() < 5 * 60 * 1000;
    } catch {
      return true;
    }
  }

  return { token, refreshToken, isLoggedIn, login, refreshAccessToken, logout, isTokenExpiringSoon };
});
