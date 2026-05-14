import axios from "axios";
import { STORAGE_KEY_TOKEN } from "@/utils/constants";

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
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(STORAGE_KEY_TOKEN);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);
