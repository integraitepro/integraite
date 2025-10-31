/**
 * API client configuration and utilities
 */

// Determine API URL based on environment
const getApiBaseUrl = () => {
  // 1. Use explicit environment variable if set
  // if (import.meta.env.VITE_API_URL) {
  //   return import.meta.env.VITE_API_URL
  // }
  
  // // 2. Auto-detect based on mode
  // if (import.meta.env.DEV) {
  //   // Development mode - use localhost
  //   return 'https://api.integraite.com/api/v1'
  // } else {
  //   // Production mode - use live API
  //   return 'https://api.integraite.com/api/v1'
  // }
    return 'https://api.integraite.com/api/v1'
    // return "http://localhost:8000/api/v1"
}

const API_BASE_URL = getApiBaseUrl()

// Debug logging (only in development)
if (import.meta.env.DEV) {
  console.log('🔗 API Configuration:', {
    mode: import.meta.env.MODE,
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
    explicitApiUrl: import.meta.env.VITE_API_URL,
    finalApiUrl: API_BASE_URL
  })
}

export class ApiError extends Error {
  constructor(public status: number, message: string, public data?: any) {
    super(message)
    this.name = 'ApiError'
  }
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    // Get token from localStorage if it exists
    this.token = localStorage.getItem('auth_token')
  }

  setToken(token: string) {
    this.token = token
    localStorage.setItem('auth_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('auth_token')
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new ApiError(
        response.status,
        errorData.detail || `HTTP ${response.status}`,
        errorData
      )
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

export const api = new ApiClient(API_BASE_URL)
