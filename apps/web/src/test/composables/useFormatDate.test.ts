import { describe, it, expect } from "vitest";
import { useFormatDate } from "@/composables/useFormatDate";

describe("useFormatDate", () => {
  it("should format a valid ISO date string", () => {
    const { formatDate } = useFormatDate();
    const result = formatDate("2024-01-15T00:00:00Z");
    expect(result).toBeTruthy();
    expect(typeof result).toBe("string");
  });

  it("should format date with zh-CN locale", () => {
    const { formatDate } = useFormatDate();
    const result = formatDate("2024-06-01T00:00:00Z");
    expect(result).toContain("2024");
  });

  it("should handle date-only string", () => {
    const { formatDate } = useFormatDate();
    const result = formatDate("2024-12-25");
    expect(result).toContain("2024");
  });

  it("should return formatted string for various dates", () => {
    const { formatDate } = useFormatDate();
    const result1 = formatDate("2023-03-10T08:30:00Z");
    const result2 = formatDate("2025-11-20T16:45:00Z");
    expect(result1).not.toBe(result2);
  });

  it("should handle date with time component", () => {
    const { formatDate } = useFormatDate();
    const result = formatDate("2024-07-04T12:30:45.123Z");
    expect(result).toBeTruthy();
  });
});
