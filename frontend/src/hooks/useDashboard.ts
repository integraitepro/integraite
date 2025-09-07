/**
 * Dashboard React Query hooks
 */

import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '@/services/dashboard'

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboardStats'],
    queryFn: dashboardService.getStats,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  })
}

export const useRecentActions = (limit = 10) => {
  return useQuery({
    queryKey: ['recentActions', limit],
    queryFn: () => dashboardService.getRecentActions(limit),
    refetchInterval: 15000, // Refetch every 15 seconds
    staleTime: 5000, // Consider data stale after 5 seconds
  })
}

export const useActiveAgents = () => {
  return useQuery({
    queryKey: ['activeAgents'],
    queryFn: dashboardService.getActiveAgents,
    refetchInterval: 60000, // Refetch every minute
    staleTime: 30000, // Consider data stale after 30 seconds
  })
}

export const useAgentCategories = () => {
  return useQuery({
    queryKey: ['agentCategories'],
    queryFn: dashboardService.getAgentCategories,
    staleTime: 1000 * 60 * 5, // Consider data stale after 5 minutes
  })
}
