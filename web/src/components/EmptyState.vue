<script setup lang="ts">
defineProps<{
  title: string
  description: string
  actionText?: string
  compact?: boolean
}>()

const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <section
    class="rounded-2xl border border-dashed border-black/20 bg-white/60 text-center dark:border-white/20 dark:bg-white/5"
    :class="compact ? 'p-5' : 'p-8'"
  >
    <div class="mx-auto mb-3 h-10 w-10 rounded-full bg-slate-900/8 dark:bg-white/10" />
    <h3 class="text-base font-semibold text-slate-800 dark:text-slate-100">{{ title }}</h3>
    <p class="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500 dark:text-slate-300">{{ description }}</p>

    <button v-if="actionText" class="btn-primary mt-4" type="button" @click="emit('retry')">
      {{ actionText }}
    </button>
  </section>
</template>
