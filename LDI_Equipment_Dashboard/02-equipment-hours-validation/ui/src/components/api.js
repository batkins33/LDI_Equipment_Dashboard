const DEFAULT_BASE = 'http://127.0.0.1:5000'

export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE
}

export async function apiGet(path, params) {
  const url = new URL(getApiBaseUrl() + path)

  if (params && typeof params === 'object') {
    Object.entries(params).forEach(([k, v]) => {
      if (v === undefined || v === null || v === '') return
      url.searchParams.set(k, String(v))
    })
  }

  const res = await fetch(url)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json()
}
