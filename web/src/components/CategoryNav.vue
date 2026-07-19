<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { Category } from '@/types/category'
import { getErrorMessage } from '@/lib/error'
import http from '@/lib/http'

const categories = ref<Category[]>([])
const selectedCategoryId = ref<number | null>(null)
const loading = ref(false)

const emit = defineEmits<{
  categoryChange: [categoryId: number | null]
}>()

async function fetchCategories(): Promise<void> {
  loading.value = true
  try {
    const { data } = await http.get<{ results: Category[] }>('/categories')
    categories.value = data.results || []
  } catch (error) {
    console.error('Failed to fetch categories:', getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function selectCategory(categoryId: number | null): void {
  selectedCategoryId.value = categoryId
  emit('categoryChange', categoryId)
}

onMounted(() => {
  void fetchCategories()
})
</script>

<template>
  <div class="rounded-2xl border border-black/10 bg-white/70 p-4 backdrop-blur dark:border-white/10 dark:bg-white/5">
    <div class="flex flex-wrap gap-2">
      <button
        class="category-chip transition-colors"
        :class="{ active: selectedCategoryId === null }"
        @click="selectCategory(null)"
      >
        全部
      </button>
      
      <button
        v-for="category in categories"
        :key="category.id"
        class="category-chip transition-colors"
        :class="{ active: selectedCategoryId === category.id }"
        :title="category.description"
        @click="selectCategory(category.id)"
      >
        {{ category.name }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.category-chip {
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(71, 85, 105);
  cursor: pointer;
  white-space: nowrap;

  &:hover {
    background-color: rgba(255, 255, 255, 0.8);
  }

  &.active {
    background-color: rgb(217, 119, 6);
    color: white;
    border-color: rgb(217, 119, 6);
  }

  :dark & {
    border-color: rgba(255, 255, 255, 0.1);
    background-color: rgba(255, 255, 255, 0.05);
    color: rgb(203, 213, 225);

    &:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }

    &.active {
      background-color: rgb(217, 119, 6);
      color: white;
      border-color: rgb(217, 119, 6);
    }
  }
}
</style>
