<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useFeedbackStore } from '@/stores/feedback'
import { useUiStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUiStore()
const feedbackStore = useFeedbackStore()
const router = useRouter()

const displayName = computed(() => authStore.user?.username || '游客')

function toggleTheme(): void {
  if (uiStore.mode === 'light') {
    uiStore.setTheme('dark')
    feedbackStore.pushToast('info', '已切换深色模式')
    return
  }

  if (uiStore.mode === 'dark') {
    uiStore.setTheme('system')
    feedbackStore.pushToast('info', '已切换跟随系统')
    return
  }

  uiStore.setTheme('light')
  feedbackStore.pushToast('info', '已切换浅色模式')
}

function logout(): void {
  feedbackStore.openModal({
    title: '退出登录',
    message: '确认退出当前账号吗？本地会话将被清理。',
    confirmText: '退出',
    cancelText: '取消',
    onConfirm: () => {
      authStore.logout()
      feedbackStore.pushToast('success', '已退出登录')
      void router.push('/')
    },
  })
}
</script>

<template>
  <header class="mb-8 rounded-2xl border border-black/10 bg-white/70 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5">
    <div class="flex items-center justify-between gap-3">
      <RouterLink to="/" class="text-lg font-semibold tracking-wide text-slate-900 dark:text-slate-100">晨昏书局</RouterLink>

      <nav class="hidden items-center gap-2 text-sm md:flex">
        <RouterLink class="nav-chip" to="/">首页</RouterLink>
        <RouterLink class="nav-chip" to="/bookshelf">书架</RouterLink>
        <RouterLink class="nav-chip" to="/creator">创作</RouterLink>
      </nav>

      <div class="flex items-center gap-2">
        <button class="nav-chip" type="button" @click="toggleTheme">主题: {{ uiStore.mode }}</button>

        <RouterLink v-if="!authStore.isAuthenticated" class="nav-chip" to="/auth/login">登录</RouterLink>
        <button v-else class="nav-chip" type="button" @click="logout">{{ displayName }} · 退出</button>
      </div>
    </div>
  </header>
</template>
