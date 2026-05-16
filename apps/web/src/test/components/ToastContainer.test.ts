import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import ToastContainer from "@/components/ui/ToastContainer.vue";
import { useToast } from "@/composables/useToast";

describe("ToastContainer", () => {
  beforeEach(() => {
    const { toasts } = useToast();
    toasts.value = [];
  });

  it("should render no toasts when empty", () => {
    const wrapper = mount(ToastContainer, {
      global: {
        stubs: { Teleport: true, TransitionGroup: false },
      },
    });
    const toastItems = wrapper.findAll("[class*='pointer-events-auto']");
    expect(toastItems.length).toBe(0);
  });

  it("should render toast message when added", () => {
    const { add } = useToast();
    add("Hello World", "success");
    const wrapper = mount(ToastContainer, {
      global: {
        stubs: { Teleport: true, TransitionGroup: false },
      },
    });
    expect(wrapper.text()).toContain("Hello World");
  });

  it("should render multiple toasts", () => {
    const { add } = useToast();
    add("First", "info");
    add("Second", "error");
    const wrapper = mount(ToastContainer, {
      global: {
        stubs: { Teleport: true, TransitionGroup: false },
      },
    });
    expect(wrapper.text()).toContain("First");
    expect(wrapper.text()).toContain("Second");
  });

  it("should remove toast when close button is clicked", async () => {
    const { add } = useToast();
    add("Removable", "info");
    const wrapper = mount(ToastContainer, {
      global: {
        stubs: { Teleport: true, TransitionGroup: false },
      },
    });
    const buttons = wrapper.findAll("button");
    expect(buttons.length).toBe(1);
    await buttons[0].trigger("click");
    const { toasts } = useToast();
    expect(toasts.value).toHaveLength(0);
  });
});
