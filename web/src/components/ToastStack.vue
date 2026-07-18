<script setup lang="ts">
import { useFeedbackStore } from '@/stores/feedback'

const feedbackStore = useFeedbackStore()
</script>

<template>
  <div class="pointer-events-none fixed right-4 top-4 z-40 flex w-[min(92vw,360px)] flex-col gap-2">
    <transition-group name="toast-pop" tag="div">
      <article
        v-for="item in feedbackStore.toasts"
        :key="item.id"
        class="pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow-md backdrop-blur"
        :class="{
          'border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-500/40 dark:bg-emerald-700/20 dark:text-emerald-100':
            item.type === 'success',
          'border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-500/40 dark:bg-rose-700/20 dark:text-rose-100':
            item.type === 'error',
          'border-sky-300 bg-sky-50 text-sky-900 dark:border-sky-500/40 dark:bg-sky-700/20 dark:text-sky-100':
            item.type === 'info',
        }"
      >
        <h4 class="font-semibold">{{ item.title }}</h4>
        <p v-if="item.message" class="mt-1 text-xs/5 opacity-85">{{ item.message }}</p>
      </article>
    </transition-group>
  </div>
</template>
