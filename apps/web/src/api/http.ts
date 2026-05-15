import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from "axios";
import { STORAGE_KEY_TOKEN } from "@/utils/constants";
import { useToast } from "@/composables/useToast";

const REFRESH_TOKEN_KEY = "refresh_token";

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token!);
    }
  });
  failedQueue = [];
}

export const http = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(STORAGE_KEY_TOKEN);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const toast = useToast();

    if (error.code === "ERR_CANCELED") {
      return Promise.reject(error);
    }

    if (!error.response) {
      toast.error("网络连接失败，请检查网络");
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

      if (!refreshToken) {
        localStorage.removeItem(STORAGE_KEY_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return http(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await axios.post("/api/v1/auth/refresh", {
          refresh_token: refreshToken,
        });
        const newToken = data.access_token;
        localStorage.setItem(STORAGE_KEY_TOKEN, newToken);
        if (data.refresh_token) {
          localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
        }
        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return http(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem(STORAGE_KEY_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.status === 401 && originalRequest._retry) {
      localStorage.removeItem(STORAGE_KEY_TOKEN);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      window.location.href = "/login";
      return Promise.reject(error);
    }

    const message = error.response?.data?.message || error.response?.data?.detail || "请求失败";
    toast.error(message);

    return Promise.reject(error);
  },
);

export function createRequestWithRetry(config: AxiosRequestConfig, retries = 1) {
  const controller = new AbortController();
  const requestConfig: AxiosRequestConfig = {
    ...config,
    signal: controller.signal,
  };

  const execute = async (attempt = 0): Promise<any> => {
    try {
      const response = await http(requestConfig);
      return response.data;
    } catch (error: any) {
      const isGet = !config.method || config.method.toLowerCase() === "get";
      if (isGet && attempt < retries && error.code !== "ERR_CANCELED") {
        return execute(attempt + 1);
      }
      throw error;
    }
  };

  return {
    execute,
    cancel: () => controller.abort(),
  };
}
