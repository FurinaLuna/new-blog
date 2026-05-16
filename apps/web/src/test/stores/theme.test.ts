import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { nextTick } from "vue";
import { useThemeStore } from "@/stores/theme";

describe("useThemeStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    document.documentElement.classList.remove("dark");
  });

  it("should initialize with light theme when localStorage is empty and prefers-color-scheme is light", () => {
    const store = useThemeStore();
    expect(store.isDark).toBe(false);
  });

  it("should toggle theme from light to dark", async () => {
    const store = useThemeStore();
    expect(store.isDark).toBe(false);
    store.toggle();
    await nextTick();
    expect(store.isDark).toBe(true);
  });

  it("should toggle theme from dark back to light", async () => {
    const store = useThemeStore();
    store.toggle();
    await nextTick();
    store.toggle();
    await nextTick();
    expect(store.isDark).toBe(false);
  });

  it("should persist theme to localStorage on toggle", async () => {
    const store = useThemeStore();
    store.toggle();
    await nextTick();
    expect(localStorage.setItem).toHaveBeenCalledWith("theme", "dark");
  });

  it("should add dark class to document element when dark", async () => {
    const store = useThemeStore();
    store.toggle();
    await nextTick();
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("should remove dark class from document element when light", async () => {
    const store = useThemeStore();
    store.toggle();
    await nextTick();
    store.toggle();
    await nextTick();
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("should initialize as dark when localStorage has dark theme", () => {
    localStorage.getItem = vi.fn((key: string) => {
      if (key === "theme") return "dark";
      return null;
    });
    const store = useThemeStore();
    expect(store.isDark).toBe(true);
  });
});
