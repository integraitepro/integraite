/**
 * Incidents API services
 */

import { api } from '@/lib/api'

export interface IncidentAction {
  type: string
  description: string
  time: string
}

export interface TimelineEntry {
  id: number
  entry_type: string
  title: string
  description?: string
  source?: string
  occurred_at: string
  created_at: string
  entry_metadata: Record<string, any>
}

export interface AgentExecution {
  id: number
  agent_id: string
  agent_name: string
  agent_type: string
  role: string
  status: string
  current_action?: string
  progress: number
  confidence?: number
  findings: string[]
  recommendations: string[]
  started_at?: string
  completed_at?: string
}

export interface InfrastructureComponent {
  id: number
  name: string
  component_type: string
  layer: string
  status: string
  metrics: Record<string, any>
  agent_actions: string[]
  component_metadata: Record<string, any>
}

export interface VerificationGate {
  id: number
  name: string
  description: string
  target_value: string
  current_value?: string
  status: string
  progress: number
  time_remaining?: string
  completed_at?: string
}

export interface IncidentExecution {
  id: number
  plan_id: string
  plan_name: string
  description?: string
  status: string
  progress: number
  estimated_duration_minutes?: number
  root_cause?: string
  started_at?: string
  completed_at?: string
}

export interface IncidentDetail {
  id: number
  incident_id: string
  title: string
  description: string
  short_description?: string
  severity: string
  status: string
  category?: string
  source_system?: string
  affected_services: string[]
  customer_impact: boolean
  estimated_affected_users?: number
  resolution_type?: string
  resolution_summary?: string
  root_cause?: string
  detection_time?: string
  response_time?: string
  resolution_time?: string
  mttr_minutes?: number
  assigned_agent?: string
  agents_involved: number
  confidence: number
  estimated_resolution: string
  start_time: string
  last_update: string
  resolved_at?: string
  closed_at?: string
  timeline: TimelineEntry[]
  active_agents: AgentExecution[]
  infrastructure_components: InfrastructureComponent[]
  verification_gates: VerificationGate[]
  executions: IncidentExecution[]
  current_progress: number
}

export interface IncidentListItem {
  id: number
  incident_id: string
  title: string
  description: string
  severity: string
  status: string
  category?: string
  impact: string
  assigned_agent?: string
  agents_involved: number
  confidence: number
  estimated_resolution: string
  start_time: string
  last_update: string
  affected_services: string[]
  actions: IncidentAction[]
}

export interface IncidentStats {
  total: number
  critical: number
  investigating: number
  remediating: number
  resolved: number
}

export interface IncidentListQuery {
  severity?: string
  status?: string
  search?: string
  page?: number
  limit?: number
}

export interface CreateIncidentRequest {
  title: string
  description: string
  short_description?: string
  severity: string
  category?: string
  source_system?: string
  affected_services?: string[]
  customer_impact?: boolean
  estimated_affected_users?: number
}

export interface UpdateIncidentRequest {
  title?: string
  description?: string
  severity?: string
  status?: string
  resolution_summary?: string
  root_cause?: string
}

export const incidentsService = {
  async getIncidentStats(): Promise<IncidentStats> {
    return api.get<IncidentStats>('/incidents/stats')
  },

  async getIncidents(query: IncidentListQuery = {}): Promise<{ incidents: IncidentListItem[] }> {
    const params = new URLSearchParams()
    
    if (query.severity) params.append('severity', query.severity)
    if (query.status) params.append('status', query.status)
    if (query.search) params.append('search', query.search)
    if (query.page) params.append('page', query.page.toString())
    if (query.limit) params.append('limit', query.limit.toString())
    
    const url = `/incidents${params.toString() ? `?${params.toString()}` : ''}`
    return api.get<{ incidents: IncidentListItem[] }>(url)
  },

  async getIncident(id: number): Promise<IncidentDetail> {
    return api.get<IncidentDetail>(`/incidents/${id}`)
  },

  async createIncident(data: CreateIncidentRequest): Promise<IncidentDetail> {
    return api.post<IncidentDetail>('/incidents', data)
  },

  async updateIncident(id: number, data: UpdateIncidentRequest): Promise<IncidentDetail> {
    return api.put<IncidentDetail>(`/incidents/${id}`, data)
  },

  async deleteIncident(id: number): Promise<{ message: string }> {
    return api.delete<{ message: string }>(`/incidents/${id}`)
  },
}
