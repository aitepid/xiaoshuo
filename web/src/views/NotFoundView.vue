<script setup lang="ts">
import { useRouter } from 'vue-router'

import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()

async function goHome(): Promise<void> {
  await router.push('/')
}
</script>

<template>
  <section class="mx-auto max-w-xl">
    <EmptyState
      title="页面走丢了"
      description="你访问的页面不存在，可能已被移动或删除。"
      action-text="返回首页"
      @retry="goHome"
    />
  </section>
</template>
