<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import EmptyState from '@/components/EmptyState.vue'
import SkeletonBlock from '@/components/SkeletonBlock.vue'
import { getErrorMessage } from '@/lib/error'
import http from '@/lib/http'
import { toRelativeApiPath } from '@/lib/pagination'

interface NovelCard {
  id: number
  title: string
  cover_url: string
  summary: string
  category: string
  word_count: number
  status: string
  author_name: string
}

interface NovelPage {
  results: NovelCard[]
  next: string | null
}

const loading = ref(false)
const loadingMore = ref(false)
const errorText = ref('')
const novels = ref<NovelCard[]>([])
const nextPath = ref('/novels')
const listSentinel = ref<HTMLElement | null>(null)

let observer: IntersectionObserver | null = null

async function fetchNovels(reset = false): Promise<void> {
  if (reset) {
    loading.value = true
    errorText.value = ''
    novels.value = []
    nextPath.value = '/novels'
  } else {
    loadingMore.value = true
  }

  try {
    const { data } = await http.get<NovelPage>(nextPath.value)
    novels.value = [...novels.value, ...(data.results || [])]
    nextPath.value = toRelativeApiPath(data.next)
  } catch (error) {
    errorText.value = getErrorMessage(error, '小说列表加载失败。')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function observeBottom(): void {
  if (!listSentinel.value) {
    return
  }

  observer = new IntersectionObserver(
    (entries) => {
      const first = entries[0]
      if (!first?.isIntersecting || !nextPath.value || loadingMore.value || loading.value) {
        return
      }
      void fetchNovels(false)
    },
    {
      root: null,
      rootMargin: '100px',
      threshold: 0.1,
    },
  )

  observer.observe(listSentinel.value)
}

onMounted(() => {
  void fetchNovels(true)
  observeBottom()
})

onBeforeUnmount(() => {
  if (observer && listSentinel.value) {
    observer.unobserve(listSentinel.value)
    observer.disconnect()
  }
})
</script>

<template>
  <section class="space-y-6">
    <div class="rounded-3xl border border-black/10 bg-white/70 p-6 shadow-sm backdrop-blur md:p-10 dark:border-white/10 dark:bg-white/5">
      <p class="text-sm font-semibold uppercase tracking-[0.24em] text-amber-700 dark:text-amber-300">commercial-ready foundation</p>
      <h1 class="mt-3 text-3xl font-semibold leading-tight text-slate-900 md:text-5xl dark:text-slate-100">
        晨昏书局 H5 / Web
      </h1>
      <p class="mt-4 max-w-2xl text-sm leading-7 text-slate-600 md:text-base dark:text-slate-300">
        当前已完成阶段 1：路由守卫、Token 自动刷新、Pinia 状态层、Tailwind 主题系统与页面切换骨架。
      </p>
    </div>
    <div v-if="loading" class="grid gap-4 md:grid-cols-3">
      <div class="card-panel space-y-3" v-for="idx in 3" :key="idx">
        <SkeletonBlock height="18px" rounded="12px" />
        <SkeletonBlock height="14px" />
        <SkeletonBlock height="14px" />
      </div>
    </div>

    <EmptyState
      v-else-if="errorText"
      title="网络开小差了"
      :description="errorText"
      action-text="重新加载"
      @retry="fetchNovels(true)"
    />

    <EmptyState
      v-else-if="!novels.length"
      title="书城暂时空荡"
      description="当前没有可展示的书籍，可能正在审核上架。"
      action-text="刷新列表"
      @retry="fetchNovels(true)"
    />

    <div v-else class="grid gap-4 md:grid-cols-3">
      <article class="card-panel">
        <h2 class="card-title">极致响应速度</h2>
        <p class="card-copy">请求层统一拦截、超时处理、401 自动续签，保障用户在网络抖动下仍可继续阅读。</p>
      </article>
      <article class="card-panel">
        <h2 class="card-title">丝滑交互底座</h2>
        <p class="card-copy">全局主题已支持系统跟随和手动切换，后续组件统一继承过渡曲线。</p>
      </article>
      <article class="card-panel">
        <h2 class="card-title">高容错架构</h2>
        <p class="card-copy">路由级鉴权与会话恢复已就绪，为书架、创作中心和阅读器做安全兜底。</p>
      </article>

      <RouterLink
        v-for="novel in novels"
        :key="novel.id"
        :to="`/novels/${novel.id}`"
        class="card-panel block transition hover:-translate-y-0.5"
      >
        <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100">{{ novel.title }}</h3>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-300">{{ novel.category }} · {{ novel.word_count }} 字 · {{ novel.author_name }}</p>
        <p class="mt-3 line-clamp-3 text-sm leading-6 text-slate-700 dark:text-slate-200">{{ novel.summary || '暂无简介。' }}</p>
      </RouterLink>
    </div>

    <div class="rounded-2xl border border-black/10 bg-white/75 p-4 text-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
      <p class="mb-3 text-slate-700 dark:text-slate-200">阶段 3 阅读器已接入：支持字体/行高/背景自定义、滚动进度记忆、触底续读与下一章预加载。</p>
      <RouterLink class="btn-primary inline-flex items-center" to="/reader/1">进入样例阅读器</RouterLink>
    </div>

    <div ref="listSentinel" class="h-2" />

    <div v-if="loadingMore" class="grid gap-3 md:grid-cols-3">
      <SkeletonBlock height="70px" rounded="14px" />
      <SkeletonBlock height="70px" rounded="14px" />
      <SkeletonBlock height="70px" rounded="14px" />
    </div>
  </section>
</template>
