import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

type ReaderBackground = 'paper' | 'light' | 'mint'

interface ReaderSettings {
  fontSize: number
  lineHeight: number
  background: ReaderBackground
}

interface ReaderProgress {
  chapterId: number
  scrollTop: number
  updatedAt: number
}

const SETTINGS_KEY = 'xs_reader_settings'
const PROGRESS_KEY = 'xs_reader_progress'

const DEFAULT_SETTINGS: ReaderSettings = {
  fontSize: 19,
  lineHeight: 1.95,
  background: 'paper',
}

function readJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) {
      return fallback
    }
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export const useReaderStore = defineStore('reader', () => {
  const settings = ref<ReaderSettings>(readJson<ReaderSettings>(SETTINGS_KEY, DEFAULT_SETTINGS))
  const progressMap = ref<Record<string, ReaderProgress>>(readJson<Record<string, ReaderProgress>>(PROGRESS_KEY, {}))

  const themeClass = computed(() => {
    return `reader-theme-${settings.value.background}`
  })

  function setFontSize(value: number): void {
    settings.value.fontSize = Math.max(14, Math.min(32, value))
  }

  function setLineHeight(value: number): void {
    settings.value.lineHeight = Math.max(1.4, Math.min(2.6, value))
  }

  function setBackground(value: ReaderBackground): void {
    settings.value.background = value
  }

  function saveProgress(novelId: string, progress: ReaderProgress): void {
    progressMap.value[novelId] = progress
  }

  function getProgress(novelId: string): ReaderProgress | null {
    return progressMap.value[novelId] ?? null
  }

  watch(
    settings,
    (value) => {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(value))
    },
    { deep: true },
  )

  watch(
    progressMap,
    (value) => {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(value))
    },
    { deep: true },
  )

  return {
    settings,
    themeClass,
    setFontSize,
    setLineHeight,
    setBackground,
    saveProgress,
    getProgress,
  }
})
