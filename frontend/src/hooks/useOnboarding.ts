/**
 * Onboarding React Query hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { onboardingService, type OnboardingCompleteRequest } from '@/services/onboarding'

export const useAvailableIntegrations = () => {
  return useQuery({
    queryKey: ['availableIntegrations'],
    queryFn: onboardingService.getAvailableIntegrations,
    staleTime: 1000 * 60 * 10, // Consider data stale after 10 minutes
  })
}

export const useAvailableAgents = () => {
  return useQuery({
    queryKey: ['availableAgents'],
    queryFn: onboardingService.getAvailableAgents,
    staleTime: 1000 * 60 * 10, // Consider data stale after 10 minutes
  })
}

export const useOnboardingStatus = () => {
  return useQuery({
    queryKey: ['onboarding', 'status'],
    queryFn: onboardingService.getOnboardingStatus,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export const useCompleteOnboarding = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: onboardingService.completeOnboarding,
    onSuccess: () => {
      // Invalidate onboarding status to trigger re-check
      queryClient.invalidateQueries({ queryKey: ['onboarding', 'status'] })
      // Also invalidate current user data 
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
      // Navigate to app after a short delay to allow status update
      setTimeout(() => {
        navigate('/app', { replace: true })
      }, 100)
    },
    onError: (error) => {
      console.error('Failed to complete onboarding:', error)
    },
  })
}
