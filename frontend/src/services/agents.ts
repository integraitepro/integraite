/**
 * Agents API services
 */

import { api } from '@/lib/api'

export interface AgentAction {
  type: string
  description: string
  time: string
}

export interface AgentMetrics {
  [key: string]: number
}

export interface Agent {
  id: number
  name: string
  type: string
  status: 'active' | 'paused' | 'error' | 'deploying' | 'stopped'
  description: string
  layer: string
  confidence: number
  incidents: number
  last_action?: string
  actions: AgentAction[]
  metrics: AgentMetrics
}

export interface CreateAgentRequest {
  name: string
  type: string
  description?: string
  config?: Record<string, any>
  environment?: string
}

export interface UpdateAgentStatusRequest {
  status: 'active' | 'paused' | 'stopped'
}

export const agentsService = {
  async getAgents(): Promise<Agent[]> {
    return api.get<Agent[]>('/agents')
  },

  async getAgent(id: number): Promise<Agent> {
    return api.get<Agent>(`/agents/${id}`)
  },

  async createAgent(data: CreateAgentRequest): Promise<Agent> {
    return api.post<Agent>('/agents', data)
  },

  async updateAgentStatus(id: number, data: UpdateAgentStatusRequest): Promise<{ message: string }> {
    return api.put<{ message: string }>(`/agents/${id}/status`, data)
  },

  async deleteAgent(id: number): Promise<{ message: string }> {
    return api.delete<{ message: string }>(`/agents/${id}`)
  },
}
