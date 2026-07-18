<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import SkeletonBlock from '@/components/SkeletonBlock.vue'
import { getErrorMessage } from '@/lib/error'
import http from '@/lib/http'
import { useAuthStore } from '@/stores/auth'
import { useFeedbackStore } from '@/stores/feedback'
import { useReaderStore } from '@/stores/reader'
import type { ChapterDetail, ChapterMeta } from '@/types/reader'

type BookShelfItem = {
  id: number
  novel: number
}

interface ChapterListResponse {
  results: ChapterMeta[]
  next: string | null
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const readerStore = useReaderStore()
const feedbackStore = useFeedbackStore()

const novelId = computed(() => String(route.params.novelId || ''))
const preferredChapterId = computed(() => Number(route.params.chapterId || 0))

const loading = ref(true)
const loadingMore = ref(false)
const panelOpen = ref(false)
const chapterList = ref<ChapterMeta[]>([])
const renderedChapters = ref<ChapterDetail[]>([])
const chapterCache = reactive<Record<number, ChapterDetail>>({})
const sectionHost = ref<HTMLElement | null>(null)
const bottomSentinel = ref<HTMLElement | null>(null)

let bottomObserver: IntersectionObserver | null = null
let lastFocusedChapterId = 0
let syncTimer: number | null = null
let bookshelfItemId: number | null = null

const hasNextChapter = computed(() => {
  const last = renderedChapters.value[renderedChapters.value.length - 1]
  return getNextChapterId(last?.id || 0) !== null
})

const readerStyle = computed(() => ({
  fontSize: `${readerStore.settings.fontSize}px`,
  lineHeight: String(readerStore.settings.lineHeight),
}))

const progressLabel = computed(() => {
  if (!chapterList.value.length || !lastFocusedChapterId) {
    return '0%'
  }

  const idx = chapterList.value.findIndex((item) => item.id === lastFocusedChapterId)
  if (idx < 0) {
    return '0%'
  }

  const percent = Math.min(100, Math.max(0, Math.round(((idx + 1) / chapterList.value.length) * 100)))
  return `${percent}%`
})

function getNextChapterId(chapterId: number): number | null {
  const idx = chapterList.value.findIndex((item) => item.id === chapterId)
  if (idx < 0 || idx >= chapterList.value.length - 1) {
    return null
  }
  return chapterList.value[idx + 1].id
}

function getPrevChapterId(chapterId: number): number | null {
  const idx = chapterList.value.findIndex((item) => item.id === chapterId)
  if (idx <= 0) {
    return null
  }
  return chapterList.value[idx - 1].id
}

async function fetchChapterList(): Promise<void> {
  const all: ChapterMeta[] = []
  let endpoint = `/novels/${novelId.value}/chapters`

  while (endpoint) {
    const { data } = await http.get<ChapterListResponse>(endpoint)
    all.push(...(data.results || []))

    if (!data.next) {
      endpoint = ''
      continue
    }

    const marker = '/api/v1/'
    const idx = data.next.indexOf(marker)
    endpoint = idx >= 0 ? data.next.slice(idx + marker.length - 1) : ''
  }

  chapterList.value = all
}

async function fetchChapterDetail(chapterId: number): Promise<ChapterDetail> {
  if (chapterCache[chapterId]) {
    return chapterCache[chapterId]
  }

  const { data } = await http.get<ChapterDetail>(`/novels/${novelId.value}/chapters/${chapterId}`)
  chapterCache[chapterId] = data
  return data
}

async function preloadNextChapter(currentChapterId: number): Promise<void> {
  const nextId = getNextChapterId(currentChapterId)
  if (!nextId || chapterCache[nextId]) {
    return
  }

  try {
    await fetchChapterDetail(nextId)
  } catch {
    // Ignore preload failure and retry on demand.
  }
}

async function appendChapter(chapterId: number): Promise<void> {
  if (!chapterId || renderedChapters.value.some((item) => item.id === chapterId)) {
    return
  }

  loadingMore.value = true
  try {
    const chapter = await fetchChapterDetail(chapterId)
    renderedChapters.value.push(chapter)
    lastFocusedChapterId = chapter.id
    await preloadNextChapter(chapter.id)
  } finally {
    loadingMore.value = false
  }
}

async function appendNextChapter(): Promise<void> {
  const last = renderedChapters.value[renderedChapters.value.length - 1]
  const nextId = getNextChapterId(last?.id || 0)
  if (!nextId) {
    return
  }
  await appendChapter(nextId)
}

function detectFocusedChapter(): number {
  const host = sectionHost.value
  if (!host) {
    return lastFocusedChapterId
  }

  const sections = host.querySelectorAll<HTMLElement>('[data-chapter-id]')
  let focused = lastFocusedChapterId
  for (const section of sections) {
    const top = section.getBoundingClientRect().top
    if (top <= window.innerHeight * 0.35) {
      focused = Number(section.dataset.chapterId || focused)
    }
  }
  return focused
}

async function ensureBookshelfItem(): Promise<number | null> {
  if (!authStore.isAuthenticated) {
    return null
  }

  if (bookshelfItemId) {
    return bookshelfItemId
  }

  const { data } = await http.get<{ results: BookShelfItem[] }>('/bookshelf')
  const list = data.results || []
  const found = list.find((item) => item.novel === Number(novelId.value))

  if (found) {
    bookshelfItemId = found.id
    return bookshelfItemId
  }

  const created = await http.post<BookShelfItem>('/bookshelf', { novel: Number(novelId.value) })
  bookshelfItemId = created.data.id
  return bookshelfItemId
}

function scheduleBackendSync(chapterId: number): void {
  if (!authStore.isAuthenticated) {
    return
  }

  if (syncTimer) {
    window.clearTimeout(syncTimer)
  }

  syncTimer = window.setTimeout(() => {
    const runner = async () => {
      try {
        const itemId = await ensureBookshelfItem()
        if (!itemId) {
          return
        }

        const index = chapterList.value.findIndex((item) => item.id === chapterId)
        const progress = index < 0 ? 0 : Math.round(((index + 1) / Math.max(chapterList.value.length, 1)) * 100)

        await http.post(`/bookshelf/${itemId}/sync-progress`, {
          last_read_chapter: chapterId,
          reading_progress: progress,
        })
      } catch {
        // Silent sync failure; local progress still retained.
      }
    }

    const idle = (window as Window & { requestIdleCallback?: (cb: () => void) => number }).requestIdleCallback
    if (idle) {
      idle(() => {
        void runner()
      })
    } else {
      window.setTimeout(() => {
        void runner()
      }, 16)
    }
  }, 800)
}

function persistProgress(scrollTop: number): void {
  const focused = detectFocusedChapter() || renderedChapters.value[0]?.id || 0
  lastFocusedChapterId = focused

  if (!focused) {
    return
  }

  readerStore.saveProgress(novelId.value, {
    chapterId: focused,
    scrollTop,
    updatedAt: Date.now(),
  })

  scheduleBackendSync(focused)
}

function handleScroll(): void {
  persistProgress(window.scrollY)
}

function setBottomObserver(): void {
  if (!bottomSentinel.value) {
    return
  }

  bottomObserver = new IntersectionObserver(
    (entries) => {
      const first = entries[0]
      if (first?.isIntersecting) {
        void appendNextChapter()
      }
    },
    {
      root: null,
      threshold: 0.1,
      rootMargin: '120px',
    },
  )

  bottomObserver.observe(bottomSentinel.value)
}

async function jumpToChapter(chapterId: number): Promise<void> {
  if (!chapterId) {
    return
  }

  renderedChapters.value = []
  await appendChapter(chapterId)
  await nextTick()
  window.scrollTo({ top: 0, behavior: 'smooth' })
  void router.replace({ name: 'reader', params: { novelId: novelId.value, chapterId } })
}

async function initReader(): Promise<void> {
  loading.value = true
  try {
    await fetchChapterList()

    if (!chapterList.value.length) {
      feedbackStore.pushToast('info', '当前暂无可读章节', '等待章节审核通过后将自动展示。')
      return
    }

    const localProgress = readerStore.getProgress(novelId.value)
    const startChapter =
      preferredChapterId.value ||
      localProgress?.chapterId ||
      chapterList.value[0].id

    await appendChapter(startChapter)

    await nextTick()
    if (localProgress?.scrollTop) {
      window.scrollTo({ top: localProgress.scrollTop })
    }

    setBottomObserver()
  } catch (error) {
    feedbackStore.pushToast('error', '阅读器加载失败', getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void initReader()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onBeforeUnmount(() => {
  if (bottomObserver && bottomSentinel.value) {
    bottomObserver.unobserve(bottomSentinel.value)
    bottomObserver.disconnect()
  }

  if (syncTimer) {
    window.clearTimeout(syncTimer)
  }

  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <section class="space-y-4">
    <header class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">沉浸式阅读器</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-300">进度 {{ progressLabel }} · 触底自动续读 · 空闲同步云端</p>
      </div>
      <div class="flex items-center gap-2">
        <button class="nav-chip" type="button" @click="panelOpen = !panelOpen">阅读设置</button>
      </div>
    </header>

    <aside v-if="panelOpen" class="rounded-2xl border border-black/10 bg-white/75 p-4 text-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
      <div class="grid gap-4 md:grid-cols-3">
        <label class="space-y-2">
          <span>字体大小 {{ readerStore.settings.fontSize }}px</span>
          <input
            type="range"
            min="14"
            max="32"
            :value="readerStore.settings.fontSize"
            @input="readerStore.setFontSize(Number(($event.target as HTMLInputElement).value))"
            class="w-full"
          />
        </label>

        <label class="space-y-2">
          <span>行高 {{ readerStore.settings.lineHeight.toFixed(2) }}</span>
          <input
            type="range"
            min="1.4"
            max="2.6"
            step="0.05"
            :value="readerStore.settings.lineHeight"
            @input="readerStore.setLineHeight(Number(($event.target as HTMLInputElement).value))"
            class="w-full"
          />
        </label>

        <div class="space-y-2">
          <span>阅读背景</span>
          <div class="flex flex-wrap gap-2">
            <button class="nav-chip" type="button" @click="readerStore.setBackground('paper')">羊皮纸</button>
            <button class="nav-chip" type="button" @click="readerStore.setBackground('light')">白底</button>
            <button class="nav-chip" type="button" @click="readerStore.setBackground('mint')">绿豆沙</button>
          </div>
        </div>
      </div>
    </aside>

    <div
      ref="sectionHost"
      class="reader-shell rounded-3xl border border-black/10 p-5 shadow-sm transition-colors duration-500 md:p-8"
      :class="readerStore.themeClass"
      :style="readerStyle"
    >
      <template v-if="loading">
        <div class="space-y-3">
          <SkeletonBlock height="22px" rounded="14px" />
          <SkeletonBlock height="22px" rounded="14px" />
          <SkeletonBlock height="22px" rounded="14px" />
          <SkeletonBlock height="22px" rounded="14px" />
        </div>
      </template>

      <template v-else-if="!chapterList.length">
        <div class="rounded-2xl border border-dashed border-black/15 bg-white/45 p-8 text-center text-sm text-slate-600 dark:border-white/20 dark:bg-white/5 dark:text-slate-300">
          当前书籍暂无已发布章节，暂时无法阅读。
        </div>
      </template>

      <template v-else>
        <article
          v-for="chapter in renderedChapters"
          :key="chapter.id"
          :data-chapter-id="chapter.id"
          class="mb-10 border-b border-black/8 pb-8 last:mb-0 last:border-none"
        >
          <h2 class="mb-2 text-2xl font-semibold tracking-wide">第 {{ chapter.chapter_number }} 章 · {{ chapter.title }}</h2>
          <p class="mb-6 text-sm opacity-70">{{ chapter.volume_title }} · {{ chapter.word_count }} 字</p>
          <div class="space-y-5 whitespace-pre-wrap text-[1em] tracking-[0.01em]">
            {{ chapter.content }}
          </div>
        </article>

        <div class="mb-5 flex flex-wrap items-center justify-between gap-2">
          <button
            class="btn-secondary"
            type="button"
            :disabled="!getPrevChapterId(renderedChapters[0]?.id || 0)"
            @click="jumpToChapter(getPrevChapterId(renderedChapters[0]?.id || 0) || 0)"
          >
            上一章
          </button>

          <button class="btn-primary" type="button" :disabled="!hasNextChapter" @click="appendNextChapter">
            {{ hasNextChapter ? '继续阅读下一章' : '已读完本书' }}
          </button>
        </div>
      </template>

      <div ref="bottomSentinel" class="h-2" />

      <div v-if="loadingMore" class="mt-4 space-y-2">
        <SkeletonBlock height="18px" rounded="10px" />
        <SkeletonBlock height="18px" rounded="10px" />
      </div>
    </div>
  </section>
</template>
