/**
 * Agents React Query hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentsService, type CreateAgentRequest, type UpdateAgentStatusRequest } from '@/services/agents'

export const useAgents = () => {
  return useQuery({
    queryKey: ['agents'],
    queryFn: agentsService.getAgents,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  })
}

export const useAgent = (id: number) => {
  return useQuery({
    queryKey: ['agent', id],
    queryFn: () => agentsService.getAgent(id),
    enabled: !!id,
    refetchInterval: 15000, // Refetch every 15 seconds
    staleTime: 5000, // Consider data stale after 5 seconds
  })
}

export const useCreateAgent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: agentsService.createAgent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: (error) => {
      console.error('Failed to create agent:', error)
    },
  })
}

export const useUpdateAgentStatus = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateAgentStatusRequest }) =>
      agentsService.updateAgentStatus(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      queryClient.invalidateQueries({ queryKey: ['agent', id] })
    },
    onError: (error) => {
      console.error('Failed to update agent status:', error)
    },
  })
}

export const useDeleteAgent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: agentsService.deleteAgent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: (error) => {
      console.error('Failed to delete agent:', error)
    },
  })
}
