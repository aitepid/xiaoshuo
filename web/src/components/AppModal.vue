<script setup lang="ts">
import { useFeedbackStore } from '@/stores/feedback'

const feedbackStore = useFeedbackStore()
</script>

<template>
  <teleport to="body">
    <transition name="fade-slide">
      <div v-if="feedbackStore.modal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 backdrop-blur-sm">
        <section class="w-full max-w-sm rounded-2xl border border-black/10 bg-white p-5 shadow-xl dark:border-white/10 dark:bg-slate-900">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100">{{ feedbackStore.modal.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{{ feedbackStore.modal.message }}</p>
          <div class="mt-6 flex items-center justify-end gap-2">
            <button class="btn-secondary" type="button" @click="feedbackStore.closeModal">{{ feedbackStore.modal.cancelText }}</button>
            <button class="btn-primary" type="button" @click="feedbackStore.confirmModal">{{ feedbackStore.modal.confirmText }}</button>
          </div>
        </section>
      </div>
    </transition>
  </teleport>
</template>
