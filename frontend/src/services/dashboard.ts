/**
 * Dashboard API services
 */

import { api } from '@/lib/api'

export interface KPIData {
  title: string
  value: string
  description: string
  trend: 'up' | 'down' | 'stable'
  color: string
  details: string
}

export interface DashboardStats {
  kpis: KPIData[]
  system_status: {
    status: string
    message: string
    uptime: string
  }
}

export interface RecentAction {
  id: number
  title: string
  description: string
  timestamp: string
  status: string
  confidence: number
  agent: string
}

export interface ActiveAgent {
  name: string
  type: string
  status: string
  incidents: number
  confidence: number
  layer: string
}

export interface AgentCategory {
  name: string
  count: number
  active: number
  color: string
}

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    return api.get<DashboardStats>('/dashboard/stats')
  },

  async getRecentActions(limit = 10): Promise<RecentAction[]> {
    return api.get<RecentAction[]>(`/dashboard/recent-actions?limit=${limit}`)
  },

  async getActiveAgents(): Promise<ActiveAgent[]> {
    return api.get<ActiveAgent[]>('/dashboard/active-agents')
  },

  async getAgentCategories(): Promise<AgentCategory[]> {
    return api.get<AgentCategory[]>('/dashboard/agent-categories')
  },
}
