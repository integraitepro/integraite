import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { useIncidents, useIncidentStats } from '@/hooks/useIncidents'
import {
  Search, Filter, AlertTriangle, Clock, CheckCircle2, XCircle, 
  Activity, Server, Database, Network, Shield, Monitor, 
  ArrowUpRight, CalendarDays, User, Zap, TrendingUp, Eye
} from 'lucide-react'

export function IncidentsPage() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')

  // Fetch incidents and stats from API
  const { data: statsData, isLoading: statsLoading } = useIncidentStats()
  const { data: incidentsData, isLoading: incidentsLoading, error: incidentsError } = useIncidents({
    severity: selectedSeverity === 'all' ? undefined : selectedSeverity,
    status: selectedStatus === 'all' ? undefined : selectedStatus,
    search: searchTerm || undefined,
  })

  const incidents = incidentsData?.incidents || []
  const stats = statsData || {
    total: 0,
    critical: 0,
    investigating: 0,
    remediating: 0,
    resolved: 0,
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400'
      case 'low': return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400'
      default: return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'investigating': return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400'
      case 'remediating': return 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400'
      case 'resolved': return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400'
      case 'closed': return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400'
      default: return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'investigating': return <Eye className="h-3 w-3" />
      case 'remediating': return <Activity className="h-3 w-3" />
      case 'resolved': return <CheckCircle2 className="h-3 w-3" />
      case 'closed': return <XCircle className="h-3 w-3" />
      default: return <Clock className="h-3 w-3" />
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const now = new Date()
    const date = new Date(dateString)
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 60) return `${diffInMinutes} min ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hour${Math.floor(diffInMinutes / 60) > 1 ? 's' : ''} ago`
    return `${Math.floor(diffInMinutes / 1440)} day${Math.floor(diffInMinutes / 1440) > 1 ? 's' : ''} ago`
  }

  // Handle loading and error states
  if (incidentsLoading || statsLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span>Loading incidents...</span>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (incidentsError) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load incidents</h3>
            <p className="text-muted-foreground">Please try refreshing the page</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Incidents</h1>
            <p className="text-muted-foreground mt-2">
              Monitor and manage incidents with autonomous agents
            </p>
          </div>
          <div className="flex items-center space-x-2 mt-4 sm:mt-0">
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button size="sm">
              <AlertTriangle className="mr-2 h-4 w-4" />
              Create Incident
            </Button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-4 md:grid-cols-5">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total</p>
                  <p className="text-2xl font-bold">{stats.total}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Critical</p>
                  <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
                </div>
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Investigating</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.investigating}</p>
                </div>
                <Eye className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Remediating</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.remediating}</p>
                </div>
                <Activity className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Resolved</p>
                  <p className="text-2xl font-bold text-green-600">{stats.resolved}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search incidents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <select 
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-2 border rounded-md bg-background"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select 
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border rounded-md bg-background"
          >
            <option value="all">All Statuses</option>
            <option value="investigating">Investigating</option>
            <option value="remediating">Remediating</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>

        {/* Incidents List */}
        <div className="space-y-4">
          {incidents.map((incident) => (
            <Card 
              key={incident.id} 
              className="hover:shadow-md transition-all duration-200 cursor-pointer border-l-4"
              style={{ borderLeftColor: incident.severity === 'critical' ? '#dc2626' : incident.severity === 'high' ? '#ea580c' : incident.severity === 'medium' ? '#ca8a04' : '#16a34a' }}
              onClick={() => navigate(`/app/incident/${incident.incident_id}`)}
            >
              <CardContent className="p-6">
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold hover:text-primary transition-colors">
                          {incident.title}
                        </h3>
                        <Badge variant="outline" className="text-xs font-mono">
                          {incident.incident_id}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground text-sm">
                        {incident.description}
                      </p>
                    </div>
                    <ArrowUpRight className="h-5 w-5 text-muted-foreground" />
                  </div>

                  {/* Status and Severity */}
                  <div className="flex items-center space-x-3">
                    <Badge className={cn("text-xs border", getSeverityColor(incident.severity))}>
                      {incident.severity.toUpperCase()}
                    </Badge>
                    <Badge className={cn("text-xs border flex items-center space-x-1", getStatusColor(incident.status))}>
                      {getStatusIcon(incident.status)}
                      <span>{incident.status.charAt(0).toUpperCase() + incident.status.slice(1)}</span>
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {incident.category}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {incident.impact}
                    </Badge>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-3 border-t border-b">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground">Assigned Agent</p>
                      <p className="text-sm font-medium">{incident.assigned_agent || 'Unassigned'}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground">Agents Involved</p>
                      <p className="text-sm font-medium">{incident.agents_involved}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground">Confidence</p>
                      <p className="text-sm font-medium">{Math.round(incident.confidence)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground">Est. Resolution</p>
                      <p className="text-sm font-medium">{incident.estimated_resolution}</p>
                    </div>
                  </div>

                  {/* Recent Actions */}
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">Recent Agent Actions</p>
                    <div className="space-y-1">
                      {incident.actions.slice(0, 2).map((action, index) => (
                        <div key={index} className="flex items-center space-x-2 text-xs">
                          <div className={cn(
                            "w-2 h-2 rounded-full",
                            action.type === 'detect' ? 'bg-blue-500' :
                            action.type === 'analyze' ? 'bg-purple-500' :
                            action.type === 'remediate' ? 'bg-orange-500' :
                            action.type === 'optimize' ? 'bg-green-500' :
                            action.type === 'monitor' ? 'bg-cyan-500' : 'bg-gray-500'
                          )} />
                          <span className="text-muted-foreground">{action.description}</span>
                          <span className="text-muted-foreground">•</span>
                          <span className="text-muted-foreground">{action.time}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground pt-2">
                    <div className="flex items-center space-x-4">
                      <span className="flex items-center space-x-1">
                        <CalendarDays className="h-3 w-3" />
                        <span>Started {formatTimeAgo(incident.start_time)}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>Updated {formatTimeAgo(incident.last_update)}</span>
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span>Affected: {incident.affected_services.length} service{incident.affected_services.length !== 1 ? 's' : ''}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {incidents.length === 0 && (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No incidents found</h3>
            <p className="text-muted-foreground">
              {searchTerm || selectedSeverity !== 'all' || selectedStatus !== 'all' 
                ? 'Try adjusting your filters' 
                : 'No incidents match your criteria'}
            </p>
          </div>
        )}
      </div>
    </AppLayout>
  )
}