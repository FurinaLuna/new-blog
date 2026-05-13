<script setup lang="ts">
import { ref, nextTick, computed } from "vue";
import { streamChatMessage } from "@/api/ai";
import { track } from "@/tracking";
import { marked } from "marked";
import type { SourceCitation } from "@/types";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
}

const isOpen = ref(false);
const question = ref("");
const messages = ref<Message[]>([]);
const loading = ref(false);
const sessionId = ref<string | undefined>();
const chatBody = ref<HTMLElement | null>(null);

const suggestedQuestions = [
  "博客主要写什么内容？",
  "如何联系博主？",
  "有哪些关于前端开发的文章？",
  "AI 在这个博客中扮演什么角色？"
];

function toggle() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    track("ai_chat_open", {});
    nextTick(() => scrollToEnd());
  }
}

function scrollToEnd() {
  if (chatBody.value) {
    chatBody.value.scrollTo({
      top: chatBody.value.scrollHeight,
      behavior: "smooth"
    });
  }
}

async function askSuggested(q: string) {
  question.value = q;
  await send();
}

async function send() {
  const q = question.value.trim();
  if (!q || loading.value) return;

  messages.value.push({ role: "user", content: q });
  question.value = "";
  loading.value = true;

  const assistantMessageIndex = messages.value.length;
  messages.value.push({ role: "assistant", content: "" });

  nextTick(() => scrollToEnd());

  try {
    const stream = streamChatMessage(q, sessionId.value);
    for await (const chunk of stream) {
      messages.value[assistantMessageIndex].content += chunk.token;
      sessionId.value = chunk.session_id;
      // Throttled scroll
      if (chatBody.value && chatBody.value.scrollHeight - chatBody.value.scrollTop < 1000) {
        scrollToEnd();
      }
    }
    
    track("ai_chat_message_stream", {
      question_length: q.length,
      answer_length: messages.value[assistantMessageIndex].content.length
    });
  } catch (error) {
    console.error(error);
    messages.value[assistantMessageIndex].content = "抱歉，连接 AI 服务时出现错误。请稍后再试。";
  } finally {
    loading.value = false;
    scrollToEnd();
  }
}

function renderMarkdown(text: string) {
  return marked.parse(text);
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
  // Could add a toast here
}
</script>

<template>
  <!-- Floating Button with Glow -->
  <button
    @click="toggle"
    class="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-[0_8px_30px_rgb(26,111,250,0.4)] hover:scale-110 active:scale-95 transition-all duration-300 flex items-center justify-center group"
    :aria-label="isOpen ? '关闭AI助手' : '打开AI助手'"
  >
    <div class="absolute inset-0 rounded-2xl bg-primary-400 blur-lg opacity-0 group-hover:opacity-40 transition-opacity"></div>
    <svg v-if="!isOpen" xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
    </svg>
  </button>

  <!-- Chat Panel with Glassmorphism -->
  <Transition name="chat-panel">
    <div
      v-if="isOpen"
      class="fixed bottom-24 right-8 z-50 w-[400px] max-w-[calc(100vw-4rem)] h-[600px] max-h-[calc(100vh-140px)] bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.15)] border border-white/20 dark:border-gray-800/50 flex flex-col overflow-hidden"
    >
      <!-- Header -->
      <div class="p-6 pb-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gradient-to-r from-transparent to-primary-50/30 dark:to-primary-900/10">
        <div>
          <h3 class="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-primary-400">AI Note Assistant</h3>
          <p class="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Powered by Blog Context</p>
        </div>
        <div class="flex gap-1">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
        </div>
      </div>

      <!-- Chat Area -->
      <div ref="chatBody" class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        <!-- Initial State -->
        <div v-if="messages.length === 0" class="space-y-6 py-4">
          <div class="bg-primary-50 dark:bg-primary-900/20 p-5 rounded-2xl border border-primary-100 dark:border-primary-800/50">
            <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              你好！我是博客的智能助手。我可以帮你快速查找文章内容、总结技术要点或回答相关疑问。
            </p>
          </div>
          
          <div class="space-y-3">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest pl-1">你可以这样问我</p>
            <div class="grid gap-2">
              <button
                v-for="q in suggestedQuestions"
                :key="q"
                @click="askSuggested(q)"
                class="text-left p-3 text-sm rounded-xl border border-gray-100 dark:border-gray-800 hover:border-primary-300 dark:hover:border-primary-700 hover:bg-white dark:hover:bg-gray-800 transition-all group"
              >
                <span class="text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">{{ q }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Message Bubbles -->
        <div v-for="(msg, idx) in messages" :key="idx" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start animate-fade-in']">
          <div
            :class="[
              'max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm',
              msg.role === 'user'
                ? 'bg-primary-600 text-white rounded-br-none'
                : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-none border border-gray-100 dark:border-gray-700',
            ]"
          >
            <div 
              v-if="msg.role === 'assistant'" 
              class="prose-ai dark:prose-invert max-w-none" 
              v-html="renderMarkdown(msg.content || '...')"
            ></div>
            <div v-else class="whitespace-pre-wrap">{{ msg.content }}</div>
            
            <div v-if="msg.role === 'assistant' && msg.content" class="mt-3 pt-3 border-t border-gray-50 dark:border-gray-700 flex justify-between items-center">
              <button @click="copyToClipboard(msg.content)" class="text-[10px] text-gray-400 hover:text-primary-500 flex items-center gap-1 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                复制回答
              </button>
              <div v-if="msg.sources?.length" class="flex gap-2">
                 <!-- Could add source links here -->
              </div>
            </div>
          </div>
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="loading && messages[messages.length-1].content === ''" class="flex justify-start">
          <div class="bg-white dark:bg-gray-800 rounded-2xl rounded-bl-none px-4 py-3 border border-gray-100 dark:border-gray-700 shadow-sm">
            <div class="flex gap-1.5">
              <div class="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce"></div>
              <div class="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
              <div class="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Bar -->
      <div class="p-6 bg-gradient-to-t from-white dark:from-gray-900 to-transparent">
        <form @submit.prevent="send" class="relative group">
          <input
            v-model="question"
            type="text"
            placeholder="输入您的问题..."
            class="w-full pl-4 pr-12 py-4 bg-gray-50 dark:bg-gray-800 border-none rounded-2xl text-sm focus:ring-2 focus:ring-primary-500/50 dark:text-white transition-all shadow-inner"
            :disabled="loading"
          />
          <button
            type="submit"
            :disabled="loading || !question.trim()"
            class="absolute right-2 top-2 bottom-2 px-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-30 disabled:hover:bg-primary-600 transition-all flex items-center justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </form>
        <p class="text-center text-[10px] text-gray-400 mt-4">AI 可能会产生错误，请核实重要信息</p>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.05);
  border-radius: 10px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.05);
}

.chat-panel-enter-active,
.chat-panel-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.chat-panel-enter-from,
.chat-panel-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
  filter: blur(10px);
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.prose-ai) {
  line-height: 1.6;
}
:deep(.prose-ai p) {
  margin: 0.5rem 0;
}
:deep(.prose-ai ul, .prose-ai ol) {
  padding-left: 1.25rem;
  margin: 0.5rem 0;
}
:deep(.prose-ai code) {
  font-family: inherit;
  background: rgba(0,0,0,0.05);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
}
.dark :deep(.prose-ai code) {
  background: rgba(255,255,255,0.1);
}
</style>
