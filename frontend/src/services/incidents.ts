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

// SRE Execution types
export interface SRETimelineEntry {
  id: number
  step_number: number
  timestamp: string
  action_type: string
  title: string
  description?: string
  status: string
  duration_seconds?: number
  metadata?: Record<string, any>
}

export interface SREHypothesis {
  id: number
  hypothesis_text: string
  confidence_score?: number
  reasoning?: string
  supporting_evidence?: Record<string, any>
  status: string
  created_at: string
  updated_at?: string
}

export interface SREVerification {
  id: number
  verification_type: string
  description: string
  command_executed?: string
  expected_result?: string
  actual_result?: string
  success: boolean
  timestamp: string
  metadata?: Record<string, any>
}

export interface SREEvidence {
  id: number
  evidence_type: string
  source: string
  content: string
  metadata?: Record<string, any>
  collected_at: string
  relevance_score?: number
}

export interface SREProvenance {
  id: number
  step_id: string
  parent_step_id?: string
  reasoning_type: string
  input_data?: Record<string, any>
  reasoning_process?: string
  output_conclusion?: string
  confidence?: number
  timestamp: string
  agent_component?: string
}

export interface SREExecutionAgent {
  id: string
  name: string
  type: string
  role: string
  status: string
  current_action?: string
  progress: number
  confidence?: number
  findings: string[]
  recommendations: string[]
  started_at: string
  completed_at?: string
}

export interface SREIncidentExecution {
  id: number
  incident_number: string
  incident_title?: string
  incident_description?: string
  target_ip?: string
  priority?: string
  category?: string
  assignment_group?: string
  status: string
  agent_name: string
  started_at: string
  completed_at?: string
  resolution_summary?: string
  final_hypothesis?: string
  resolution_steps?: Record<string, any>[]
  verification_results?: Record<string, any>
  timeline_entries: SRETimelineEntry[]
  hypotheses: SREHypothesis[]
  verifications: SREVerification[]
  evidence: SREEvidence[]
  provenance: SREProvenance[]
  agents: SREExecutionAgent[]
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
  
  // SRE execution data
  sre_execution?: SREIncidentExecution
  sre_timeline: SRETimelineEntry[]
  sre_hypotheses: SREHypothesis[]
  sre_verifications: SREVerification[]
  sre_evidence: SREEvidence[]
  sre_provenance: SREProvenance[]
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

  async getIncident(id: string): Promise<IncidentDetail> {
    return api.get<IncidentDetail>(`/incidents/${id}`)
  },

  async createIncident(data: CreateIncidentRequest): Promise<IncidentDetail> {
    return api.post<IncidentDetail>('/incidents', data)
  },

  async updateIncident(id: string, data: UpdateIncidentRequest): Promise<IncidentDetail> {
    return api.put<IncidentDetail>(`/incidents/${id}`, data)
  },

  async deleteIncident(id: string): Promise<{ message: string }> {
    return api.delete<{ message: string }>(`/incidents/${id}`)
  },
}
