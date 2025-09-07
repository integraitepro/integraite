/**
 * Organization management service
 */

import { api } from '@/lib/api'

export interface Organization {
  id: number
  name: string
  slug: string
  description?: string
  logo_url?: string
  timezone: string
  created_at: string
  updated_at: string
  user_role: string
  agents_count: number
  integrations_count: number
  team_size: number
}

export interface CreateOrganizationRequest {
  name: string
  description?: string
  logo_url?: string
  timezone?: string
}

export interface OrganizationSwitchResponse {
  success: boolean
  message: string
  organization: {
    id: number
    name: string
    slug: string
    role: string
  }
}

export const organizationService = {
  async listOrganizations(): Promise<{ organizations: Organization[] }> {
    return api.get<{ organizations: Organization[] }>('/organizations')
  },

  async createOrganization(data: CreateOrganizationRequest): Promise<Organization> {
    return api.post<Organization>('/organizations', data)
  },

  async getOrganization(organizationId: number): Promise<Organization> {
    return api.get<Organization>(`/organizations/${organizationId}`)
  },

  async switchOrganization(organizationId: number): Promise<OrganizationSwitchResponse> {
    return api.put<OrganizationSwitchResponse>(`/organizations/${organizationId}/switch`)
  },
}
