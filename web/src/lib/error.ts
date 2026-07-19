import type { AxiosError } from 'axios'

import type { ApiErrorPayload } from '@/types/api'

function pickFirstError(payload: Record<string, unknown>): string {
  const firstValue = Object.values(payload)[0]
  if (Array.isArray(firstValue) && firstValue.length > 0) {
    return String(firstValue[0])
  }
  if (typeof firstValue === 'string') {
    return firstValue
  }
  return '请求失败，请稍后重试。'
}

export function getErrorMessage(error: unknown, fallback = '请求失败，请稍后重试。'): string {
  const axiosError = error as AxiosError<ApiErrorPayload | Record<string, unknown>>
  const payload = axiosError?.response?.data

  if (!payload) {
    // 如果没有响应数据，检查请求错误
    if (axiosError?.message === 'Network Error') {
      console.error('❌ 网络错误:', {
        message: axiosError.message,
        config: axiosError.config,
        requestURL: axiosError.config?.url,
        baseURL: axiosError.config?.baseURL,
      })
      return '网络连接失败，请检查 API 地址配置。'
    }
    return fallback
  }

  if (typeof payload === 'string') {
    return payload
  }

  if (typeof payload.detail === 'string') {
    return payload.detail
  }

  if (typeof payload.message === 'string') {
    return payload.message
  }

  return pickFirstError(payload as Record<string, unknown>)
}
