/**
 * Incidents React Query hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  incidentsService, 
  type IncidentListQuery, 
  type CreateIncidentRequest, 
  type UpdateIncidentRequest 
} from '@/services/incidents'

export const useIncidentStats = () => {
  return useQuery({
    queryKey: ['incident', 'stats'],
    queryFn: incidentsService.getIncidentStats,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider data stale after 10 seconds
  })
}

export const useIncidents = (query: IncidentListQuery = {}) => {
  return useQuery({
    queryKey: ['incidents', 'list', query],
    queryFn: () => incidentsService.getIncidents(query),
    refetchInterval: 15000, // Refetch every 15 seconds
    staleTime: 5000, // Consider data stale after 5 seconds
  })
}

export const useIncident = (id: string | null) => {
  return useQuery({
    queryKey: ['incident', 'detail', id],
    queryFn: () => incidentsService.getIncident(id!),
    enabled: !!id,
    refetchInterval: 10000, // Refetch every 10 seconds for real-time updates
    staleTime: 3000, // Consider data stale after 3 seconds
  })
}

export const useCreateIncident = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: incidentsService.createIncident,
    onSuccess: () => {
      // Invalidate and refetch incident list and stats
      queryClient.invalidateQueries({ queryKey: ['incidents', 'list'] })
      queryClient.invalidateQueries({ queryKey: ['incident', 'stats'] })
    },
    onError: (error) => {
      console.error('Failed to create incident:', error)
    },
  })
}

export const useUpdateIncident = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateIncidentRequest }) =>
      incidentsService.updateIncident(id, data),
    onSuccess: (_, { id }) => {
      // Invalidate specific incident, list, and stats
      queryClient.invalidateQueries({ queryKey: ['incident', 'detail', id] })
      queryClient.invalidateQueries({ queryKey: ['incidents', 'list'] })
      queryClient.invalidateQueries({ queryKey: ['incident', 'stats'] })
    },
    onError: (error) => {
      console.error('Failed to update incident:', error)
    },
  })
}

export const useDeleteIncident = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: incidentsService.deleteIncident,
    onSuccess: () => {
      // Invalidate incident list and stats
      queryClient.invalidateQueries({ queryKey: ['incidents', 'list'] })
      queryClient.invalidateQueries({ queryKey: ['incident', 'stats'] })
    },
    onError: (error) => {
      console.error('Failed to delete incident:', error)
    },
  })
}

export const useExecutionLogs = (incidentId: string | null) => {
  return useQuery({
    queryKey: ['incident', 'execution-logs', incidentId],
    queryFn: () => incidentsService.getExecutionLogs(incidentId!),
    enabled: !!incidentId,
    refetchInterval: 2000, // Poll every 2 seconds for real-time updates
    staleTime: 1000, // Consider data stale after 1 second
  })
}
