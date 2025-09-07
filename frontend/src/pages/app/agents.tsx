import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { useAgents, useUpdateAgentStatus } from '@/hooks/useAgents'
import { useDeployAgent } from '@/hooks/useAgentDeployment'
import { DeployAgentModal } from '@/components/deploy-agent-modal'
import {
  Search, Filter, Plus, Play, Pause, Settings, Activity, Database, Server, Network, Shield, Monitor,
  List, Workflow, Mail, Container, Brain, ArrowDown, Layers, GitBranch, Eye, MoreHorizontal, FileText, Bot
} from 'lucide-react'

// Architecture view component with 3-tier architecture and animations
function ArchitectureView() {
  const [activeLayer, setActiveLayer] = useState<string | null>('presentation')
  
  const architectureLayers = [
    {
      id: 'presentation',
      name: 'Presentation Layer',
      description: 'User interfaces and client applications',
      components: [
        { id: 'web-app', name: 'Web Application', type: 'React SPA', agents: ['UI Monitor', 'Performance Agent'], status: 'healthy' },
        { id: 'mobile-app', name: 'Mobile App', type: 'React Native', agents: ['Mobile Analytics'], status: 'healthy' },
        { id: 'api-gateway', name: 'API Gateway', type: 'Kong/Nginx', agents: ['Rate Limiter', 'Auth Guard'], status: 'warning' }
      ]
    },
    {
      id: 'application',
      name: 'Application Layer',
      description: 'Business logic and application services',
      components: [
        { id: 'user-service', name: 'User Service', type: 'Node.js', agents: ['Service Monitor', 'Auto Scaler'], status: 'healthy' },
        { id: 'payment-service', name: 'Payment Service', type: 'Java Spring', agents: ['Transaction Monitor', 'Security Agent'], status: 'healthy' },
        { id: 'notification-service', name: 'Notification Service', type: 'Python Flask', agents: ['Queue Monitor', 'Delivery Agent'], status: 'error' },
        { id: 'analytics-service', name: 'Analytics Service', type: 'Python Django', agents: ['Data Processor', 'ML Agent'], status: 'healthy' }
      ]
    },
    {
      id: 'data',
      name: 'Data Layer',
      description: 'Databases and data storage systems',
      components: [
        { id: 'postgres', name: 'PostgreSQL', type: 'Primary DB', agents: ['DB Guardian', 'Query Optimizer', 'Backup Agent'], status: 'healthy' },
        { id: 'redis', name: 'Redis Cache', type: 'In-Memory DB', agents: ['Cache Manager', 'Memory Monitor'], status: 'healthy' },
        { id: 'elasticsearch', name: 'Elasticsearch', type: 'Search Engine', agents: ['Index Manager', 'Search Optimizer'], status: 'warning' },
        { id: 's3', name: 'AWS S3', type: 'Object Storage', agents: ['Storage Monitor', 'Cost Optimizer'], status: 'healthy' }
      ]
    }
  ]

  const ancillaryServices = [
    { id: 'rabbitmq', name: 'RabbitMQ', type: 'Message Broker', agents: ['Queue Manager', 'Message Router'], status: 'healthy', icon: Mail },
    { id: 'kubernetes', name: 'Kubernetes', type: 'Container Orchestrator', agents: ['Pod Manager', 'Node Monitor', 'Resource Scheduler'], status: 'healthy', icon: Container },
    { id: 'monitoring', name: 'Prometheus', type: 'Monitoring', agents: ['Metrics Collector', 'Alert Manager'], status: 'healthy', icon: Monitor },
    { id: 'logging', name: 'ELK Stack', type: 'Logging', agents: ['Log Aggregator', 'Log Analyzer'], status: 'warning', icon: FileText }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-500 border-green-500 bg-green-500/10'
      case 'warning': return 'text-yellow-500 border-yellow-500 bg-yellow-500/10'
      case 'error': return 'text-red-500 border-red-500 bg-red-500/10'
      default: return 'text-gray-500 border-gray-500 bg-gray-500/10'
    }
  }

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500'
      case 'warning': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-8">
      {/* Architecture Overview */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-muted rounded-full">
          <Layers className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">3-Tier Architecture</span>
        </div>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Interactive system architecture showing agent deployment across all infrastructure layers.
          Click on any component to see active agents and their current activities.
        </p>
      </div>

      {/* Architecture Layers */}
      <div className="space-y-12">
        {architectureLayers.map((layer, layerIndex) => (
          <div key={layer.id} className="relative">
            {/* Layer Header */}
            <div className="flex items-center justify-between mb-6">
              <div 
                className={cn(
                  "flex items-center space-x-3 p-4 rounded-lg border-2 cursor-pointer transition-all duration-300",
                  activeLayer === layer.id 
                    ? "border-primary bg-primary/5" 
                    : "border-muted hover:border-muted-foreground/50"
                )}
                onClick={() => setActiveLayer(activeLayer === layer.id ? null : layer.id)}
              >
                <div className={cn(
                  "w-3 h-3 rounded-full transition-all duration-300",
                  activeLayer === layer.id ? "bg-primary animate-pulse" : "bg-muted-foreground"
                )} />
                <div>
                  <h3 className="text-lg font-semibold">{layer.name}</h3>
                  <p className="text-sm text-muted-foreground">{layer.description}</p>
                </div>
              </div>
              
              {/* Layer Stats */}
              <div className="flex items-center space-x-4">
                <div className="text-center">
                  <div className="text-sm font-bold">{layer.components.length}</div>
                  <div className="text-xs text-muted-foreground">Services</div>
                </div>
                <div className="text-center">
                  <div className="text-sm font-bold text-green-600">
                    {layer.components.reduce((acc, comp) => acc + comp.agents.length, 0)}
                  </div>
                  <div className="text-xs text-muted-foreground">Agents</div>
                </div>
              </div>
            </div>

            {/* Components Grid */}
            <div className={cn(
              "grid gap-4 md:grid-cols-2 lg:grid-cols-4 transition-all duration-500",
              activeLayer === layer.id ? "opacity-100 scale-100" : "opacity-70 scale-95"
            )}>
              {layer.components.map((component) => (
                <Card 
                  key={component.id}
                  className={cn(
                    "relative overflow-hidden transition-all duration-300 hover:shadow-lg cursor-pointer",
                    getStatusColor(component.status),
                    activeLayer === layer.id && "transform hover:scale-105"
                  )}
                >
                  {/* Status Indicator */}
                  <div className={cn(
                    "absolute top-2 right-2 w-3 h-3 rounded-full animate-pulse",
                    getStatusDot(component.status)
                  )} />

                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-2">
                      <Server className="h-5 w-5" />
                      <div>
                        <CardTitle className="text-sm">{component.name}</CardTitle>
                        <CardDescription className="text-xs">{component.type}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      <div className="text-xs font-medium text-muted-foreground">Active Agents:</div>
                      {component.agents.map((agent, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <div className={cn(
                            "w-1.5 h-1.5 rounded-full animate-pulse",
                            getStatusDot(component.status)
                          )} />
                          <span className="text-xs">{agent}</span>
                          {activeLayer === layer.id && (
                            <div className="ml-auto">
                              <Brain className="h-3 w-3 text-primary animate-pulse" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Agent Activity Animation */}
                    {activeLayer === layer.id && (
                      <div className="mt-3 pt-3 border-t">
                        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                          <Activity className="h-3 w-3 animate-pulse" />
                          <span>Analyzing...</span>
                          <div className="flex space-x-1 ml-2">
                            <div className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-1 h-1 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Data Flow Arrow */}
            {layerIndex < architectureLayers.length - 1 && (
              <div className="flex justify-center my-8">
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <ArrowDown className="h-6 w-6 animate-bounce" />
                  <span className="text-sm">Data Flow</span>
                  <ArrowDown className="h-6 w-6 animate-bounce" style={{ animationDelay: '200ms' }} />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Ancillary Services */}
      <div className="mt-12 pt-8 border-t">
        <div className="text-center mb-8">
          <h3 className="text-xl font-semibold mb-2">Supporting Infrastructure</h3>
          <p className="text-muted-foreground">Essential services that support the application stack</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {ancillaryServices.map((service) => {
            const Icon = service.icon
            return (
              <Card 
                key={service.id}
                className={cn(
                  "relative transition-all duration-300 hover:shadow-lg cursor-pointer",
                  getStatusColor(service.status)
                )}
              >
                {/* Service Icon */}
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center border-2 bg-background",
                    getStatusColor(service.status)
                  )}>
                    <Icon className="h-4 w-4" />
                  </div>
                </div>

                <CardHeader className="pt-8 text-center">
                  <CardTitle className="text-sm">{service.name}</CardTitle>
                  <CardDescription className="text-xs">{service.type}</CardDescription>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="space-y-2">
                    {service.agents.map((agent, index) => (
                      <div key={index} className="flex items-center justify-between text-xs">
                        <span>{agent}</span>
                        <div className={cn(
                          "w-2 h-2 rounded-full animate-pulse",
                          getStatusDot(service.status)
                        )} />
                      </div>
                    ))}
                  </div>

                  {/* Connection Lines Animation */}
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center justify-center space-x-1">
                      <div className="h-0.5 w-4 bg-gradient-to-r from-transparent to-primary animate-pulse" />
                      <GitBranch className="h-3 w-3 text-primary" />
                      <div className="h-0.5 w-4 bg-gradient-to-l from-transparent to-primary animate-pulse" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Real-time Activity Feed */}
      <Card className="bg-muted/20">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-primary animate-pulse" />
            <span>Real-time Agent Activity</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {[
              { agent: 'DB Guardian', action: 'Optimized slow query in orders table', layer: 'Data', time: '2s ago' },
              { agent: 'Auto Scaler', action: 'Scaled up user-service replicas', layer: 'Application', time: '15s ago' },
              { agent: 'Security Agent', action: 'Blocked suspicious login attempt', layer: 'Presentation', time: '32s ago' },
              { agent: 'Queue Manager', action: 'Rebalanced RabbitMQ queues', layer: 'Infrastructure', time: '45s ago' },
              { agent: 'Cache Manager', action: 'Evicted stale Redis keys', layer: 'Data', time: '1m ago' },
              { agent: 'Pod Manager', action: 'Restarted unhealthy pod', layer: 'Infrastructure', time: '2m ago' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-background/50">
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{activity.agent}</span>
                    <Badge variant="outline" className="text-xs">{activity.layer}</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">{activity.action}</div>
                </div>
                <div className="text-xs text-muted-foreground">{activity.time}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// List view component - now using real API data
function ListView() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<any>(null)
  
  // Fetch real agents data from API
  const { data: agentsData, isLoading, error } = useAgents()
  const agents = agentsData || []
  
  console.log('Agents from API:', agents) // Debug log

  // Calculate dynamic agent categories based on actual data
  const agentCategories = React.useMemo(() => {
    const categories = agents.reduce((acc: any, agent: any) => {
      const type = agent.type || 'Unknown'
      const typeName = type.charAt(0).toUpperCase() + type.slice(1).toLowerCase()
      
      if (!acc[typeName]) {
        acc[typeName] = { 
          name: typeName, 
          count: 0, 
          active: 0, 
          icon: getIconForType(type), 
          color: getColorForType(type) 
        }
      }
      
      acc[typeName].count++
      if (agent.status === 'active' || agent.status === 'deploying') {
        acc[typeName].active++
      }
      
      return acc
    }, {})
    
    return Object.values(categories)
  }, [agents])

  const filteredAgents = agents.filter((agent: any) => 
    agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Helper functions for dynamic categories
  function getIconForType(type: string) {
    switch (type.toLowerCase()) {
      case 'compute': return Server
      case 'database': return Database
      case 'network': return Network
      case 'security': return Shield
      case 'monitoring': return Monitor
      default: return Bot
    }
  }

  function getColorForType(type: string) {
    switch (type.toLowerCase()) {
      case 'compute': return "text-blue-600"
      case 'database': return "text-green-600"
      case 'network': return "text-purple-600"
      case 'security': return "text-red-600"
      case 'monitoring': return "text-orange-600"
      default: return "text-gray-600"
    }
  }

  // Handle loading and error states
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          <span>Loading agents...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <p className="text-red-600 mb-2">Failed to load agents</p>
          <p className="text-sm text-muted-foreground">Please try refreshing the page</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Agent Categories Overview */}
      <div className="grid gap-4 md:grid-cols-5">
        {agentCategories.map((category) => {
          const Icon = category.icon
          return (
            <Card key={category.name} className="card-hover">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <Icon className={cn("h-8 w-8", category.color)} />
                  <div className="text-right">
                    <div className="text-2xl font-bold">{category.active}</div>
                    <div className="text-xs text-muted-foreground">of {category.count} active</div>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="font-medium">{category.name}</div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search agents..." className="pl-10" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        </div>
        <Button variant="outline"><Filter className="mr-2 h-4 w-4" />Filter</Button>
      </div>

      {/* Agents List */}
      <div className="grid gap-6 lg:grid-cols-2">
        {filteredAgents.map((agent) => (
          <Card key={agent.id} className="card-hover">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", 
                    agent.status === 'active' ? "bg-green-100 dark:bg-green-900/20" : "bg-gray-100 dark:bg-gray-900/20")}>
                    <Server className={cn("h-5 w-5", agent.status === 'active' ? "text-green-600" : "text-gray-600")} />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="text-xs">{agent.type}</Badge>
                      <Badge variant={agent.status === 'active' ? 'default' : 'secondary'} className="text-xs">{agent.status}</Badge>
                      <span className="text-xs text-muted-foreground">{agent.confidence}% confidence</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="icon" onClick={() => setSelectedAgent(agent)}>
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    {agent.status === 'active' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </Button>
                  <Button variant="ghost" size="icon"><Settings className="h-4 w-4" /></Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription className="mb-4">{agent.description}</CardDescription>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">{agent.incidents}</div>
                  <div className="text-xs text-muted-foreground">Incidents</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">{agent.confidence}%</div>
                  <div className="text-xs text-muted-foreground">Success</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-600">{agent.layer}</div>
                  <div className="text-xs text-muted-foreground">Layer</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm font-medium">Recent Actions</div>
                {agent.actions.slice(0, 2).map((action, index) => (
                  <div key={index} className="flex items-start space-x-2 text-xs">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-1.5" />
                    <div className="flex-1">
                      <div className="text-foreground">{action.description}</div>
                      <div className="text-muted-foreground">{action.time}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t">
                <div className="text-xs text-muted-foreground">Last action: {agent.lastAction || agent.last_action || 'No recent actions'}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Agent Details Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{selectedAgent.name}</CardTitle>
                  <CardDescription>{selectedAgent.description}</CardDescription>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setSelectedAgent(null)}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h4 className="font-medium mb-3">Recent Activity</h4>
                  <div className="space-y-3">
                    {selectedAgent.actions.map((action, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-muted/50">
                        <div className="w-2 h-2 rounded-full bg-green-500 mt-2" />
                        <div className="flex-1">
                          <div className="font-medium text-sm">{action.description}</div>
                          <div className="text-xs text-muted-foreground">{action.time}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Performance Metrics</h4>
                  <div className="grid grid-cols-3 gap-4">
                    {Object.entries(selectedAgent.metrics).map(([key, value]) => (
                      <div key={key} className="text-center p-3 rounded-lg bg-muted/50">
                        <div className="text-lg font-bold">{value}</div>
                        <div className="text-xs text-muted-foreground capitalize">{key}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

// Main agents page component
export function AgentsPage() {
  const [currentView, setCurrentView] = useState<'list' | 'architecture'>('list')
  const [isDeployModalOpen, setIsDeployModalOpen] = useState(false)
  const deployAgentMutation = useDeployAgent()

  const handleDeployAgent = async (agentData: any) => {
    try {
      const result = await deployAgentMutation.mutateAsync(agentData)
      setIsDeployModalOpen(false)
      console.log('Agent deployed successfully:', result.agent.name)
      // The useDeployAgent hook automatically invalidates the agents list
    } catch (error) {
      console.error('Failed to deploy agent:', error)
      // Show error message here
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header with View Toggle */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Agents</h1>
            <p className="text-muted-foreground mt-2">
              Manage your autonomous AI agents across different infrastructure layers
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* View Toggle */}
            <div className="flex items-center rounded-lg border p-1">
              <Button
                variant={currentView === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('list')}
                className="h-8"
              >
                <List className="mr-2 h-4 w-4" />
                List View
              </Button>
              <Button
                variant={currentView === 'architecture' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('architecture')}
                className="h-8"
              >
                <Workflow className="mr-2 h-4 w-4" />
                Architecture
              </Button>
            </div>
            
            <Button onClick={() => setIsDeployModalOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Deploy Agent
            </Button>
          </div>
        </div>

        {/* View Content */}
        {currentView === 'list' ? <ListView /> : <ArchitectureView />}

        {/* Deploy Agent Modal */}
        <DeployAgentModal
          isOpen={isDeployModalOpen}
          onClose={() => setIsDeployModalOpen(false)}
          onDeploy={handleDeployAgent}
        />
      </div>
    </AppLayout>
  )
}
