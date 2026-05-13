<script setup lang="ts">
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-12">
    <h1 class="text-2xl font-bold mb-8">关于</h1>

    <div class="prose-custom">
      <p>
        这是用 Vue 3 + FastAPI + PostgreSQL 构建的个人技术博客。
      </p>

      <h2>博客功能</h2>
      <ul>
        <li><strong>文章管理</strong>: Markdown 写作，标签分类，全文搜索</li>
        <li><strong>评论系统</strong>: 支持读者评论和审核</li>
        <li><strong>暗色模式</strong>: 自动跟随系统或手动切换</li>
        <li><strong>RSS 订阅</strong>: 通过 RSS 获取最新文章</li>
        <li><strong>AI 问答</strong>: 基于博客内容的 RAG 智能问答</li>
        <li><strong>数据埋点</strong>: 页面访问、文章阅读统计</li>
      </ul>

      <h2>技术栈</h2>

      <h3>前端</h3>
      <ul>
        <li>Vue 3 + TypeScript</li>
        <li>Vite 构建工具</li>
        <li>Tailwind CSS 极简风格</li>
        <li>Vue Router + Pinia</li>
      </ul>

      <h3>后端</h3>
      <ul>
        <li>FastAPI (Python)</li>
        <li>SQLAlchemy 2.0 (异步)</li>
        <li>PostgreSQL 16 + pgvector</li>
        <li>Redis 7 缓存</li>
      </ul>

      <h3>AI</h3>
      <ul>
        <li>OpenAI Embedding API</li>
        <li>pgvector 向量检索</li>
        <li>RAG 检索增强生成</li>
      </ul>

      <h2>关于作者</h2>
      <p>
        热爱技术与写作的开发者，希望通过博客记录学习和思考的过程。
      </p>

      <h2>联系方式</h2>
      <p>
        可以通过评论功能留言，或在文章下方参与讨论。
      </p>
    </div>
  </div>
</template>
