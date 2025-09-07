/**
 * Organization management hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { organizationService, type CreateOrganizationRequest } from '@/services/organizations'

export const useOrganizations = () => {
  return useQuery({
    queryKey: ['organizations'],
    queryFn: organizationService.listOrganizations,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export const useOrganization = (organizationId: number) => {
  return useQuery({
    queryKey: ['organization', organizationId],
    queryFn: () => organizationService.getOrganization(organizationId),
    enabled: !!organizationId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export const useCreateOrganization = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: organizationService.createOrganization,
    onSuccess: (newOrganization) => {
      // Update the organizations list
      queryClient.setQueryData(['organizations'], (old: any) => {
        if (!old) return { organizations: [newOrganization] }
        return {
          ...old,
          organizations: [newOrganization, ...old.organizations]
        }
      })
      
      // Store as current organization
      localStorage.setItem('organization_name', newOrganization.name)
      localStorage.setItem('current_organization_id', newOrganization.id.toString())
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
    },
  })
}

export const useSwitchOrganization = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: organizationService.switchOrganization,
    onSuccess: (response) => {
      // Update localStorage with new organization
      localStorage.setItem('organization_name', response.organization.name)
      localStorage.setItem('current_organization_id', response.organization.id.toString())
      
      // Invalidate all data queries since we're switching context
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['automations'] })
      
      // Trigger a page refresh to update all components with new org context
      window.location.reload()
    },
  })
}
