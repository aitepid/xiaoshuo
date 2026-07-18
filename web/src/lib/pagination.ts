export function toRelativeApiPath(nextUrl: string | null): string {
  if (!nextUrl) {
    return ''
  }

  const marker = '/api/v1'
  const idx = nextUrl.indexOf(marker)
  if (idx < 0) {
    return ''
  }

  return nextUrl.slice(idx + marker.length)
}
