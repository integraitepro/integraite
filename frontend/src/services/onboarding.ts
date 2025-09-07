/**
 * Onboarding API services
 */

import { api } from '@/lib/api'

export interface Integration {
  id: string
  name: string
  category: string
  description: string
  setup_time?: string
  difficulty?: string
}

export interface AvailableAgent {
  id: string
  name: string
  layer: string
  description: string
  recommended: boolean
  capabilities?: string[]
  supported_services?: string[]
}

export interface OnboardingCompanyData {
  organization_name: string
  domain?: string
  description?: string
  logo_url?: string
}

export interface OnboardingIntegrationsData {
  selected_integrations: string[]
}

export interface OnboardingAgentsData {
  selected_agents: string[]
}

export interface OnboardingPoliciesData {
  auto_approval_threshold: number
  require_approval_for_high: boolean
  require_approval_for_medium: boolean
  enable_rollback: boolean
}

export interface TeamMember {
  email: string
  role: 'viewer' | 'member' | 'admin'
}

export interface OnboardingTeamData {
  team_members: TeamMember[]
}

export interface OnboardingCompleteRequest {
  company: OnboardingCompanyData
  integrations: OnboardingIntegrationsData
  agents: OnboardingAgentsData
  policies: OnboardingPoliciesData
  team: OnboardingTeamData
}

export interface OnboardingStatus {
  completed: boolean
  current_step: number
  steps: Array<{
    id: number
    title: string
    completed: boolean
  }>
}

export interface OnboardingCompleteResponse {
  success: boolean
  message: string
  organization: {
    name: string
    agents_count: number
    integrations_count: number
    team_size: number
  }
  next_steps: string[]
}

export const onboardingService = {
  async getAvailableIntegrations(): Promise<{ integrations: Integration[] }> {
    return api.get<{ integrations: Integration[] }>('/onboarding/available-integrations')
  },

  async getAvailableAgents(): Promise<{ agents: AvailableAgent[] }> {
    return api.get<{ agents: AvailableAgent[] }>('/onboarding/available-agents')
  },

  async completeOnboarding(data: OnboardingCompleteRequest): Promise<OnboardingCompleteResponse> {
    return api.post<OnboardingCompleteResponse>('/onboarding/complete', data)
  },

  async getOnboardingStatus(): Promise<OnboardingStatus> {
    return api.get<OnboardingStatus>('/onboarding/status')
  },
}
