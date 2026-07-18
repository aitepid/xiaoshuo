<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import EmptyState from '@/components/EmptyState.vue'
import SkeletonBlock from '@/components/SkeletonBlock.vue'
import { getErrorMessage } from '@/lib/error'
import http from '@/lib/http'
import { useAuthStore } from '@/stores/auth'
import { useFeedbackStore } from '@/stores/feedback'

interface NovelDetail {
  id: number
  title: string
  cover_url: string
  summary: string
  category: string
  status: string
  word_count: number
  updated_at: string
  tags: Array<{ id: number; name: string }>
}

interface ChapterMeta {
  id: number
  chapter_number: number
  title: string
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const feedbackStore = useFeedbackStore()

const novelId = computed(() => Number(route.params.id || 0))
const loading = ref(true)
const loadingAction = ref(false)
const errorText = ref('')
const novel = ref<NovelDetail | null>(null)
const chapters = ref<ChapterMeta[]>([])

async function fetchDetail(): Promise<void> {
  if (!novelId.value) {
    return
  }

  loading.value = true
  errorText.value = ''

  try {
    const [detailRes, chapterRes] = await Promise.all([
      http.get<NovelDetail>(`/novels/${novelId.value}`),
      http.get<{ results: ChapterMeta[] }>(`/novels/${novelId.value}/chapters`),
    ])

    novel.value = detailRes.data
    chapters.value = chapterRes.data.results || []
  } catch (error) {
    errorText.value = getErrorMessage(error, '书籍详情加载失败。')
  } finally {
    loading.value = false
  }
}

async function addToBookshelf(): Promise<void> {
  if (!authStore.isAuthenticated) {
    await router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  if (!novel.value) {
    return
  }

  loadingAction.value = true
  try {
    await http.post('/bookshelf', { novel: novel.value.id })
    feedbackStore.pushToast('success', '已加入书架')
  } catch (error) {
    feedbackStore.pushToast('error', '加入书架失败', getErrorMessage(error))
  } finally {
    loadingAction.value = false
  }
}

async function startReading(): Promise<void> {
  if (!chapters.value.length) {
    feedbackStore.pushToast('info', '暂无可读章节')
    return
  }

  await router.push({
    name: 'reader',
    params: {
      novelId: novelId.value,
      chapterId: chapters.value[0].id,
    },
  })
}

onMounted(() => {
  void fetchDetail()
})
</script>

<template>
  <section class="space-y-5">
    <div v-if="loading" class="rounded-3xl border border-black/10 bg-white/70 p-6 backdrop-blur dark:border-white/10 dark:bg-white/5">
      <SkeletonBlock height="30px" rounded="14px" />
      <div class="mt-4 grid gap-5 md:grid-cols-[220px_1fr]">
        <SkeletonBlock height="280px" rounded="16px" />
        <div class="space-y-3">
          <SkeletonBlock height="18px" />
          <SkeletonBlock height="18px" />
          <SkeletonBlock height="18px" />
        </div>
      </div>
    </div>

    <EmptyState
      v-else-if="errorText"
      title="加载失败"
      :description="errorText"
      action-text="重新加载"
      @retry="fetchDetail"
    />

    <template v-else-if="novel">
      <section class="rounded-3xl border border-black/10 bg-white/70 p-6 backdrop-blur dark:border-white/10 dark:bg-white/5">
        <div class="grid gap-6 md:grid-cols-[220px_1fr]">
          <div class="overflow-hidden rounded-2xl border border-black/10 bg-slate-100 dark:border-white/10 dark:bg-slate-900">
            <img
              v-if="novel.cover_url"
              :src="novel.cover_url"
              :alt="novel.title"
              class="h-full w-full object-cover"
            />
            <div v-else class="flex h-[300px] items-center justify-center text-sm text-slate-400">暂无封面</div>
          </div>

          <div>
            <h1 class="text-3xl font-semibold text-slate-900 dark:text-slate-100">{{ novel.title }}</h1>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-300">{{ novel.category }} · {{ novel.word_count }} 字 · {{ novel.status }}</p>
            <p class="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-700 dark:text-slate-200">{{ novel.summary || '暂无简介。' }}</p>

            <div class="mt-5 flex flex-wrap gap-2">
              <span
                v-for="tag in novel.tags"
                :key="tag.id"
                class="rounded-full border border-black/10 bg-white/70 px-3 py-1 text-xs dark:border-white/10 dark:bg-white/10"
              >
                {{ tag.name }}
              </span>
            </div>

            <div class="mt-6 flex flex-wrap gap-3">
              <button class="btn-primary" type="button" :disabled="loadingAction" @click="startReading">立即阅读</button>
              <button class="btn-secondary" type="button" :disabled="loadingAction" @click="addToBookshelf">
                {{ loadingAction ? '处理中...' : '加入书架' }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-2xl border border-black/10 bg-white/70 p-5 backdrop-blur dark:border-white/10 dark:bg-white/5">
        <h2 class="mb-4 text-xl font-semibold">目录</h2>

        <EmptyState
          v-if="!chapters.length"
          title="暂无目录"
          description="章节可能还在审核中，稍后再来看看。"
          compact
        />

        <ul v-else class="grid gap-2">
          <li v-for="chapter in chapters" :key="chapter.id" class="rounded-xl border border-black/10 bg-white/60 px-4 py-3 text-sm dark:border-white/10 dark:bg-white/5">
            第 {{ chapter.chapter_number }} 章 · {{ chapter.title }}
          </li>
        </ul>
      </section>
    </template>
  </section>
</template>
