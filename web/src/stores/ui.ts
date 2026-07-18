import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

type ThemeMode = 'light' | 'dark' | 'system'

const THEME_KEY = 'xs_theme_mode'

export const useUiStore = defineStore('ui', () => {
  const mode = ref<ThemeMode>((localStorage.getItem(THEME_KEY) as ThemeMode) || 'system')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)')

  const resolvedTheme = computed<'light' | 'dark'>(() => {
    if (mode.value === 'system') {
      return prefersDark.matches ? 'dark' : 'light'
    }
    return mode.value
  })

  function applyTheme(): void {
    document.documentElement.dataset.theme = resolvedTheme.value
  }

  function setTheme(next: ThemeMode): void {
    mode.value = next
  }

  watch(
    mode,
    (value) => {
      localStorage.setItem(THEME_KEY, value)
      applyTheme()
    },
    { immediate: true },
  )

  prefersDark.addEventListener('change', () => {
    if (mode.value === 'system') {
      applyTheme()
    }
  })

  return {
    mode,
    resolvedTheme,
    setTheme,
    applyTheme,
  }
})
