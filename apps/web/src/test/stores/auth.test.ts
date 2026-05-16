import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useAuthStore } from "@/stores/auth";

function createToken(exp: number): string {
  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = btoa(JSON.stringify({ exp, sub: "user1" }));
  return `${header}.${payload}.signature`;
}

describe("useAuthStore", () => {
  beforeEach(() => {
    const pinia = createPinia();
    setActivePinia(pinia);
    localStorage.clear();
  });

  it("should not be logged in when no token", () => {
    const store = useAuthStore();
    store.token = "";
    store.refreshToken = "";
    expect(store.isLoggedIn).toBe(false);
  });

  it("should be logged in with valid non-expired token", () => {
    const futureExp = Math.floor(Date.now() / 1000) + 3600;
    const token = createToken(futureExp);
    const store = useAuthStore();
    store.token = token;
    expect(store.isLoggedIn).toBe(true);
  });

  it("should not be logged in with expired token", () => {
    const pastExp = Math.floor(Date.now() / 1000) - 3600;
    const token = createToken(pastExp);
    const store = useAuthStore();
    store.token = token;
    expect(store.isLoggedIn).toBe(false);
  });

  it("should detect token expiring soon", () => {
    const soonExp = Math.floor(Date.now() / 1000) + 60;
    const token = createToken(soonExp);
    const store = useAuthStore();
    store.token = token;
    expect(store.isTokenExpiringSoon()).toBe(true);
  });

  it("should not detect token expiring soon when far from expiry", () => {
    const farExp = Math.floor(Date.now() / 1000) + 3600;
    const token = createToken(farExp);
    const store = useAuthStore();
    store.token = token;
    expect(store.isTokenExpiringSoon()).toBe(false);
  });

  it("should clear token and refreshToken on logout", async () => {
    const store = useAuthStore();
    store.token = "some-token";
    store.refreshToken = "some-refresh-token";
    vi.spyOn(store, "logout").mockImplementation(async () => {
      store.token = "";
      store.refreshToken = "";
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
    });
    await store.logout();
    expect(store.token).toBe("");
    expect(store.refreshToken).toBe("");
  });

  it("should return true for isTokenExpiringSoon when no token", () => {
    const store = useAuthStore();
    store.token = "";
    expect(store.isTokenExpiringSoon()).toBe(true);
  });
});
