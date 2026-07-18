<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'

import AppModal from '@/components/AppModal.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import BottomTabBar from '@/components/BottomTabBar.vue'
import ToastStack from '@/components/ToastStack.vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUiStore()

onMounted(() => {
  uiStore.applyTheme()

  window.addEventListener('auth:expired', () => {
    authStore.logout()
  })
})
</script>

<template>
  <div class="min-h-screen bg-[var(--app-bg)] text-[var(--text-main)] transition-colors duration-500">
    <div class="mx-auto flex min-h-screen w-full max-w-[1120px] flex-col px-4 pb-24 pt-5 md:px-8 md:pb-10">
      <AppNavbar />

      <main class="flex-1">
        <RouterView v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </main>

      <footer class="mt-10 text-center text-xs text-slate-500 dark:text-slate-400">
        商用级阅读平台 · 阶段 2 公共层持续完善中
      </footer>

      <BottomTabBar />
      <ToastStack />
      <AppModal />
    </div>
  </div>
</template>
