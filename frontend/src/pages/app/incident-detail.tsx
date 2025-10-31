import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/app-layout'
import { useIncident } from '@/hooks/useIncidents'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import {
  ArrowLeft, Clock, AlertTriangle, CheckCircle2, Activity, Eye, 
  Server, Database, Network, Shield, Monitor, Bot, Brain, Zap,
  Play, Pause, RotateCcw, GitBranch, Target, Layers, Code,
  TrendingUp, TrendingDown, Cpu, MemoryStick, HardDrive,
  Calendar, User, ExternalLink, Download, Share2
} from 'lucide-react'

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'execution' | 'agents' | 'timeline' | 'hypotheses' | 'verification' | 'provenance' | 'evidence'>('execution')
  
  // Fetch incident data from API
  const { data: incident, isLoading, error } = useIncident(id || null)
  
  // Handle loading and error states
  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span>Loading incident details...</span>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load incident</h3>
            <p className="text-muted-foreground mb-4">Please try refreshing the page</p>
            <Button onClick={() => navigate('/app/incidents')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Incidents
            </Button>
          </div>
        </div>
      </AppLayout>
    )
  }
  
  if (!incident) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Incident not found</h3>
            <p className="text-muted-foreground mb-4">The requested incident could not be found.</p>
            <Button onClick={() => navigate('/app/incidents')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Incidents
            </Button>
          </div>
        </div>
      </AppLayout>
    )
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400'
      default: return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'investigating': return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400'
      case 'remediating': return 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400'
      case 'resolved': return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400'
      default: return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400'
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

  const tabContent = {
    execution: (
      <div className="space-y-6">
        {/* SRE Execution Plan */}
        {incident.sre_execution && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Bot className="h-5 w-5 text-blue-600" />
                    <span>SRE Agent Execution</span>
                  </CardTitle>
                  <CardDescription>
                    Autonomous SRE agent handling incident resolution
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={cn(
                    incident.sre_execution.status === 'success' ? 'bg-green-100 text-green-800 border-green-200' :
                    incident.sre_execution.status === 'running' ? 'bg-blue-100 text-blue-800 border-blue-200' :
                    incident.sre_execution.status === 'failed' ? 'bg-red-100 text-red-800 border-red-200' :
                    'bg-gray-100 text-gray-800 border-gray-200'
                  )}>
                    <Activity className="mr-1 h-3 w-3" />
                    {incident.sre_execution.status}
                  </Badge>
                  {incident.sre_execution.agents && incident.sre_execution.agents.length > 0 && (
                    <span className="text-sm text-muted-foreground">
                      {incident.sre_execution.agents[0].progress}% complete
                    </span>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {incident.sre_execution.agents && incident.sre_execution.agents.length > 0 && (
                <Progress value={incident.sre_execution.agents[0].progress} className="h-3" />
              )}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Agent:</span>
                  <span className="ml-2 font-medium">{incident.sre_execution.agent_name}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Started:</span>
                  <span className="ml-2 font-medium">{formatTimeAgo(incident.sre_execution.started_at)}</span>
                </div>
                {incident.sre_execution.target_ip && (
                  <div>
                    <span className="text-muted-foreground">Target:</span>
                    <span className="ml-2 font-medium">{incident.sre_execution.target_ip}</span>
                  </div>
                )}
                {incident.sre_execution.priority && (
                  <div>
                    <span className="text-muted-foreground">Priority:</span>
                    <span className="ml-2 font-medium">{incident.sre_execution.priority}</span>
                  </div>
                )}
              </div>
              
              {incident.sre_execution.resolution_summary && (
                <div>
                  <p className="text-sm font-medium mb-1">Resolution Summary</p>
                  <p className="text-sm text-muted-foreground">{incident.sre_execution.resolution_summary}</p>
                </div>
              )}
              
              {incident.sre_execution.final_hypothesis && (
                <div>
                  <p className="text-sm font-medium mb-1">Final Hypothesis</p>
                  <p className="text-sm text-muted-foreground">{incident.sre_execution.final_hypothesis}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
        
        {/* Legacy Execution Plan Overview */}
        {incident.executions && incident.executions.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="h-5 w-5 text-blue-600" />
                    <span>Execution Plan</span>
                  </CardTitle>
                  <CardDescription>
                    Automated remediation plan with real-time progress tracking
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className="bg-green-100 text-green-800 border-green-200">
                    <Activity className="mr-1 h-3 w-3" />
                    executing
                  </Badge>
                   <span className="text-sm text-muted-foreground">
                     {incident.current_progress}% complete
                   </span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Progress value={incident.current_progress} className="h-3" />
              <div className="text-sm text-muted-foreground">
                Estimated duration: 15 minutes • Plan ID: plan-001
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pre-execution Checks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <span>Pre-execution Checks</span>
            </CardTitle>
            <CardDescription>
              Safety checks before executing remediation actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                'System backup verification',
                'Resource availability check',
                'Dependency health validation',
                'Rollback plan preparation'
              ].map((check, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-sm">{check}</span>
                  <Badge variant="outline" className="text-xs">Passed</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Infrastructure Impact Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Layers className="h-5 w-5 text-purple-600" />
              <span>Infrastructure Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
               {incident.infrastructure_components.map((component: any, index: number) => (
                <Card key={index} className="border-l-4 border-l-orange-500">
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                           <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center">
                             {component.component_type === 'EC2 Instance' && <Server className="h-4 w-4 text-orange-600" />}
                             {component.component_type === 'Load Balancer' && <Network className="h-4 w-4 text-orange-600" />}
                             {component.component_type === 'Redis Cluster' && <Database className="h-4 w-4 text-orange-600" />}
                           </div>
                           <div>
                             <h4 className="font-medium">{component.name}</h4>
                             <p className="text-sm text-muted-foreground">{component.component_type} • {component.layer} Layer</p>
                           </div>
                        </div>
                        <Badge className={cn(
                          "text-xs",
                          component.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                        )}>
                          {component.status}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4">
                        {Object.entries(component.metrics).map(([key, metric]: [string, any]) => (
                          <div key={key} className="text-center">
                            <p className="text-xs text-muted-foreground capitalize">{key}</p>
                            <p className="text-sm font-medium">
                              {metric.current}{metric.unit}
                              <span className={cn(
                                "ml-1 text-xs",
                                metric.current > metric.normal ? 'text-red-600' : 'text-green-600'
                              )}>
                                ({metric.current > metric.normal ? '+' : ''}{metric.current - metric.normal})
                              </span>
                            </p>
                          </div>
                        ))}
                      </div>
                      
                         <div className="pt-2 border-t">
                           <p className="text-xs text-muted-foreground mb-1">Agent Actions:</p>
                           <div className="flex flex-wrap gap-1">
                             {component.agent_actions.map((action: string, idx: number) => (
                             <Badge key={idx} variant="outline" className="text-xs">
                               {action}
                             </Badge>
                           ))}
                         </div>
                       </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    ),
    
     agents: (
       <div className="space-y-6">
         {/* SRE Agents */}
         {incident.sre_execution && incident.sre_execution.agents && incident.sre_execution.agents.length > 0 && (
           <div className="space-y-4">
             <h3 className="text-lg font-medium flex items-center space-x-2">
               <Bot className="h-5 w-5 text-blue-600" />
               <span>SRE Agents</span>
             </h3>
             {incident.sre_execution.agents.map((agent: any, index: number) => (
               <Card key={agent.id} className="border-l-4 border-l-blue-500">
                 <CardHeader>
                   <div className="flex items-center justify-between">
                     <div className="flex items-center space-x-3">
                       <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                         <Bot className="h-5 w-5 text-blue-600" />
                       </div>
                        <div>
                          <CardTitle className="text-lg">{agent.name}</CardTitle>
                          <CardDescription>{agent.type} • {agent.role}</CardDescription>
                        </div>
                     </div>
                     <div className="flex items-center space-x-2">
                       <Badge className={cn(
                         "text-xs",
                         agent.status === 'completed' ? 'bg-green-100 text-green-800' : 
                         agent.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 
                         agent.status === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                       )}>
                         {agent.status}
                       </Badge>
                       {agent.confidence && (
                         <span className="text-sm text-muted-foreground">{agent.confidence}% confidence</span>
                       )}
                     </div>
                   </div>
                 </CardHeader>
                 <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">Current Action</p>
                      <p className="text-sm text-muted-foreground">{agent.current_action || 'No current action'}</p>
                      <Progress value={agent.progress} className="h-2 mt-2" />
                      <p className="text-xs text-muted-foreground mt-1">{agent.progress}% complete</p>
                    </div>
                   
                   {agent.findings && agent.findings.length > 0 && (
                     <div>
                       <p className="text-sm font-medium mb-2">Key Findings</p>
                       <div className="space-y-1">
                         {agent.findings.map((finding: string, idx: number) => (
                           <div key={idx} className="flex items-start space-x-2">
                             <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                             <span className="text-sm">{finding}</span>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}
                   
                   {agent.recommendations && agent.recommendations.length > 0 && (
                     <div>
                       <p className="text-sm font-medium mb-2">Recommendations</p>
                       <div className="space-y-1">
                         {agent.recommendations.map((rec: string, idx: number) => (
                           <div key={idx} className="flex items-start space-x-2">
                             <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0" />
                             <span className="text-sm">{rec}</span>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}
                   
                   <div className="text-xs text-muted-foreground">
                     Started: {formatTimeAgo(agent.started_at)}
                     {agent.completed_at && ` • Completed: ${formatTimeAgo(agent.completed_at)}`}
                   </div>
                 </CardContent>
               </Card>
             ))}
           </div>
         )}
         
         {/* Legacy Agents */}
         {incident.active_agents && incident.active_agents.length > 0 && (
           <div className="space-y-4">
             {incident.sre_execution && incident.sre_execution.agents && incident.sre_execution.agents.length > 0 && (
               <h3 className="text-lg font-medium flex items-center space-x-2">
                 <Bot className="h-5 w-5 text-gray-600" />
                 <span>Legacy Agents</span>
               </h3>
             )}
             {incident.active_agents.map((agent: any, index: number) => (
              <Card key={agent.id} className="border-l-4 border-l-blue-500">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-blue-600" />
                      </div>
                       <div>
                         <CardTitle className="text-lg">{agent.agent_name}</CardTitle>
                         <CardDescription>{agent.agent_type} • {agent.role}</CardDescription>
                       </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={cn(
                        "text-xs",
                        agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      )}>
                        {agent.status}
                      </Badge>
                      {agent.confidence && (
                        <span className="text-sm text-muted-foreground">{agent.confidence}% confidence</span>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                   <div>
                     <p className="text-sm font-medium mb-2">Current Action</p>
                     <p className="text-sm text-muted-foreground">{agent.current_action}</p>
                     <Progress value={agent.progress} className="h-2 mt-2" />
                     <p className="text-xs text-muted-foreground mt-1">{agent.progress}% complete</p>
                   </div>
                  
                  <div>
                    <p className="text-sm font-medium mb-2">Key Findings</p>
                    <div className="space-y-1">
                      {agent.findings.map((finding: string, idx: number) => (
                        <div key={idx} className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                          <span className="text-sm">{finding}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium mb-2">Recommendations</p>
                    <div className="space-y-1">
                      {agent.recommendations.map((rec: string, idx: number) => (
                        <div key={idx} className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0" />
                          <span className="text-sm">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
           </div>
         )}
         
         {/* No agents */}
         {(!incident.sre_execution || !incident.sre_execution.agents || incident.sre_execution.agents.length === 0) &&
          (!incident.active_agents || incident.active_agents.length === 0) && (
           <Card>
             <CardContent className="p-6">
               <div className="text-center py-8">
                 <Bot className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                 <h3 className="text-lg font-medium mb-2">No Agents Active</h3>
                 <p className="text-muted-foreground">
                   SRE agents will appear here when they are deployed to handle this incident
                 </p>
               </div>
             </CardContent>
           </Card>
         )}
       </div>
    ),
    
    timeline: (
      <div className="space-y-4">
        {/* SRE Timeline */}
        {incident.sre_timeline && incident.sre_timeline.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium flex items-center space-x-2">
              <Bot className="h-5 w-5 text-blue-600" />
              <span>SRE Agent Timeline</span>
            </h3>
            {incident.sre_timeline.map((event: any, index: number) => {
              const isCompleted = event.status === 'completed';
              const isInProgress = event.status === 'running';
              
              return (
                <Card key={event.id} className={cn(
                  "border-l-4",
                  isCompleted ? 'border-l-green-500' :
                  isInProgress ? 'border-l-blue-500' : 'border-l-gray-300'
                )}>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center",
                            isCompleted ? 'bg-green-100 text-green-600' :
                            isInProgress ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                          )}>
                            {isCompleted && <CheckCircle2 className="h-4 w-4" />}
                            {isInProgress && <Activity className="h-4 w-4" />}
                            {!isCompleted && !isInProgress && <Clock className="h-4 w-4" />}
                          </div>
                          <div>
                            <h4 className="font-medium">{event.title}</h4>
                            <p className="text-sm text-muted-foreground">
                              Step {event.step_number} • {event.action_type}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={cn(
                            "text-xs mb-1",
                            isCompleted ? 'bg-green-100 text-green-800' :
                            isInProgress ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                          )}>
                            {event.status}
                          </Badge>
                          <p className="text-xs text-muted-foreground">
                            {formatTimeAgo(event.timestamp)}
                          </p>
                          {event.duration_seconds && (
                            <p className="text-xs text-muted-foreground">
                              Duration: {event.duration_seconds}s
                            </p>
                          )}
                        </div>
                      </div>
                      
                      {event.description && (
                        <p className="text-sm">{event.description}</p>
                      )}
                      
                      {event.metadata && Object.keys(event.metadata).length > 0 && (
                        <div className="text-xs text-muted-foreground">
                          <details>
                            <summary className="cursor-pointer">View metadata</summary>
                            <pre className="mt-2 bg-gray-100 dark:bg-gray-800 p-2 rounded">
                              {JSON.stringify(event.metadata, null, 2)}
                            </pre>
                          </details>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
        
        {/* Regular Timeline */}
        {incident.timeline && incident.timeline.length > 0 && (
          <div className="space-y-4">
            {incident.sre_timeline && incident.sre_timeline.length > 0 && (
              <h3 className="text-lg font-medium flex items-center space-x-2">
                <Clock className="h-5 w-5 text-gray-600" />
                <span>General Timeline</span>
              </h3>
            )}
            {incident.timeline.map((event: any, index: number) => {
              // Use entry_type if status is not available, with fallback
              const status = event.status || event.entry_type || 'info';
              const isCompleted = status === 'completed' || status === 'resolved';
              const isInProgress = status === 'in_progress' || status === 'action';
              
              return (
                <Card key={index} className={cn(
                  "border-l-4",
                  isCompleted ? 'border-l-green-500' :
                  isInProgress ? 'border-l-blue-500' : 'border-l-gray-300'
                )}>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center",
                            isCompleted ? 'bg-green-100 text-green-600' :
                            isInProgress ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                          )}>
                            {isCompleted && <CheckCircle2 className="h-4 w-4" />}
                            {isInProgress && <Activity className="h-4 w-4" />}
                            {!isCompleted && !isInProgress && <Clock className="h-4 w-4" />}
                          </div>
                          <div>
                            <h4 className="font-medium">{event.title || event.action || 'Timeline Event'}</h4>
                            <p className="text-sm text-muted-foreground">{event.source || event.agent || 'System'}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={cn(
                            "text-xs mb-1",
                            isCompleted ? 'bg-green-100 text-green-800' :
                            isInProgress ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                          )}>
                            {status.replace('_', ' ')}
                          </Badge>
                          <p className="text-xs text-muted-foreground">
                            {formatTimeAgo(event.occurred_at || event.timestamp)}
                          </p>
                        </div>
                      </div>
                      
                      <p className="text-sm">{event.description || 'No description available'}</p>
                      {event.details && <p className="text-xs text-muted-foreground">{event.details}</p>}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
        
        {/* No timeline data */}
        {(!incident.sre_timeline || incident.sre_timeline.length === 0) && 
         (!incident.timeline || incident.timeline.length === 0) && (
          <Card>
            <CardContent className="p-6">
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Timeline Available</h3>
                <p className="text-muted-foreground">
                  Timeline events will appear here as the incident progresses
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    ),
    
     verification: (
       <div className="space-y-4">
         {/* SRE Verifications */}
         {incident.sre_verifications && incident.sre_verifications.length > 0 && (
           <div className="space-y-4">
             <h3 className="text-lg font-medium flex items-center space-x-2">
               <Zap className="h-5 w-5 text-blue-600" />
               <span>SRE Agent Verifications</span>
             </h3>
             {incident.sre_verifications.map((verification: any, index: number) => (
               <Card key={verification.id} className={cn(
                 "border-l-4",
                 verification.success ? 'border-l-green-500' : 'border-l-red-500'
               )}>
                 <CardContent className="p-4">
                   <div className="space-y-3">
                     <div className="flex items-center justify-between">
                       <h4 className="font-medium">{verification.description}</h4>
                       <Badge className={cn(
                         "text-xs",
                         verification.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                       )}>
                         {verification.success ? 'Passed' : 'Failed'}
                       </Badge>
                     </div>
                     
                     <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                       <div>
                         <span className="text-muted-foreground">Type:</span>
                         <span className="ml-2 font-medium">{verification.verification_type}</span>
                       </div>
                       {verification.expected_result && (
                         <div>
                           <span className="text-muted-foreground">Expected:</span>
                           <span className="ml-2 font-medium">{verification.expected_result}</span>
                         </div>
                       )}
                       {verification.actual_result && (
                         <div>
                           <span className="text-muted-foreground">Actual:</span>
                           <span className="ml-2 font-medium">{verification.actual_result}</span>
                         </div>
                       )}
                     </div>
                     
                     {verification.command_executed && (
                       <div>
                         <p className="text-sm font-medium mb-1">Command Executed</p>
                         <code className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded block">
                           {verification.command_executed}
                         </code>
                       </div>
                     )}
                     
                     <p className="text-xs text-muted-foreground">
                       Executed: {formatTimeAgo(verification.timestamp)}
                     </p>
                   </div>
                 </CardContent>
               </Card>
             ))}
           </div>
         )}
         
         {/* Legacy Verification Gates */}
         {incident.verification_gates && incident.verification_gates.length > 0 && (
           <div className="space-y-4">
             <h3 className="text-lg font-medium flex items-center space-x-2">
               <CheckCircle2 className="h-5 w-5 text-green-600" />
               <span>Verification Gates</span>
             </h3>
             {incident.verification_gates.map((gate: any, index: number) => (
              <Card key={index} className={cn(
                "border-l-4",
                gate.status === 'completed' ? 'border-l-green-500' :
                gate.status === 'in_progress' ? 'border-l-blue-500' : 'border-l-gray-300'
              )}>
                <CardContent className="p-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{gate.name}</h4>
                      <Badge className={cn(
                        "text-xs",
                        gate.status === 'completed' ? 'bg-green-100 text-green-800' :
                        gate.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                      )}>
                        {gate.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-muted-foreground">{gate.description}</p>
                    
                    <div className="space-y-2">
                      <Progress value={gate.progress} className="h-2" />
                      <div className="flex justify-between text-xs">
                        <span>Progress: {gate.progress}%</span>
                        <span>Time remaining: {gate.time_remaining}</span>
                      </div>
                    </div>
                    
                     <div className="grid grid-cols-2 gap-4 text-sm">
                       <div>
                         <span className="text-muted-foreground">Target:</span>
                         <span className="ml-2 font-medium">{gate.target_value}</span>
                       </div>
                       <div>
                         <span className="text-muted-foreground">Current:</span>
                         <span className="ml-2 font-medium">{gate.current_value}</span>
                       </div>
                     </div>
                  </div>
                </CardContent>
              </Card>
            ))}
           </div>
         )}
         
         {/* No verification data */}
         {(!incident.sre_verifications || incident.sre_verifications.length === 0) && 
          (!incident.verification_gates || incident.verification_gates.length === 0) && (
           <Card>
             <CardContent className="p-6">
               <div className="text-center py-8">
                 <CheckCircle2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                 <h3 className="text-lg font-medium mb-2">No Verifications Available</h3>
                 <p className="text-muted-foreground">
                   {incident.sre_execution ? 
                     "The SRE agent has not performed any verifications yet" :
                     "Verification steps will appear here when the SRE agent starts testing"
                   }
                 </p>
               </div>
             </CardContent>
           </Card>
         )}
       </div>
     ),
    
    hypotheses: (
      <div className="space-y-4">
        {incident.sre_hypotheses && incident.sre_hypotheses.length > 0 ? (
          incident.sre_hypotheses.map((hypothesis: any, index: number) => (
            <Card key={hypothesis.id} className={cn(
              "border-l-4",
              hypothesis.status === 'confirmed' ? 'border-l-green-500' :
              hypothesis.status === 'testing' ? 'border-l-blue-500' :
              hypothesis.status === 'rejected' ? 'border-l-red-500' : 'border-l-gray-300'
            )}>
              <CardContent className="p-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Hypothesis {index + 1}</h4>
                    <div className="flex items-center space-x-2">
                      <Badge className={cn(
                        "text-xs",
                        hypothesis.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                        hypothesis.status === 'testing' ? 'bg-blue-100 text-blue-800' :
                        hypothesis.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                      )}>
                        {hypothesis.status}
                      </Badge>
                      {hypothesis.confidence_score && (
                        <span className="text-sm text-muted-foreground">
                          {hypothesis.confidence_score}% confidence
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-sm">{hypothesis.hypothesis_text}</p>
                  
                  {hypothesis.reasoning && (
                    <div>
                      <p className="text-sm font-medium mb-1">Reasoning</p>
                      <p className="text-sm text-muted-foreground">{hypothesis.reasoning}</p>
                    </div>
                  )}
                  
                  {hypothesis.supporting_evidence && Object.keys(hypothesis.supporting_evidence).length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Supporting Evidence</p>
                      <div className="space-y-1">
                        {Object.entries(hypothesis.supporting_evidence).map(([key, value]: [string, any]) => (
                          <div key={key} className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                            <span className="text-sm"><strong>{key}:</strong> {String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs text-muted-foreground">
                    Created: {formatTimeAgo(hypothesis.created_at)}
                    {hypothesis.updated_at && hypothesis.updated_at !== hypothesis.created_at && 
                      ` • Updated: ${formatTimeAgo(hypothesis.updated_at)}`
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="p-6">
              <div className="text-center py-8">
                <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Hypotheses Available</h3>
                <p className="text-muted-foreground">
                  {incident.sre_execution ? 
                    "The SRE agent has not generated any hypotheses yet" :
                    "AI-generated hypotheses will appear here when SRE agent analyzes the incident"
                  }
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    ),
    
    provenance: (
      <div className="space-y-4">
        {incident.sre_provenance && incident.sre_provenance.length > 0 ? (
          incident.sre_provenance.map((prov: any, index: number) => (
            <Card key={prov.id} className="border-l-4 border-l-purple-500">
              <CardContent className="p-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Step {prov.step_id}</h4>
                    <div className="flex items-center space-x-2">
                      <Badge className="text-xs bg-purple-100 text-purple-800">
                        {prov.reasoning_type}
                      </Badge>
                      {prov.confidence && (
                        <span className="text-sm text-muted-foreground">
                          {prov.confidence}% confidence
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {prov.parent_step_id && (
                    <p className="text-sm text-muted-foreground">
                      Follows from step: {prov.parent_step_id}
                    </p>
                  )}
                  
                  {prov.reasoning_process && (
                    <div>
                      <p className="text-sm font-medium mb-1">Reasoning Process</p>
                      <p className="text-sm">{prov.reasoning_process}</p>
                    </div>
                  )}
                  
                  {prov.input_data && Object.keys(prov.input_data).length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Input Data</p>
                      <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-xs">
                        <pre>{JSON.stringify(prov.input_data, null, 2)}</pre>
                      </div>
                    </div>
                  )}
                  
                  {prov.output_conclusion && (
                    <div>
                      <p className="text-sm font-medium mb-1">Conclusion</p>
                      <p className="text-sm">{prov.output_conclusion}</p>
                    </div>
                  )}
                  
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Component: {prov.agent_component || 'Unknown'}</span>
                    <span>{formatTimeAgo(prov.timestamp)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="p-6">
              <div className="text-center py-8">
                <GitBranch className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Provenance Data Available</h3>
                <p className="text-muted-foreground">
                  {incident.sre_execution ? 
                    "The SRE agent has not recorded any reasoning chains yet" :
                    "Exact snippets from logs, metrics, and tickets will appear here when SRE agent analyzes data"
                  }
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    ),
    
    evidence: (
      <div className="space-y-4">
        {incident.sre_evidence && incident.sre_evidence.length > 0 ? (
          incident.sre_evidence.map((evidence: any, index: number) => (
            <Card key={evidence.id} className={cn(
              "border-l-4",
              evidence.relevance_score && evidence.relevance_score > 80 ? 'border-l-green-500' :
              evidence.relevance_score && evidence.relevance_score > 60 ? 'border-l-yellow-500' : 'border-l-blue-500'
            )}>
              <CardContent className="p-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">{evidence.evidence_type} from {evidence.source}</h4>
                    <div className="flex items-center space-x-2">
                      {evidence.relevance_score && (
                        <Badge className={cn(
                          "text-xs",
                          evidence.relevance_score > 80 ? 'bg-green-100 text-green-800' :
                          evidence.relevance_score > 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                        )}>
                          {evidence.relevance_score}% relevant
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium mb-1">Evidence Content</p>
                    <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-sm max-h-40 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">{evidence.content}</pre>
                    </div>
                  </div>
                  
                  {evidence.metadata && Object.keys(evidence.metadata).length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Metadata</p>
                      <div className="space-y-1">
                        {Object.entries(evidence.metadata).map(([key, value]: [string, any]) => (
                          <div key={key} className="flex items-start space-x-2">
                            <span className="text-xs text-muted-foreground min-w-0 flex-shrink-0">{key}:</span>
                            <span className="text-xs">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs text-muted-foreground">
                    Collected: {formatTimeAgo(evidence.collected_at)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="p-6">
              <div className="text-center py-8">
                <Code className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Evidence Available</h3>
                <p className="text-muted-foreground">
                  {incident.sre_execution ? 
                    "The SRE agent has not collected any evidence yet" :
                    "Comprehensive evidence search and analysis will appear here when SRE agent investigates"
                  }
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm" onClick={() => navigate('/app/incidents')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
             <div>
               <h1 className="text-2xl font-bold">{incident.title}</h1>
               <p className="text-muted-foreground">{incident.incident_id}</p>
             </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
          </div>
        </div>

        {/* Status Overview */}
        <Card>
          <CardContent className="p-6">
            <div className="grid gap-6 md:grid-cols-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Status</p>
                <Badge className={cn("text-sm", getStatusColor(incident.status))}>
                  {incident.status.charAt(0).toUpperCase() + incident.status.slice(1)}
                </Badge>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Severity</p>
                <Badge className={cn("text-sm", getSeverityColor(incident.severity))}>
                  {incident.severity.toUpperCase()}
                </Badge>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Confidence</p>
                <p className="text-lg font-bold">{incident.confidence}%</p>
              </div>
               <div className="space-y-2">
                 <p className="text-sm text-muted-foreground">Est. Resolution</p>
                 <p className="text-lg font-bold">{incident.estimated_resolution}</p>
               </div>
            </div>
          </CardContent>
        </Card>

        {/* Navigation Tabs */}
        <div className="border-b">
          <nav className="flex space-x-8">
            {[
              { id: 'execution', label: 'Execution', icon: Play },
              { id: 'agents', label: 'Agents', icon: Bot },
              { id: 'timeline', label: 'Timeline', icon: Clock },
              { id: 'hypotheses', label: 'Hypotheses', icon: Brain },
              { id: 'verification', label: 'Verification', icon: CheckCircle2 },
              { id: 'provenance', label: 'Provenance', icon: GitBranch },
              { id: 'evidence', label: 'Evidence', icon: Code }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={cn(
                    "flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors",
                    activeTab === tab.id
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div>
          {tabContent[activeTab]}
        </div>
      </div>
    </AppLayout>
  )
}
