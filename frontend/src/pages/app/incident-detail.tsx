import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/app-layout'
import { useExecutionLogs } from '@/hooks/useIncidents'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import type { ExecutionLogStep } from '@/services/incidents'
import {
  ArrowLeft, Clock, AlertTriangle, CheckCircle2, Activity, Eye, 
  Server, Terminal, Code, PlayCircle, Pause, CheckSquare,
  Calendar, User, ExternalLink, Download, Share2, Zap,
  Settings, MessageSquare, FileText, GitBranch, Timer,
  BarChart3, TrendingUp, Cpu, Monitor, Layers
} from 'lucide-react'

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  // Fetch execution logs from API with polling
  const { data: executionLogs, isLoading, error } = useExecutionLogs(id || null)

  // Handle loading and error states
  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[70vh]">
          <div className="text-center">
            <div className="relative mb-6">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary/20 border-t-primary mx-auto"></div>
              <div className="absolute inset-0 rounded-full h-16 w-16 border-4 border-transparent border-r-primary/40 animate-pulse mx-auto"></div>
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">Loading Incident Details</h3>
              <p className="text-muted-foreground">Fetching execution logs and analysis...</p>
              <div className="flex items-center justify-center space-x-1 mt-4">
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[70vh]">
          <div className="text-center max-w-md">
            <div className="relative mb-6">
              <div className="w-20 h-20 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto">
                <AlertTriangle className="h-10 w-10 text-red-600 dark:text-red-400" />
              </div>
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full animate-ping"></div>
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">Unable to Load Execution Logs</h3>
            <p className="text-muted-foreground mb-6">We encountered an error while fetching the incident execution data. Please try again.</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button onClick={() => window.location.reload()} variant="default">
                <AlertTriangle className="mr-2 h-4 w-4" />
                Retry
              </Button>
              <Button onClick={() => navigate('/app/incidents')} variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Incidents
              </Button>
            </div>
          </div>
        </div>
      </AppLayout>
    )
  }
  
  if (!executionLogs || !executionLogs.logs || executionLogs.logs.length === 0) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[70vh]">
          <div className="text-center max-w-md">
            <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
              <FileText className="h-10 w-10 text-gray-500" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">No Execution Logs Found</h3>
            <p className="text-muted-foreground mb-2">
              {executionLogs?.message || `No execution logs are available for incident ${id}`}
            </p>
            <p className="text-sm text-muted-foreground mb-6">
              The incident may not have started execution yet, or logs are still being generated.
            </p>
            <Button onClick={() => navigate('/app/incidents')} variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Incidents
            </Button>
          </div>
        </div>
      </AppLayout>
    )
  }

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'INCIDENT_RECEIVED': return <AlertTriangle className="h-4 w-4" />
      case 'TOOL_CALL': return <Settings className="h-4 w-4" />
      case 'TOOL_RESULT': return <CheckSquare className="h-4 w-4" />
      case 'AGENT_RESPONSE': return <MessageSquare className="h-4 w-4" />
      case 'INCIDENT_COMPLETED': return <CheckCircle2 className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  const getStepTypeColor = (stepType: string) => {
    switch (stepType) {
      case 'INCIDENT_RECEIVED': return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400'
      case 'TOOL_CALL': return 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400'
      case 'TOOL_RESULT': return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400'
      case 'AGENT_RESPONSE': return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400'
      case 'INCIDENT_COMPLETED': return 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400'
      default: return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400'
      case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400'
      case 'FAILED': return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400'
      default: return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  const renderLogData = (step: ExecutionLogStep) => {
    const { data } = step
    
    // Function to format text with **bold** markdown-style formatting
    const formatText = (text: string) => {
      if (!text) return text
      
      const parts = text.split(/(\*\*.*?\*\*)/)
      return parts.map((part, index) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          const boldText = part.slice(2, -2)
          return <strong key={index}>{boldText}</strong>
        }
        return part
      })
    }
    
    if (step.step_type === 'TOOL_CALL') {
      return (
        <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl border border-purple-200 dark:border-purple-700">
          <div className="flex items-center space-x-2 mb-3">
            <div className="p-1.5 bg-purple-200 dark:bg-purple-700 rounded-lg">
              <Code className="h-4 w-4 text-purple-700 dark:text-purple-300" />
            </div>
            <span className="font-semibold text-purple-900 dark:text-purple-100">Tool Execution: {data.tool_name}</span>
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-sm font-medium text-purple-800 dark:text-purple-200 mb-2">Parameters:</div>
              <pre className="text-xs bg-white dark:bg-gray-900 p-3 rounded-lg border border-purple-200 dark:border-purple-700 overflow-auto max-h-40">
                {JSON.stringify(data.arguments, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )
    }
    
    if (step.step_type === 'TOOL_RESULT') {
      return (
        <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl border border-green-200 dark:border-green-700">
          <div className="flex items-center space-x-2 mb-3">
            <div className="p-1.5 bg-green-200 dark:bg-green-700 rounded-lg">
              <Terminal className="h-4 w-4 text-green-700 dark:text-green-300" />
            </div>
            <span className="font-semibold text-green-900 dark:text-green-100">Result: {data.tool_name}</span>
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">Output:</div>
              <pre className="text-xs bg-white dark:bg-gray-900 p-3 rounded-lg border border-green-200 dark:border-green-700 max-h-48 overflow-auto font-mono">
                {data.result}
              </pre>
            </div>
          </div>
        </div>
      )
    }
    
    if (step.step_type === 'AGENT_RESPONSE') {
      return (
        <div className="mt-4 p-4 bg-gradient-to-r from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl border border-orange-200 dark:border-orange-700">
          <div className="flex items-center space-x-2 mb-3">
            <div className="p-1.5 bg-orange-200 dark:bg-orange-700 rounded-lg">
              <MessageSquare className="h-4 w-4 text-orange-700 dark:text-orange-300" />
            </div>
            <span className="font-semibold text-orange-900 dark:text-orange-100">Agent Analysis</span>
          </div>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <div className="text-sm text-orange-900 dark:text-orange-100 whitespace-pre-wrap leading-relaxed">
              {formatText(data.message)}
            </div>
          </div>
        </div>
      )
    }
    
    if (step.step_type === 'INCIDENT_RECEIVED') {
      return (
        <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border border-blue-200 dark:border-blue-700">
          <div className="flex items-center space-x-2 mb-3">
            <div className="p-1.5 bg-blue-200 dark:bg-blue-700 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-blue-700 dark:text-blue-300" />
            </div>
            <span className="font-semibold text-blue-900 dark:text-blue-100">Incident Received</span>
          </div>
          <div className="space-y-2 text-sm text-blue-900 dark:text-blue-100">
            <div><strong>Description:</strong> {formatText(data.incident_description)}</div>
            <div><strong>Status:</strong> <Badge variant="outline" className="ml-1">{data.status}</Badge></div>
          </div>
        </div>
      )
    }
    
    if (step.step_type === 'INCIDENT_COMPLETED') {
      return (
        <div className="mt-4 p-4 bg-gradient-to-r from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 rounded-xl border border-emerald-200 dark:border-emerald-700">
          <div className="flex items-center space-x-2 mb-3">
            <div className="p-1.5 bg-emerald-200 dark:bg-emerald-700 rounded-lg">
              <CheckCircle2 className="h-4 w-4 text-emerald-700 dark:text-emerald-300" />
            </div>
            <span className="font-semibold text-emerald-900 dark:text-emerald-100">Execution Completed</span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm text-emerald-900 dark:text-emerald-100">
            <div><strong>Status:</strong> {data.status}</div>
            <div><strong>Total Steps:</strong> {data.total_steps}</div>
            <div><strong>Duration:</strong> {formatDuration(data.duration_seconds)}</div>
            <div className="col-span-2"><strong>Summary:</strong> {formatText(data.summary)}</div>
          </div>
        </div>
      )
    }
    
    return null
  }

  return (
    <AppLayout>
      <div className="space-y-8">
        {/* Enhanced Hero Header */}
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-cyan-500/10 dark:from-blue-500/5 dark:via-purple-500/5 dark:to-cyan-500/5"></div>
          <div className="relative bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-2xl p-8">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
              <div className="flex items-start space-x-4">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => navigate('/app/incidents')}
                  className="shrink-0 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back
                </Button>
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <Monitor className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h1 className="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 dark:from-gray-100 dark:via-blue-200 dark:to-purple-200 bg-clip-text text-transparent">
                        Incident Execution
                      </h1>
                      <p className="text-lg text-muted-foreground">
                        Real-time analysis for <span className="font-mono font-semibold text-foreground">{executionLogs.incident_id}</span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Timer className="h-4 w-4" />
                      <span>Started {formatTimestamp(executionLogs.start_time)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Activity className="h-4 w-4" />
                      <span>Duration {formatDuration(executionLogs.duration_seconds)}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex flex-col space-y-3">
                <Badge 
                  className={cn("text-sm px-4 py-2 font-medium shadow-lg", getStatusColor(executionLogs.status))}
                >
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  {executionLogs.status}
                </Badge>
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground">{executionLogs.logs.length}/{executionLogs.step_count}</div>
                  <div className="text-xs text-muted-foreground">Steps Available</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5"></div>
            <CardContent className="relative p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <Clock className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <Badge variant="outline" className="text-xs">Timing</Badge>
              </div>
              <div className="space-y-2">
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {formatDuration(executionLogs.duration_seconds)}
                  </div>
                  <div className="text-xs text-muted-foreground">Total Duration</div>
                </div>
                <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-sm text-muted-foreground">
                    Last updated {formatTimestamp(executionLogs.last_updated)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-emerald-500/5"></div>
            <CardContent className="relative p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <Badge variant="outline" className="text-xs">Performance</Badge>
              </div>
              <div className="space-y-2">
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {executionLogs.step_count}
                  </div>
                  <div className="text-xs text-muted-foreground">Total Steps</div>
                </div>
                <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-sm text-muted-foreground">
                    Avg: {(executionLogs.duration_seconds / executionLogs.step_count).toFixed(1)}s per step
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Execution Logs */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 via-white to-gray-50/50 dark:from-gray-900/50 dark:via-gray-800/50 dark:to-gray-900/50"></div>
          <CardHeader className="relative">
            <CardTitle className="flex items-center space-x-2 text-xl">
              <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                <Layers className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </div>
              <span>Execution Timeline</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="relative">
            <div className="space-y-6">
              {executionLogs.logs.map((step, index) => {
                const isLatest = index === executionLogs.logs.length - 1
                const isCompleted = index < executionLogs.logs.length - 1
                return (
                  <div 
                    key={step.step_number} 
                    className={cn(
                      "relative transition-all duration-700"
                    )}
                  >
                    {/* Timeline Line */}
                    {index < executionLogs.logs.length - 1 && (
                      <div className="absolute left-6 top-12 w-0.5 h-full bg-gradient-to-b from-gray-300 to-transparent dark:from-gray-600"></div>
                    )}
                    
                    <div className={cn(
                      "relative flex items-start space-x-4 p-6 rounded-2xl border transition-all duration-500",
                      isLatest 
                        ? "bg-primary/5 border-primary/20 shadow-lg shadow-primary/10" 
                        : isCompleted 
                          ? "bg-gray-50/50 dark:bg-gray-800/50 border-gray-200/50 dark:border-gray-700/50" 
                          : "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700"
                    )}>
                      {/* Step Icon */}
                      <div className={cn(
                        "flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-500",
                        isLatest 
                          ? "bg-primary text-white border-primary shadow-lg" 
                          : isCompleted 
                            ? "bg-green-100 text-green-600 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-700" 
                            : "bg-gray-100 text-gray-500 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700"
                      )}>
                        {getStepIcon(step.step_type)}
                      </div>
                      
                      {/* Step Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <Badge className={cn("text-xs font-medium", getStepTypeColor(step.step_type))}>
                              {step.step_type.replace('_', ' ')}
                            </Badge>
                            <span className="text-sm font-semibold text-foreground">
                              Step {step.step_number}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            <span>{formatTimestamp(step.timestamp)}</span>
                          </div>
                        </div>
                        
                        {renderLogData(step)}
                      </div>
                    </div>
                  </div>
                )
              })}
              
              {/* Completion Message */}
              {executionLogs.status === 'COMPLETED' && (
                <div className="text-center py-8 border-t border-gray-200 dark:border-gray-700">
                  <div className="inline-flex items-center space-x-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-full">
                    <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                    <span className="text-sm font-medium text-green-800 dark:text-green-200">
                      Execution completed successfully
                    </span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}