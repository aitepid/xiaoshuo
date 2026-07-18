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
