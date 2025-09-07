/**
 * Agent deployment hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { agentDeploymentService, type DeployAgentRequest } from '@/services/agentDeployment'

export const useDeployAgent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: agentDeploymentService.deployAgent,
    onSuccess: (response) => {
      // Invalidate agents list to show the new agent
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      
      // Show success notification
      console.log('Agent deployed successfully:', response.agent.name)
      
      // Optionally store deployment info for notifications
      localStorage.setItem('lastDeployedAgent', JSON.stringify({
        id: response.agent.id,
        name: response.agent.name,
        estimatedReadyTime: response.estimatedReadyTime,
        deployedAt: new Date().toISOString()
      }))
    },
    onError: (error) => {
      console.error('Failed to deploy agent:', error)
    },
  })
}

export const useAgentTemplates = () => {
  return useQuery({
    queryKey: ['agentTemplates'],
    queryFn: agentDeploymentService.getAgentTemplates,
    staleTime: 1000 * 60 * 30, // Templates don't change often, cache for 30 minutes
  })
}

export const useUpdateAgentStatus = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ agentId, status }: { agentId: string, status: 'active' | 'inactive' | 'paused' }) =>
      agentDeploymentService.updateAgentStatus(agentId, status),
    onSuccess: (data, variables) => {
      // Invalidate agents list to reflect status change
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      console.log(`Agent ${variables.agentId} status updated to ${variables.status}`)
    },
    onError: (error) => {
      console.error('Failed to update agent status:', error)
    },
  })
}

export const useDeleteAgent = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: agentDeploymentService.deleteAgent,
    onSuccess: (data, agentId) => {
      // Invalidate agents list to remove the deleted agent
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      console.log(`Agent ${agentId} deleted successfully`)
    },
    onError: (error) => {
      console.error('Failed to delete agent:', error)
    },
  })
}
