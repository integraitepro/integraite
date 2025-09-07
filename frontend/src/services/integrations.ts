/**
 * Integrations API services
 */

import { api } from '@/lib/api'

export interface Integration {
  id: string
  name: string
  category: string
  description: string
  status: 'available' | 'coming-soon' | 'beta'
}

export interface IntegrationCategory {
  title: string
  integrations: Integration[]
}

export interface IntegrationsMarketplace {
  categories: IntegrationCategory[]
}

export const integrationsService = {
  async getMarketplace(): Promise<IntegrationsMarketplace> {
    return api.get<IntegrationsMarketplace>('/integrations/marketplace')
  },

  async getConfiguredIntegrations(): Promise<{ integrations: any[] }> {
    return api.get<{ integrations: any[] }>('/integrations')
  },

  async createIntegration(data: any): Promise<{ message: string }> {
    return api.post<{ message: string }>('/integrations', data)
  },

  async testIntegration(id: number): Promise<{ integration_id: number; status: string }> {
    return api.post<{ integration_id: number; status: string }>(`/integrations/${id}/test`)
  },
}
