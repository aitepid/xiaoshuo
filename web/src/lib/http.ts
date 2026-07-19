import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'

import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '@/lib/storage'

// 自动推断 API 基础 URL
function getApiBaseUrl(): string {
  // 1. 优先使用 Vite 环境变量
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl) {
    console.log('✓ 使用环境变量 API 地址:', envUrl)
    return envUrl
  }

  // 2. 在 Render 上，推断 API 地址
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    const protocol = window.location.protocol
    
    // 检测 Render 域名
    if (hostname.includes('onrender.com')) {
      // Render 前端: xiaoshuo-web.onrender.com
      // 后端: xiaoshuo-ng79.onrender.com
      const backendUrl = `${protocol}//xiaoshuo-ng79.onrender.com/api/v1`
      console.log('✓ Render 环境，推断 API 地址:', backendUrl)
      return backendUrl
    }
  }

  // 3. 本地开发默认地址
  const defaultUrl = 'http://127.0.0.1:8000/api/v1'
  console.log('✓ 使用默认 API 地址:', defaultUrl)
  return defaultUrl
}

const API_BASE_URL = getApiBaseUrl()

interface RetriableAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const refresh = getRefreshToken()
  if (!refresh) {
    throw new Error('Missing refresh token')
  }

  const response = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh })
  const nextAccess = response.data?.access as string | undefined

  if (!nextAccess) {
    throw new Error('Invalid refresh response')
  }

  setTokens(nextAccess, refresh)
  return nextAccess
}

function attachAuthHeader(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  const access = getAccessToken()
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
}

async function handleAuthError(instance: AxiosInstance, error: AxiosError): Promise<unknown> {
  const original = error.config as RetriableAxiosRequestConfig | undefined

  if (!original || original._retry || error.response?.status !== 401) {
    throw error
  }

  original._retry = true

  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null
    })
  }

  try {
    const freshToken = await refreshPromise
    original.headers = original.headers ?? {}
    original.headers.Authorization = `Bearer ${freshToken}`
    return instance(original as AxiosRequestConfig)
  } catch (refreshError) {
    clearTokens()
    window.dispatchEvent(new CustomEvent('auth:expired'))
    throw refreshError
  }
}

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

http.interceptors.request.use(attachAuthHeader)
http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => handleAuthError(http, error),
)

export default http
