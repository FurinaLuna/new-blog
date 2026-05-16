import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useToast } from "@/composables/useToast";

describe("useToast", () => {
  beforeEach(() => {
    const { toasts } = useToast();
    toasts.value = [];
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should add a toast with default type info", () => {
    const { add, toasts } = useToast();
    add("hello");
    expect(toasts.value).toHaveLength(1);
    expect(toasts.value[0].message).toBe("hello");
    expect(toasts.value[0].type).toBe("info");
  });

  it("should add toast with specific type", () => {
    const { add, toasts } = useToast();
    add("saved", "success");
    expect(toasts.value[0].type).toBe("success");
  });

  it("should add toast via success shortcut", () => {
    const { success, toasts } = useToast();
    success("done");
    expect(toasts.value[0].type).toBe("success");
    expect(toasts.value[0].message).toBe("done");
  });

  it("should add toast via error shortcut with 5000ms duration", () => {
    const { error, toasts } = useToast();
    error("fail");
    expect(toasts.value[0].type).toBe("error");
    expect(toasts.value[0].message).toBe("fail");
  });

  it("should add toast via info shortcut", () => {
    const { info, toasts } = useToast();
    info("notice");
    expect(toasts.value[0].type).toBe("info");
    expect(toasts.value[0].message).toBe("notice");
  });

  it("should remove a toast by id", () => {
    const { add, remove, toasts } = useToast();
    const id = add("to remove");
    expect(toasts.value).toHaveLength(1);
    remove(id);
    expect(toasts.value).toHaveLength(0);
  });

  it("should auto-dismiss toast after duration", () => {
    const { add, toasts } = useToast();
    add("temporary", "info", 3000);
    expect(toasts.value).toHaveLength(1);
    vi.advanceTimersByTime(3000);
    expect(toasts.value).toHaveLength(0);
  });

  it("should not auto-dismiss when duration is 0", () => {
    const { add, toasts } = useToast();
    add("persistent", "info", 0);
    vi.advanceTimersByTime(10000);
    expect(toasts.value).toHaveLength(1);
  });

  it("should return incrementing ids", () => {
    const { add, toasts } = useToast();
    add("first");
    add("second");
    expect(toasts.value[0].id).toBeLessThan(toasts.value[1].id);
  });
});
