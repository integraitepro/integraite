/**
 * React hooks for integrations management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  integrationsService,
  type IntegrationProvider,
  type UserIntegration,
  type IntegrationRequest,
  type IntegrationStats,
  type IntegrationTestResult,
  type CreateIntegrationData,
  type UpdateIntegrationData,
  type CreateIntegrationRequestData,
  type TestIntegrationData
} from '../services/integrations';

// Provider hooks
export function useIntegrationProviders(params?: {
  category?: string;
  status?: string;
  featured?: boolean;
  search?: string;
}) {
  return useQuery({
    queryKey: ['integration-providers', params],
    queryFn: () => integrationsService.getProviders(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useIntegrationProvider(providerId: number) {
  return useQuery({
    queryKey: ['integration-provider', providerId],
    queryFn: () => integrationsService.getProvider(providerId),
    enabled: !!providerId,
    staleTime: 5 * 60 * 1000,
  });
}

// User integrations hooks
export function useUserIntegrations(params?: {
  provider_id?: number;
  active?: boolean;
  verified?: boolean;
}) {
  return useQuery({
    queryKey: ['user-integrations', params],
    queryFn: () => integrationsService.getUserIntegrations(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useUserIntegration(integrationId: number) {
  return useQuery({
    queryKey: ['user-integration', integrationId],
    queryFn: () => integrationsService.getUserIntegration(integrationId),
    enabled: !!integrationId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateIntegrationData) => integrationsService.createIntegration(data),
    onSuccess: (newIntegration) => {
      // Invalidate and refetch user integrations
      queryClient.invalidateQueries({ queryKey: ['user-integrations'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      
      toast.success(`Integration "${newIntegration.name}" created successfully!`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create integration');
    },
  });
}

export function useUpdateIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ integrationId, data }: { integrationId: number; data: UpdateIntegrationData }) =>
      integrationsService.updateIntegration(integrationId, data),
    onSuccess: (updatedIntegration, { integrationId }) => {
      // Update the specific integration in cache
      queryClient.setQueryData(['user-integration', integrationId], updatedIntegration);
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['user-integrations'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      
      toast.success(`Integration "${updatedIntegration.name}" updated successfully!`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update integration');
    },
  });
}

export function useDeleteIntegration() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (integrationId: number) => integrationsService.deleteIntegration(integrationId),
    onSuccess: (_, integrationId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: ['user-integration', integrationId] });
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['user-integrations'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      
      toast.success('Integration deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete integration');
    },
  });
}

// Testing hooks
export function useTestIntegration() {
  return useMutation({
    mutationFn: ({ integrationId, testData }: { integrationId: number; testData?: TestIntegrationData }) =>
      integrationsService.testIntegration(integrationId, testData),
    onSuccess: (result) => {
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to test integration');
    },
  });
}

export function useTestIntegrationConfig() {
  return useMutation({
    mutationFn: ({ providerId, testData }: { providerId: number; testData: TestIntegrationData }) =>
      integrationsService.testIntegrationConfig(providerId, testData),
    onSuccess: (result) => {
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to test configuration');
    },
  });
}

// Integration requests hooks
export function useIntegrationRequests(status?: string) {
  return useQuery({
    queryKey: ['integration-requests', status],
    queryFn: () => integrationsService.getIntegrationRequests(status),
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateIntegrationRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateIntegrationRequestData) => integrationsService.createIntegrationRequest(data),
    onSuccess: (newRequest) => {
      queryClient.invalidateQueries({ queryKey: ['integration-requests'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      
      toast.success(`Integration request for "${newRequest.service_name}" submitted successfully!`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to submit integration request');
    },
  });
}

// Statistics hook
export function useIntegrationStats() {
  return useQuery({
    queryKey: ['integration-stats'],
    queryFn: () => integrationsService.getStats(),
    staleTime: 5 * 60 * 1000,
  });
}

// Utility hooks
export function useIntegrationCategories() {
  const { data: providers } = useIntegrationProviders();
  
  const categories = providers?.reduce((acc, provider) => {
    if (!acc.includes(provider.category)) {
      acc.push(provider.category);
    }
    return acc;
  }, [] as string[]) || [];

  return categories.map(category => ({
    value: category,
    label: integrationsService.getCategoryDisplayName(category)
  }));
}

export function useProvidersByCategory() {
  const { data: providers } = useIntegrationProviders();
  
  const providersByCategory = providers?.reduce((acc, provider) => {
    const category = provider.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(provider);
    return acc;
  }, {} as Record<string, IntegrationProvider[]>) || {};

  return providersByCategory;
}
