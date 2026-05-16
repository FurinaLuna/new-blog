import { describe, it, expect, vi, beforeEach } from "vitest";
import { http } from "@/api/http";

describe("http client", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("should create axios instance with correct baseURL", () => {
    expect(http.defaults.baseURL).toBe("/api/v1");
  });

  it("should create axios instance with correct timeout", () => {
    expect(http.defaults.timeout).toBe(30000);
  });

  it("should have request interceptor configured", () => {
    expect(http.interceptors.request.handlers?.length).toBeGreaterThan(0);
  });

  it("should have response interceptor configured", () => {
    expect(http.interceptors.response.handlers?.length).toBeGreaterThan(0);
  });

  it("should add Authorization header when token exists in localStorage", () => {
    localStorage.setItem("token", "test-jwt-token");
    const handler = http.interceptors.request.handlers?.[0];
    const config = { headers: { Authorization: "" } } as any;
    const result = handler!.fulfilled(config) as any;
    expect(result.headers.Authorization).toBe("Bearer test-jwt-token");
  });

  it("should not add Authorization header when no token", () => {
    const handler = http.interceptors.request.handlers?.[0];
    const config = { headers: { Authorization: "" } } as any;
    const result = handler!.fulfilled(config) as any;
    expect(result.headers.Authorization).toBe("");
  });
});
