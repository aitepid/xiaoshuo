<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getErrorMessage } from '@/lib/error'
import { useAuthStore } from '@/stores/auth'
import { useFeedbackStore } from '@/stores/feedback'

const authStore = useAuthStore()
const feedbackStore = useFeedbackStore()
const router = useRouter()
const route = useRoute()

const form = reactive({
  account: '',
  password: '',
})

const errors = reactive({
  account: '',
  password: '',
})
const submitting = ref(false)

const canSubmit = computed(() => !submitting.value)

function validate(): boolean {
  errors.account = ''
  errors.password = ''

  if (!form.account.trim()) {
    errors.account = '请输入邮箱、手机号或用户名。'
  }

  if (!form.password || form.password.length < 8) {
    errors.password = '密码长度至少 8 位。'
  }

  return !errors.account && !errors.password
}

async function submit(): Promise<void> {
  if (!validate()) {
    feedbackStore.pushToast('error', '请修正表单错误')
    return
  }

  submitting.value = true
  try {
    await authStore.login({ ...form })
    feedbackStore.pushToast('success', '登录成功')
    const redirect = (route.query.redirect as string) || '/bookshelf'
    await router.push(redirect)
  } catch (error) {
    feedbackStore.pushToast('error', '登录失败', getErrorMessage(error))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="mx-auto max-w-md rounded-3xl border border-black/10 bg-white/80 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-black/20">
    <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">欢迎回来</h1>
    <p class="mt-2 text-sm text-slate-500 dark:text-slate-300">输入账号即可继续阅读与同步书架进度。</p>

    <form class="mt-6 space-y-4" @submit.prevent="submit">
      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>账号（邮箱/手机号/用户名）</span>
        <input v-model="form.account" required class="field-input" :class="{ 'field-error': errors.account }" />
        <p v-if="errors.account" class="error-text">{{ errors.account }}</p>
      </label>

      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>密码</span>
        <input v-model="form.password" type="password" required class="field-input" :class="{ 'field-error': errors.password }" />
        <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
      </label>

      <button type="submit" class="btn-primary w-full" :disabled="!canSubmit || authStore.loading">
        {{ authStore.loading || submitting ? '登录中...' : '登录' }}
      </button>

      <p class="text-center text-xs text-slate-500 dark:text-slate-400">
        还没有账号？
        <RouterLink class="font-semibold text-amber-700 hover:underline dark:text-amber-300" to="/auth/register">立即注册</RouterLink>
      </p>
    </form>
  </section>
</template>
