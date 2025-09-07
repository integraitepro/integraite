/**
 * Authentication API services
 */

import { api } from '@/lib/api'

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  organization_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    first_name: string
    last_name: string
    full_name: string
    is_active: boolean
    is_verified: boolean
    avatar_url?: string
    timezone: string
  }
}

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  is_active: boolean
  is_verified: boolean
  avatar_url?: string
  timezone: string
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://api.integraite.com/api/v1'}/auth/login`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    api.setToken(data.access_token)
    return data
  },

  async signup(userData: SignupRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', userData)
    api.setToken(response.access_token)
    return response
  },

  async getCurrentUser(): Promise<User> {
    return api.get<User>('/auth/me')
  },

  async googleAuth(idToken: string, organizationName?: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/google', {
      id_token: idToken,
      organization_name: organizationName,
    })
    api.setToken(response.access_token)
    return response
  },

  async microsoftAuth(accessToken: string, organizationName?: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/microsoft', {
      access_token: accessToken,
      organization_name: organizationName,
    })
    api.setToken(response.access_token)
    return response
  },

  async refreshToken(): Promise<{ access_token: string; token_type: string }> {
    return api.post('/auth/refresh')
  },

  logout() {
    api.clearToken()
  },
}
