/**
 * Generic API response interface matching backend ApiResponse model
 */
export interface ApiResponse<T = any> {
  success: boolean
  msg: string
  data?: T
}

export interface ErrorResponse {
  success: boolean
  msg: string
  error?: string
}

/**
 * Generic API request wrapper that handles the new response format
 */
export async function apiRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const router = useRouter()

  // Add auth header if token exists
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`
  }

  const response = await fetch(`${config.public.apiBase}${url}`, {
    ...options,
    headers,
  })

  // Handle 401/403 - unauthorized/forbidden
  if (response.status === 401 || response.status === 403) {
    // Clear auth and redirect to login
    authStore.clearAuth()
    router.push('/login')
    throw new Error('Session expired. Please login again.')
  }

  const json: ApiResponse<T> = await response.json()

  if (!response.ok || !json.success) {
    throw new Error(json.msg || 'An error occurred')
  }

  return json.data as T
}

/**
 * Convenience methods for different HTTP verbs
 */
export const api = {
  get: <T>(url: string) => apiRequest<T>(url, { method: 'GET' }),

  post: <T>(url: string, body?: any) =>
    apiRequest<T>(url, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  put: <T>(url: string, body?: any) =>
    apiRequest<T>(url, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  patch: <T>(url: string, body?: any) =>
    apiRequest<T>(url, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  delete: <T>(url: string) =>
    apiRequest<T>(url, { method: 'DELETE' }),
}
