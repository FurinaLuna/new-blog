import { ref } from "vue";

export interface Toast {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

const toasts = ref<Toast[]>([]);
let nextId = 0;

export function useToast() {
  function add(message: string, type: Toast["type"] = "info", duration = 3000) {
    const id = nextId++;
    toasts.value.push({ id, message, type });
    if (duration > 0) {
      setTimeout(() => remove(id), duration);
    }
    return id;
  }

  function remove(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  function success(msg: string) { return add(msg, "success"); }
  function error(msg: string) { return add(msg, "error", 5000); }
  function info(msg: string) { return add(msg, "info"); }

  return { toasts, add, remove, success, error, info };
}
