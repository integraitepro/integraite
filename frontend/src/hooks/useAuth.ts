/**
 * Authentication React Query hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authService, type LoginRequest, type SignupRequest, type User } from '@/services/auth'

export const useLogin = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      queryClient.setQueryData(['currentUser'], data.user)
      navigate('/app')
    },
    onError: (error) => {
      console.error('Login failed:', error)
    },
  })
}

export const useSignup = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: authService.signup,
    onSuccess: (data) => {
      queryClient.setQueryData(['currentUser'], data.user)
      navigate('/app/onboarding')
    },
    onError: (error) => {
      console.error('Signup failed:', error)
    },
  })
}

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: authService.getCurrentUser,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export const useGoogleAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ idToken, organizationName }: { idToken: string; organizationName?: string }) =>
      authService.googleAuth(idToken, organizationName),
    onSuccess: (data) => {
      queryClient.setQueryData(['currentUser'], data.user)
      navigate('/app')
    },
    onError: (error) => {
      console.error('Google auth failed:', error)
    },
  })
}

export const useMicrosoftAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ accessToken, organizationName }: { accessToken: string; organizationName?: string }) =>
      authService.microsoftAuth(accessToken, organizationName),
    onSuccess: (data) => {
      queryClient.setQueryData(['currentUser'], data.user)
      navigate('/app')
    },
    onError: (error) => {
      console.error('Microsoft auth failed:', error)
    },
  })
}

export const useLogout = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return () => {
    authService.logout()
    queryClient.clear()
    navigate('/login')
  }
}
