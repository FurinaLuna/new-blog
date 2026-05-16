<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ url: string; title: string }>();

const copied = ref(false);
const wechatTooltip = ref(false);

async function copyLink() {
  try {
    await navigator.clipboard.writeText(props.url);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch {}
}

function shareTwitter() {
  const text = encodeURIComponent(props.title);
  const url = encodeURIComponent(props.url);
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank", "noopener,noreferrer");
}
</script>

<template>
  <div class="flex items-center gap-3">
    <span class="text-sm text-gray-500 dark:text-gray-400 mr-1">分享</span>
    <button
      @click="copyLink"
      class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
    >
      <svg v-if="!copied" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
      {{ copied ? '已复制!' : '复制链接' }}
    </button>
    <button
      @click="shareTwitter"
      class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
    >
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      Twitter
    </button>
    <div class="relative">
      <button
        @mouseenter="wechatTooltip = true"
        @mouseleave="wechatTooltip = false"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor"><path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 01.213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 00.167-.054l1.903-1.114a.864.864 0 01.717-.098 10.16 10.16 0 002.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 01-1.162 1.178A1.17 1.17 0 014.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 01-1.162 1.178 1.17 1.17 0 01-1.162-1.178c0-.651.52-1.18 1.162-1.18zm3.68 4.025c-3.837 0-6.953 2.708-6.953 6.048 0 3.342 3.116 6.048 6.953 6.048.778 0 1.533-.118 2.245-.338a.72.72 0 01.586.078l1.465.856a.28.28 0 00.136.045c.131 0 .237-.108.237-.242 0-.058-.023-.115-.038-.172l-.3-1.133a.48.48 0 01.174-.544c1.56-1.128 2.553-2.787 2.553-4.598 0-3.34-3.116-6.048-6.953-6.048h-.105zm-2.556 3.28c.523 0 .947.43.947.963a.955.955 0 01-.947.963.955.955 0 01-.948-.963c0-.532.425-.963.948-.963zm5.11 0c.524 0 .948.43.948.963a.955.955 0 01-.948.963.955.955 0 01-.947-.963c0-.532.423-.963.947-.963z"/></svg>
        微信
      </button>
      <div
        v-if="wechatTooltip"
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 text-xs text-white bg-gray-800 dark:bg-gray-700 rounded-lg whitespace-nowrap"
      >
        请复制链接分享到微信
        <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-800 dark:border-t-gray-700"></div>
      </div>
    </div>
  </div>
</template>
