import { http } from "./http";

export async function login(username: string, password: string) {
  const { data } = await http.post<{ access_token: string }>("/auth/login", { username, password });
  return data;
}
