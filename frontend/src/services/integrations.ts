/**
 * Integration service for managing external service connections
 */

import { api } from '../lib/api';

// Types
export interface IntegrationProvider {
  id: number;
  name: string;
  display_name: string;
  description: string;
  category: string;
  status: string;
  icon_url?: string;
  logo_url?: string;
  brand_color?: string;
  documentation_url?: string;
  setup_guide_url?: string;
  tags: string[];
  supported_features: string[];
  is_active: boolean;
  is_featured: boolean;
  requires_approval: boolean;
  created_at: string;
  updated_at: string;
  configuration_fields: ConfigurationField[];
  total_integrations: number;
  active_integrations: number;
}

export interface ConfigurationField {
  id: number;
  provider_id: number;
  field_name: string;
  display_label: string;
  field_type: string;
  description?: string;
  placeholder?: string;
  is_required: boolean;
  is_sensitive: boolean;
  validation_regex?: string;
  validation_message?: string;
  field_options?: Array<{ value: string; label: string }>;
  default_value?: string;
  sort_order: number;
  field_group?: string;
}

export interface UserIntegration {
  id: number;
  provider_id: number;
  user_id: number;
  organization_id: number;
  name: string;
  description?: string;
  configuration: Record<string, any>;
  tags: string[];
  integration_metadata: Record<string, any>;
  is_active: boolean;
  is_verified: boolean;
  last_sync_at?: string;
  last_error?: string;
  created_at: string;
  updated_at: string;
  provider: IntegrationProvider;
}

export interface IntegrationRequest {
  id: number;
  user_id: number;
  organization_id: number;
  provider_id?: number;
  service_name: string;
  service_url?: string;
  description: string;
  business_justification?: string;
  expected_usage?: string;
  priority: string;
  category?: string;
  estimated_users?: number;
  status: string;
  admin_notes?: string;
  reviewed_by?: number;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
  user_name?: string;
  user_email?: string;
}

export interface IntegrationStats {
  total_providers: number;
  active_providers: number;
  total_user_integrations: number;
  active_user_integrations: number;
  pending_requests: number;
  providers_by_category: Record<string, number>;
  integrations_by_category: Record<string, number>;
  popular_providers: Array<{
    name: string;
    integrations: number;
    category: string;
  }>;
}

export interface IntegrationTestResult {
  success: boolean;
  message: string;
  details?: Record<string, any>;
  response_time_ms?: number;
}

// Create Integration Data
export interface CreateIntegrationData {
  provider_id: number;
  name: string;
  description?: string;
  configuration: Record<string, any>;
  tags?: string[];
  integration_metadata?: Record<string, any>;
}

export interface UpdateIntegrationData {
  name?: string;
  description?: string;
  configuration?: Record<string, any>;
  is_active?: boolean;
  tags?: string[];
  integration_metadata?: Record<string, any>;
}

export interface CreateIntegrationRequestData {
  provider_id?: number;
  service_name: string;
  service_url?: string;
  description: string;
  business_justification?: string;
  expected_usage?: string;
  priority?: string;
  category?: string;
  estimated_users?: number;
}

export interface TestIntegrationData {
  configuration: Record<string, any>;
}

// API Endpoints
class IntegrationsService {
  // Provider endpoints
  async getProviders(params?: {
    category?: string;
    status?: string;
    featured?: boolean;
    search?: string;
  }): Promise<IntegrationProvider[]> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.append('category', params.category);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.featured !== undefined) searchParams.append('featured', params.featured.toString());
    if (params?.search) searchParams.append('search', params.search);

    const url = `/integrations/providers${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    const response = await api.get<IntegrationProvider[]>(url);
    return response;
  }

  async getProvider(providerId: number): Promise<IntegrationProvider> {
    const response = await api.get<IntegrationProvider>(`/integrations/providers/${providerId}`);
    return response;
  }

  // User integrations endpoints
  async getUserIntegrations(params?: {
    provider_id?: number;
    active?: boolean;
    verified?: boolean;
  }): Promise<UserIntegration[]> {
    const searchParams = new URLSearchParams();
    if (params?.provider_id) searchParams.append('provider_id', params.provider_id.toString());
    if (params?.active !== undefined) searchParams.append('active', params.active.toString());
    if (params?.verified !== undefined) searchParams.append('verified', params.verified.toString());

    const url = `/integrations${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    const response = await api.get<UserIntegration[]>(url);
    return response;
  }

  async getUserIntegration(integrationId: number): Promise<UserIntegration> {
    const response = await api.get<UserIntegration>(`/integrations/${integrationId}`);
    return response;
  }

  async createIntegration(data: CreateIntegrationData): Promise<UserIntegration> {
    const response = await api.post<UserIntegration>('/integrations', data);
    return response;
  }

  async updateIntegration(integrationId: number, data: UpdateIntegrationData): Promise<UserIntegration> {
    const response = await api.put<UserIntegration>(`/integrations/${integrationId}`, data);
    return response;
  }

  async deleteIntegration(integrationId: number): Promise<void> {
    await api.delete(`/integrations/${integrationId}`);
  }

  // Testing endpoints
  async testIntegration(integrationId: number, testData?: TestIntegrationData): Promise<IntegrationTestResult> {
    const response = await api.post<IntegrationTestResult>(`/integrations/${integrationId}/test`, testData);
    return response;
  }

  async testIntegrationConfig(providerId: number, testData: TestIntegrationData): Promise<IntegrationTestResult> {
    const response = await api.post<IntegrationTestResult>(`/integrations/test?provider_id=${providerId}`, testData);
    return response;
  }

  // Integration requests endpoints
  async getIntegrationRequests(status?: string): Promise<IntegrationRequest[]> {
    const url = `/integrations/requests${status ? `?status=${status}` : ''}`;
    const response = await api.get<IntegrationRequest[]>(url);
    return response;
  }

  async createIntegrationRequest(data: CreateIntegrationRequestData): Promise<IntegrationRequest> {
    const response = await api.post<IntegrationRequest>('/integrations/requests', data);
    return response;
  }

  // Statistics endpoint
  async getStats(): Promise<IntegrationStats> {
    const response = await api.get<IntegrationStats>('/integrations/stats');
    return response;
  }

  // Utility methods
  getCategoryDisplayName(category: string): string {
    const categoryNames: Record<string, string> = {
      cloud_infrastructure: 'Cloud Infrastructure',
      monitoring: 'Monitoring & Observability',
      incident_management: 'Incident Management',
      communication: 'Communication',
      version_control: 'Version Control',
      ci_cd: 'CI/CD',
      security: 'Security',
      database: 'Database',
      container: 'Container',
      logging: 'Logging',
      analytics: 'Analytics',
      storage: 'Storage',
      networking: 'Networking',
      other: 'Other'
    };
    return categoryNames[category] || category;
  }

  getStatusDisplayName(status: string): string {
    const statusNames: Record<string, string> = {
      available: 'Available',
      coming_soon: 'Coming Soon',
      beta: 'Beta',
      deprecated: 'Deprecated'
    };
    return statusNames[status] || status;
  }

  getFieldTypeDisplayName(fieldType: string): string {
    const fieldTypeNames: Record<string, string> = {
      text: 'Text',
      password: 'Password',
      email: 'Email',
      url: 'URL',
      number: 'Number',
      boolean: 'Boolean',
      select: 'Select',
      multiselect: 'Multi Select',
      json: 'JSON',
      file: 'File'
    };
    return fieldTypeNames[fieldType] || fieldType;
  }
}

export const integrationsService = new IntegrationsService();