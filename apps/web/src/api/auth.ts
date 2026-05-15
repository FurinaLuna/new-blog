import { http } from "./http";

export async function login(username: string, password: string) {
  const { data } = await http.post<{ access_token: string }>("/auth/login", { username, password });
  return data;
}

export async function changePassword(old_password: string, new_password: string) {
  const { data } = await http.post<{ detail: string }>("/auth/change-password", { old_password, new_password });
  return data;
}
