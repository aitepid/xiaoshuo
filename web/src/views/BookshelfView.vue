<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import EmptyState from '@/components/EmptyState.vue'
import SkeletonBlock from '@/components/SkeletonBlock.vue'
import { getErrorMessage } from '@/lib/error'
import http from '@/lib/http'
import { useFeedbackStore } from '@/stores/feedback'

interface BookshelfItem {
  id: number
  novel: number
  novel_title: string
  last_read_chapter: number | null
  reading_progress: number
  updated_at: string
}

const router = useRouter()
const feedbackStore = useFeedbackStore()

const loading = ref(false)
const busy = ref(false)
const errorText = ref('')
const items = ref<BookshelfItem[]>([])

const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
})

async function fetchBookshelf(): Promise<void> {
  loading.value = true
  errorText.value = ''
  try {
    const { data } = await http.get<{ results: BookshelfItem[] }>('/bookshelf')
    items.value = data.results || []
  } catch (error) {
    errorText.value = getErrorMessage(error, '书架加载失败。')
  } finally {
    loading.value = false
  }
}

async function removeItem(id: number): Promise<void> {
  busy.value = true
  try {
    await http.delete(`/bookshelf/${id}`)
    items.value = items.value.filter((item) => item.id !== id)
    feedbackStore.pushToast('success', '已从书架移除')
  } catch (error) {
    feedbackStore.pushToast('error', '移除失败', getErrorMessage(error))
  } finally {
    busy.value = false
  }
}

async function continueReading(item: BookshelfItem): Promise<void> {
  let chapterId = item.last_read_chapter || 0

  if (!chapterId) {
    try {
      const { data } = await http.get<{ results: Array<{ id: number }> }>(`/novels/${item.novel}/chapters`)
      chapterId = data.results?.[0]?.id || 0
    } catch {
      chapterId = 0
    }
  }

  if (!chapterId) {
    feedbackStore.pushToast('info', '暂无可读章节')
    return
  }

  await router.push({
    name: 'reader',
    params: {
      novelId: item.novel,
      chapterId,
    },
  })
}

async function goDetail(item: BookshelfItem): Promise<void> {
  await router.push({
    name: 'novel-detail',
    params: {
      id: item.novel,
    },
  })
}

async function goDiscover(): Promise<void> {
  await router.push('/')
}

onMounted(() => {
  void fetchBookshelf()
})
</script>

<template>
  <section class="space-y-4">
    <header class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">我的书架</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-300">云端同步阅读进度，跨端无缝续读。</p>
      </div>
      <button class="btn-secondary" type="button" :disabled="loading" @click="fetchBookshelf">{{ loading ? '刷新中...' : '刷新' }}</button>
    </header>

    <div v-if="loading" class="grid gap-3">
      <SkeletonBlock height="86px" rounded="14px" />
      <SkeletonBlock height="86px" rounded="14px" />
      <SkeletonBlock height="86px" rounded="14px" />
    </div>

    <EmptyState
      v-else-if="errorText"
      title="书架加载失败"
      :description="errorText"
      action-text="重试"
      @retry="fetchBookshelf"
    />

    <EmptyState
      v-else-if="!sortedItems.length"
      title="书架还是空的"
      description="去书城挑一本到书架，阅读进度会自动云同步。"
      action-text="前往书城"
      @retry="goDiscover"
    />

    <ul v-else class="grid gap-3">
      <li
        v-for="item in sortedItems"
        :key="item.id"
        class="rounded-2xl border border-black/10 bg-white/70 p-4 backdrop-blur transition hover:-translate-y-0.5 dark:border-white/10 dark:bg-white/5"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">{{ item.novel_title }}</h2>
          <span class="text-xs text-slate-500 dark:text-slate-300">阅读进度 {{ Math.round(item.reading_progress) }}%</span>
        </div>

        <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <div class="h-full rounded-full bg-amber-600 transition-all duration-500" :style="{ width: `${Math.max(0, Math.min(100, item.reading_progress))}%` }" />
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <button class="btn-primary" type="button" :disabled="busy" @click="continueReading(item)">继续阅读</button>
          <button class="btn-secondary" type="button" :disabled="busy" @click="goDetail(item)">书籍详情</button>
          <button class="btn-secondary" type="button" :disabled="busy" @click="removeItem(item.id)">移出书架</button>
        </div>
      </li>
    </ul>
  </section>
</template>
