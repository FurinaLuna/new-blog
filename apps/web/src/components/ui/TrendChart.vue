<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useChart } from "@/composables/useChart";

const props = defineProps<{
  labels: string[];
  datasets: Array<{ label: string; data: number[]; color: string }>;
  loading?: boolean;
  title?: string;
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
const { createChart, destroyChart } = useChart();

function buildChart() {
  if (!canvasRef.value || props.loading) return;

  destroyChart();

  const isDark = document.documentElement.classList.contains("dark");

  const chartDatasets = props.datasets.map((ds) => {
    const ctx = canvasRef.value!.getContext("2d")!;
    const gradient = ctx.createLinearGradient(0, 0, 0, 280);
    gradient.addColorStop(0, ds.color + "33");
    gradient.addColorStop(1, ds.color + "00");

    return {
      label: ds.label,
      data: ds.data,
      borderColor: ds.color,
      backgroundColor: gradient,
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 3,
      pointHoverRadius: 6,
      pointBackgroundColor: ds.color,
      pointBorderColor: isDark ? "#1f2937" : "#ffffff",
      pointBorderWidth: 2,
    };
  });

  createChart(
    canvasRef.value,
    "line",
    {
      labels: props.labels,
      datasets: chartDatasets,
    },
    {
      plugins: {
        legend: {
          display: props.datasets.length > 1,
          position: "top",
          align: "end",
          labels: {
            color: isDark ? "#d1d5db" : "#4b5563",
            usePointStyle: true,
            pointStyle: "circle",
            padding: 16,
            font: { size: 12 },
          },
        },
      },
    },
  );
}

onMounted(buildChart);

watch(
  () => [props.labels, props.datasets, props.loading],
  () => buildChart(),
  { deep: true },
);
</script>

<template>
  <div
    class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5"
  >
    <h3
      v-if="title"
      class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4"
    >
      {{ title }}
    </h3>

    <div v-if="loading" class="animate-pulse">
      <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4"></div>
      <div class="h-56 bg-gray-200 dark:bg-gray-700 rounded"></div>
    </div>

    <div v-else class="relative" style="height: 280px">
      <canvas ref="canvasRef"></canvas>
    </div>
  </div>
</template>
