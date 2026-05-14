import { ref } from "vue";

interface ConfirmState {
  message: string;
  resolve: ((value: boolean) => void) | null;
}

const state = ref<ConfirmState>({ message: "", resolve: null });

export function useConfirm() {
  function confirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      state.value = { message, resolve };
    });
  }

  function onConfirm() {
    state.value.resolve?.(true);
    state.value = { message: "", resolve: null };
  }

  function onCancel() {
    state.value.resolve?.(false);
    state.value = { message: "", resolve: null };
  }

  return { state, confirm, onConfirm, onCancel };
}
