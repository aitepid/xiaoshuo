export interface ApiErrorPayload {
  detail?: string
  message?: string
  code?: string
  [key: string]: unknown
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface ApiPage<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
