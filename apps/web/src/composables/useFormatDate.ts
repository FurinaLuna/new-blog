export function useFormatDate() {
  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }
  return { formatDate };
}
