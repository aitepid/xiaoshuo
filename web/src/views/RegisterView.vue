<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getErrorMessage } from '@/lib/error'
import { useAuthStore } from '@/stores/auth'
import { useFeedbackStore } from '@/stores/feedback'

const authStore = useAuthStore()
const feedbackStore = useFeedbackStore()
const router = useRouter()

const form = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  role: 'reader' as 'reader' | 'author',
})

const errors = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
})
const submitting = ref(false)
const canSubmit = computed(() => !submitting.value)

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function validatePhone(phone: string): boolean {
  return /^\+?\d{6,20}$/.test(phone)
}

function validate(): boolean {
  errors.username = ''
  errors.email = ''
  errors.phone = ''
  errors.password = ''

  if (!form.email.trim() && !form.phone.trim()) {
    errors.email = '邮箱或手机号至少填写一个。'
    errors.phone = '邮箱或手机号至少填写一个。'
  }

  if (form.email.trim() && !validateEmail(form.email.trim())) {
    errors.email = '邮箱格式不正确。'
  }

  if (form.phone.trim() && !validatePhone(form.phone.trim())) {
    errors.phone = '手机号格式不正确。'
  }

  if (form.username.trim() && form.username.trim().length < 2) {
    errors.username = '用户名至少 2 个字符。'
  }

  if (form.password.length < 8) {
    errors.password = '密码长度至少 8 位。'
  }

  return !errors.username && !errors.email && !errors.phone && !errors.password
}

async function submit(): Promise<void> {
  if (!validate()) {
    feedbackStore.pushToast('error', '请修正表单错误')
    return
  }

  submitting.value = true
  try {
    await authStore.register({ ...form })
    feedbackStore.pushToast('success', '注册成功', '请登录后开始阅读')
    await router.push('/auth/login')
  } catch (error) {
    feedbackStore.pushToast('error', '注册失败', getErrorMessage(error))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="mx-auto max-w-md rounded-3xl border border-black/10 bg-white/80 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-black/20">
    <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-100">创建账号</h1>
    <p class="mt-2 text-sm text-slate-500 dark:text-slate-300">注册后即可同步书架、解锁创作中心和阅读偏好。</p>

    <form class="mt-6 space-y-4" @submit.prevent="submit">
      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>用户名（可选）</span>
        <input v-model="form.username" class="field-input" :class="{ 'field-error': errors.username }" />
        <p v-if="errors.username" class="error-text">{{ errors.username }}</p>
      </label>

      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>邮箱（可选）</span>
        <input v-model="form.email" type="email" class="field-input" :class="{ 'field-error': errors.email }" />
        <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
      </label>

      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>手机号（可选）</span>
        <input v-model="form.phone" class="field-input" :class="{ 'field-error': errors.phone }" />
        <p v-if="errors.phone" class="error-text">{{ errors.phone }}</p>
      </label>

      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>密码</span>
        <input v-model="form.password" type="password" required class="field-input" :class="{ 'field-error': errors.password }" />
        <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
      </label>

      <label class="space-y-2 text-sm text-slate-600 dark:text-slate-200">
        <span>身份</span>
        <select v-model="form.role" class="field-input">
          <option value="reader">读者</option>
          <option value="author">作者</option>
        </select>
      </label>

      <button type="submit" class="btn-primary w-full" :disabled="!canSubmit || authStore.loading">
        {{ authStore.loading || submitting ? '提交中...' : '注册并前往登录' }}
      </button>

      <p class="text-center text-xs text-slate-500 dark:text-slate-400">
        已有账号？
        <RouterLink class="font-semibold text-amber-700 hover:underline dark:text-amber-300" to="/auth/login">前往登录</RouterLink>
      </p>
    </form>
  </section>
</template>
