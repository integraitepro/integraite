/**
 * Agent deployment service
 */

import { api } from '@/lib/api'

export interface DeployAgentRequest {
  name: string
  description: string
  category: 'compute' | 'database' | 'network' | 'security' | 'monitoring' | 'application' | 'container' | 'storage'
  template?: string
  layer: 'presentation' | 'application' | 'data' | 'infrastructure'
  autoStart: boolean
  alertThreshold: number
  retryAttempts: number
  configOverrides?: string
  tags: string[]
}

export interface DeployAgentResponse {
  success: boolean
  message: string
  agent: {
    id: string
    name: string
    description: string
    category: string
    layer: string
    status: string
    confidence: number
    incidents: number
    lastAction: string
    createdAt: string
    updatedAt: string
    config: {
      alertThreshold: number
      retryAttempts: number
      autoStart: boolean
      template?: string
      configOverrides?: string
      tags: string[]
    }
  }
  estimatedReadyTime: string
  nextSteps: string[]
}

export interface AgentTemplate {
  id: string
  name: string
  description: string
  category: string
  layer: string
  capabilities: string[]
  estimatedSetupTime: string
  complexity: string
}

export const agentDeploymentService = {
  async deployAgent(data: DeployAgentRequest): Promise<DeployAgentResponse> {
    return api.post<DeployAgentResponse>('/agents/deploy', data)
  },

  async getAgentTemplates(): Promise<{ [category: string]: AgentTemplate[] }> {
    return api.get<{ [category: string]: AgentTemplate[] }>('/agents/templates/')
  },

  async updateAgentStatus(agentId: string, status: 'active' | 'inactive' | 'paused'): Promise<any> {
    return api.put(`/agents/${agentId}/status`, { status })
  },

  async deleteAgent(agentId: string): Promise<any> {
    return api.delete(`/agents/${agentId}`)
  }
}
