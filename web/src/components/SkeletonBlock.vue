<script setup lang="ts">
defineProps<{
  height?: string
  rounded?: string
}>()
</script>

<template>
  <div
    class="skeleton-wave"
    :style="{
      height: height || '1rem',
      borderRadius: rounded || '0.75rem',
    }"
  />
</template>
