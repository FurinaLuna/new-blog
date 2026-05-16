import { ref, onUnmounted, shallowRef } from "vue";
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

export function useChart() {
  const chartInstance = shallowRef<Chart | null>(null);

  function createChart(
    canvasRef: HTMLCanvasElement,
    type: "line" | "bar" | "doughnut",
    data: Chart["data"],
    options?: Chart["options"],
  ) {
    if (chartInstance.value) {
      chartInstance.value.destroy();
    }

    const isDark = document.documentElement.classList.contains("dark");
    const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
    const tickColor = isDark ? "rgba(255,255,255,0.5)" : "rgba(0,0,0,0.5)";

    const defaultOptions: Chart["options"] = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: isDark ? "#1f2937" : "#fff",
          titleColor: isDark ? "#f9fafb" : "#111827",
          bodyColor: isDark ? "#d1d5db" : "#4b5563",
          borderColor: isDark ? "#374151" : "#e5e7eb",
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
        },
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: tickColor, font: { size: 11 } },
          border: { display: false },
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: tickColor, font: { size: 11 } },
          border: { display: false },
          beginAtZero: true,
        },
      },
    };

    const mergedOptions = {
      ...defaultOptions,
      ...options,
      scales: {
        ...defaultOptions.scales,
        ...options?.scales,
      },
      plugins: {
        ...defaultOptions.plugins,
        ...options?.plugins,
      },
    };

    chartInstance.value = new Chart(canvasRef, {
      type,
      data,
      options: mergedOptions,
    });

    return chartInstance.value;
  }

  function destroyChart() {
    if (chartInstance.value) {
      chartInstance.value.destroy();
      chartInstance.value = null;
    }
  }

  onUnmounted(destroyChart);

  return {
    chartInstance,
    createChart,
    destroyChart,
  };
}
