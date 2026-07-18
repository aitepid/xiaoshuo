import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import http from '@/lib/http'
import { clearTokens, getAccessToken, getRefreshToken, hasToken, setTokens } from '@/lib/storage'

interface LoginPayload {
  account: string
  password: string
}

interface RegisterPayload {
  username?: string
  email?: string
  phone?: string
  password: string
  role?: 'reader' | 'author'
}

interface UserProfile {
  id: number
  username: string
  email?: string | null
  phone?: string | null
  role: string
  bio?: string
  avatar_url?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserProfile | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => hasToken())

  async function login(payload: LoginPayload): Promise<void> {
    loading.value = true
    try {
      const { data } = await http.post('/auth/login', payload)
      setTokens(data.access, data.refresh)
      user.value = data.user
    } finally {
      loading.value = false
    }
  }

  async function register(payload: RegisterPayload): Promise<void> {
    loading.value = true
    try {
      await http.post('/auth/register', payload)
    } finally {
      loading.value = false
    }
  }

  async function loadProfile(): Promise<void> {
    if (!isAuthenticated.value || user.value) {
      return
    }

    const { data } = await http.get('/users/me')
    user.value = data
  }

  async function refreshSession(): Promise<boolean> {
    const refresh = getRefreshToken()
    if (!refresh) {
      return false
    }

    try {
      const { data } = await http.post('/auth/refresh', { refresh })
      setTokens(data.access, refresh)
      return true
    } catch {
      logout()
      return false
    }
  }

  function logout(): void {
    clearTokens()
    user.value = null
  }

  function bootFromStorage(): void {
    if (!getAccessToken()) {
      user.value = null
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    loadProfile,
    refreshSession,
    logout,
    bootFromStorage,
  }
})
