import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useAvailableIntegrations, useAvailableAgents, useCompleteOnboarding } from '@/hooks/useOnboarding'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { cn } from '@/lib/utils'
import { 
  Building2, 
  Link, 
  Shield, 
  Server, 
  Database, 
  Network, 
  Monitor, 
  Bot,
  Users,
  Mail,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Zap,
  Settings,
  Check,
  X
} from 'lucide-react'

// Form schemas for each step
const companySchema = z.object({
  organizationName: z.string().min(2, 'Organization name must be at least 2 characters'),
  domain: z.string().optional(),
  description: z.string().optional(),
})

const integrationsSchema = z.object({
  selectedIntegrations: z.array(z.string()).min(0, 'Select at least one integration'),
})

const agentsSchema = z.object({
  selectedAgents: z.array(z.string()).min(0, 'Select at least one agent'),
})

const policiesSchema = z.object({
  autoApprovalThreshold: z.number().min(50).max(100),
  requireApprovalForHigh: z.boolean(),
  requireApprovalForMedium: z.boolean(),
  enableRollback: z.boolean(),
})

const teamSchema = z.object({
  teamMembers: z.array(z.object({
    email: z.string().email('Invalid email address'),
    role: z.enum(['admin', 'member', 'viewer']),
  })),
})

type CompanyFormValues = z.infer<typeof companySchema>
type IntegrationsFormValues = z.infer<typeof integrationsSchema>
type AgentsFormValues = z.infer<typeof agentsSchema>
type PoliciesFormValues = z.infer<typeof policiesSchema>
type TeamFormValues = z.infer<typeof teamSchema>

// Available integrations (fallback data)
const availableIntegrations = [
  // Communication & Collaboration
  { id: 'slack', name: 'Slack', category: 'Communication', icon: '💬', description: 'Team communication and incident notifications', popular: true },
  { id: 'teams', name: 'Microsoft Teams', category: 'Communication', icon: '👥', description: 'Enterprise collaboration and video calls' },
  { id: 'discord', name: 'Discord', category: 'Communication', icon: '🎮', description: 'Community chat and voice channels' },
  { id: 'zoom', name: 'Zoom', category: 'Communication', icon: '📹', description: 'Video conferencing and webinars' },
  { id: 'webex', name: 'Cisco Webex', category: 'Communication', icon: '🌐', description: 'Enterprise video meetings' },

  // Monitoring & Observability
  { id: 'datadog', name: 'Datadog', category: 'Monitoring', icon: '🐕', description: 'Infrastructure monitoring and analytics', popular: true },
  { id: 'newrelic', name: 'New Relic', category: 'Monitoring', icon: '📊', description: 'Application performance monitoring' },
  { id: 'prometheus', name: 'Prometheus', category: 'Monitoring', icon: '🔥', description: 'Metrics collection and alerting' },
  { id: 'grafana', name: 'Grafana', category: 'Monitoring', icon: '📈', description: 'Metrics visualization and dashboards' },
  { id: 'splunk', name: 'Splunk', category: 'Monitoring', icon: '🔍', description: 'Log analysis and security monitoring' },

  // Incident Management
  { id: 'pagerduty', name: 'PagerDuty', category: 'Incident Management', icon: '🚨', description: 'Incident response and alerting', popular: true },
  { id: 'opsgenie', name: 'Atlassian Opsgenie', category: 'Incident Management', icon: '⚡', description: 'Alert management and on-call scheduling' },
  { id: 'victorops', name: 'VictorOps', category: 'Incident Management', icon: '🎯', description: 'Collaborative incident management' },
  { id: 'servicenow', name: 'ServiceNow', category: 'Incident Management', icon: '🎫', description: 'Enterprise service management' },
  { id: 'freshservice', name: 'Freshservice', category: 'Incident Management', icon: '🍃', description: 'IT service management platform' },

  // Project Management
  { id: 'jira', name: 'Jira', category: 'Project Management', icon: '📋', description: 'Issue tracking and project management', popular: true },
  { id: 'asana', name: 'Asana', category: 'Project Management', icon: '✅', description: 'Team task and project management' },
  { id: 'trello', name: 'Trello', category: 'Project Management', icon: '📌', description: 'Visual project boards and cards' },
  { id: 'monday', name: 'Monday.com', category: 'Project Management', icon: '📅', description: 'Work operating system and collaboration' },
  { id: 'notion', name: 'Notion', category: 'Project Management', icon: '📝', description: 'All-in-one workspace and documentation' },

  // Cloud & Infrastructure
  { id: 'aws', name: 'AWS', category: 'Cloud', icon: '☁️', description: 'Amazon Web Services integration', popular: true },
  { id: 'azure', name: 'Microsoft Azure', category: 'Cloud', icon: '🌤️', description: 'Microsoft cloud platform services' },
  { id: 'gcp', name: 'Google Cloud', category: 'Cloud', icon: '🌩️', description: 'Google Cloud Platform services' },
  { id: 'kubernetes', name: 'Kubernetes', category: 'Cloud', icon: '⚓', description: 'Container orchestration platform' },
  { id: 'docker', name: 'Docker', category: 'Cloud', icon: '🐳', description: 'Containerization and deployment' },
]

// Available agents (fallback data)
const availableAgents = [
  // Infrastructure Monitoring
  { id: 'ec2-monitor', name: 'EC2 Monitor', category: 'Infrastructure', icon: Server, description: 'Monitors EC2 instances and auto-scales resources', popular: true },
  { id: 'k8s-guardian', name: 'Kubernetes Guardian', category: 'Infrastructure', icon: Server, description: 'Monitors pods, nodes, and cluster health' },
  { id: 'load-balancer-agent', name: 'Load Balancer Agent', category: 'Infrastructure', icon: Server, description: 'Optimizes traffic distribution and scaling' },
  { id: 'storage-optimizer', name: 'Storage Optimizer', category: 'Infrastructure', icon: Server, description: 'Manages disk space and performance' },
  { id: 'resource-scheduler', name: 'Resource Scheduler', category: 'Infrastructure', icon: Server, description: 'Optimizes resource allocation and costs' },

  // Database Management
  { id: 'database-healer', name: 'Database Healer', category: 'Database', icon: Database, description: 'Optimizes queries and manages connections', popular: true },
  { id: 'mysql-guardian', name: 'MySQL Guardian', category: 'Database', icon: Database, description: 'Monitors MySQL performance and health' },
  { id: 'postgres-optimizer', name: 'PostgreSQL Optimizer', category: 'Database', icon: Database, description: 'Tunes PostgreSQL configurations automatically' },
  { id: 'redis-manager', name: 'Redis Manager', category: 'Database', icon: Database, description: 'Manages Redis cache and memory optimization' },
  { id: 'backup-sentinel', name: 'Backup Sentinel', category: 'Database', icon: Database, description: 'Automates database backups and recovery' },

  // Network & Security
  { id: 'network-analyzer', name: 'Network Analyzer', category: 'Network', icon: Network, description: 'Monitors network performance and security', popular: true },
  { id: 'firewall-guardian', name: 'Firewall Guardian', category: 'Network', icon: Shield, description: 'Manages firewall rules and security policies' },
  { id: 'ssl-monitor', name: 'SSL Monitor', category: 'Network', icon: Shield, description: 'Tracks SSL certificates and renewals' },
  { id: 'ddos-protector', name: 'DDoS Protector', category: 'Network', icon: Shield, description: 'Detects and mitigates DDoS attacks' },
  { id: 'vpn-manager', name: 'VPN Manager', category: 'Network', icon: Network, description: 'Manages VPN connections and tunnels' },

  // Application Performance
  { id: 'app-performance-agent', name: 'App Performance Agent', category: 'Application', icon: Monitor, description: 'Monitors application response times and errors', popular: true },
  { id: 'memory-optimizer', name: 'Memory Optimizer', category: 'Application', icon: Monitor, description: 'Optimizes application memory usage' },
  { id: 'thread-analyzer', name: 'Thread Analyzer', category: 'Application', icon: Monitor, description: 'Monitors thread pools and concurrency' },
  { id: 'error-tracker', name: 'Error Tracker', category: 'Application', icon: Monitor, description: 'Tracks and analyzes application errors' },
  { id: 'cache-manager', name: 'Cache Manager', category: 'Application', icon: Monitor, description: 'Optimizes application caching strategies' },

  // DevOps & Deployment
  { id: 'deployment-agent', name: 'Deployment Agent', category: 'DevOps', icon: Zap, description: 'Manages deployments and rollbacks', popular: true },
  { id: 'pipeline-optimizer', name: 'Pipeline Optimizer', category: 'DevOps', icon: Zap, description: 'Optimizes CI/CD pipeline performance' },
  { id: 'container-manager', name: 'Container Manager', category: 'DevOps', icon: Zap, description: 'Manages container lifecycles and health' },
  { id: 'artifact-guardian', name: 'Artifact Guardian', category: 'DevOps', icon: Zap, description: 'Manages build artifacts and dependencies' },
  { id: 'release-coordinator', name: 'Release Coordinator', category: 'DevOps', icon: Zap, description: 'Coordinates multi-service deployments' },
]

export function OnboardingPage() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  
  // Local state for selections to ensure UI updates
  const [selectedIntegrations, setSelectedIntegrations] = useState<string[]>([])
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  
  // API hooks
  const { data: integrationsData } = useAvailableIntegrations()
  const { data: agentsData } = useAvailableAgents()
  const completeOnboardingMutation = useCompleteOnboarding()

  // Use API data if available, otherwise fallback to mock data
  const apiIntegrations = integrationsData?.integrations || availableIntegrations
  const apiAgents = agentsData?.agents || availableAgents

  // Form instances for each step
  const companyForm = useForm<CompanyFormValues>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      organizationName: '',
      domain: '',
      description: '',
    },
  })

  const integrationsForm = useForm<IntegrationsFormValues>({
    resolver: zodResolver(integrationsSchema),
    defaultValues: {
      selectedIntegrations: [],
    },
  })
  
  // Sync local state with form state
  const syncIntegrationsWithForm = (newSelections: string[]) => {
    setSelectedIntegrations(newSelections)
    integrationsForm.setValue('selectedIntegrations', newSelections)
  }

  const agentsForm = useForm<AgentsFormValues>({
    resolver: zodResolver(agentsSchema),
    defaultValues: {
      selectedAgents: [],
    },
  })
  
  // Sync local state with form state
  const syncAgentsWithForm = (newSelections: string[]) => {
    setSelectedAgents(newSelections)
    agentsForm.setValue('selectedAgents', newSelections)
  }

  const policiesForm = useForm<PoliciesFormValues>({
    resolver: zodResolver(policiesSchema),
    defaultValues: {
      autoApprovalThreshold: 85,
      requireApprovalForHigh: true,
      requireApprovalForMedium: false,
      enableRollback: true,
    },
  })



  const steps = [
    { id: 1, title: 'Company', description: 'Basic info', icon: Building2 },
    { id: 2, title: 'Integrations', description: 'Connect tools', icon: Link },
    { id: 3, title: 'Agents', description: 'Choose AI agents', icon: Bot },
    { id: 4, title: 'Policies', description: 'Set automation rules', icon: Settings },
  ]

  const progress = (currentStep / steps.length) * 100

  const handleNext = async () => {
    let isValid = false

    // Validate current step
    switch (currentStep) {
      case 1:
        isValid = await companyForm.trigger()
        break
      case 2:
        // Sync local state to form before validation
        syncIntegrationsWithForm(selectedIntegrations)
        isValid = await integrationsForm.trigger()
        break
      case 3:
        // Sync local state to form before validation
        syncAgentsWithForm(selectedAgents)
        isValid = await agentsForm.trigger()
        break
      case 4:
        isValid = await policiesForm.trigger()
        break
    }

    if (!isValid) return

    if (currentStep === 4) {
      // Complete onboarding
      const companyData = companyForm.getValues()
      const policiesData = policiesForm.getValues()

      completeOnboardingMutation.mutate({
        company: {
          organization_name: companyData.organizationName,
          domain: companyData.domain,
          description: companyData.description,
        },
        integrations: {
          selected_integrations: selectedIntegrations,
        },
        agents: {
          selected_agents: selectedAgents,
        },
        policies: {
          auto_approval_threshold: policiesData.autoApprovalThreshold,
          require_approval_for_high: policiesData.requireApprovalForHigh,
          require_approval_for_medium: policiesData.requireApprovalForMedium,
          enable_rollback: policiesData.enableRollback,
        },
        team: {
          team_members: [],
        },
      }, {
        onSuccess: (response) => {
          // Store organization name in localStorage for display
          localStorage.setItem('organization_name', companyData.organizationName)
          // Redirect to dashboard after successful onboarding
          navigate('/app', { replace: true })
        },
        onError: (error) => {
          console.error('Onboarding failed:', error)
          // You could show a toast/notification here
        },
      })
    } else {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                  <Building2 className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Company Setup</CardTitle>
                  <CardDescription>Tell us about your organization to get started</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <Form {...companyForm}>
                <form className="space-y-6">
                  <FormField
                    control={companyForm.control}
                    name="organizationName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Organization Name *</FormLabel>
                        <FormControl>
                          <Input placeholder="Acme Corporation" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={companyForm.control}
                    name="domain"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company Domain</FormLabel>
                        <FormControl>
                          <Input placeholder="acme.com" {...field} />
                        </FormControl>
                        <FormDescription>
                          This will be used for SSO and team member verification
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={companyForm.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Textarea 
                            placeholder="Brief description of your organization..."
                            className="min-h-[100px]"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </form>
              </Form>
            </CardContent>
          </Card>
        )

      case 2:
        return (
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                  <Link className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Connect Systems</CardTitle>
                  <CardDescription>Connect your existing tools and services for comprehensive monitoring</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Form {...integrationsForm}>
                <form>
                  <FormField
                    control={integrationsForm.control}
                    name="selectedIntegrations"
                    render={({ field }) => {
                      console.log('Local selectedIntegrations:', selectedIntegrations) // Debug log
                      console.log('Form field value:', field.value) // Debug log
                      
                      const handleToggle = (integrationId: string) => {
                        const isCurrentlySelected = selectedIntegrations.includes(integrationId)
                        const newSelection = isCurrentlySelected
                          ? selectedIntegrations.filter(id => id !== integrationId)
                          : [...selectedIntegrations, integrationId]
                        
                        syncIntegrationsWithForm(newSelection)
                        console.log('Selection changed:', { integrationId, isCurrentlySelected, newSelection }) // Debug log
                      }

                      // Group integrations by category
                      const groupedIntegrations = apiIntegrations.reduce((acc, integration) => {
                        const category = 'category' in integration ? integration.category : 'Other'
                        if (!acc[category]) acc[category] = []
                        acc[category].push(integration)
                        return acc
                      }, {} as Record<string, any[]>)

                      return (
                        <FormItem>
                          <div className="space-y-8">
                            {Object.entries(groupedIntegrations).map(([category, integrations]) => (
                              <div key={category} className="space-y-4">
                                <div className="flex items-center justify-between">
                                  <h3 className="text-lg font-semibold text-foreground">{category}</h3>
                                  <Badge variant="outline" className="text-xs">
                                    {integrations.length} available
                                  </Badge>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                  {integrations.map((integration) => {
                                    const isSelected = selectedIntegrations.includes(integration.id)
                                    const isPopular = 'popular' in integration && integration.popular
                                    return (
                                      <Card 
                                        key={integration.id}
                                        className={cn(
                                          "transition-all duration-200 hover:shadow-md border-2 relative",
                                          isSelected 
                                            ? "ring-2 ring-primary border-primary bg-primary/5" 
                                            : "border-muted hover:border-muted-foreground/50"
                                        )}
                                      >
                                        {isPopular && (
                                          <div className="absolute -top-2 -right-2 z-10">
                                            <Badge className="bg-orange-500 text-white text-xs px-2 py-1">
                                              Popular
                                            </Badge>
                                          </div>
                                        )}
                                        <CardContent className="p-4">
                                          <div className="space-y-4">
                                            <div className="flex items-start gap-3 cursor-pointer"
                                                 onClick={(e) => {
                                                   e.preventDefault()
                                                   e.stopPropagation()
                                                   handleToggle(integration.id)
                                                 }}>
                                              <div className="text-2xl">{'icon' in integration ? integration.icon : '🔗'}</div>
                                              <div className="flex-1">
                                                <h4 className="font-semibold">{integration.name}</h4>
                                                <p className="text-sm text-muted-foreground mt-1">
                                                  {integration.description}
                                                </p>
                                              </div>
                                              <div className={cn(
                                                "w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0",
                                                isSelected 
                                                  ? "bg-primary border-primary text-primary-foreground" 
                                                  : "border-muted-foreground/25"
                                              )}>
                                                {isSelected && <Check className="h-3 w-3" />}
                                              </div>
                                            </div>
                                            {isSelected && (
                                              <div className="flex gap-2 pt-2 border-t">
                                                <Button 
                                                  size="sm" 
                                                  className="flex-1"
                                                  onClick={(e) => {
                                                    e.stopPropagation()
                                                    // TODO: Open setup modal
                                                    console.log(`Setup ${integration.name}`)
                                                  }}
                                                >
                                                  Setup Now
                                                </Button>
                                                <Button 
                                                  variant="outline" 
                                                  size="sm" 
                                                  className="flex-1"
                                                  onClick={(e) => {
                                                    e.stopPropagation()
                                                    console.log(`Skip ${integration.name} setup`)
                                                  }}
                                                >
                                                  Skip for Now
                                                </Button>
                                              </div>
                                            )}
                                          </div>
                                        </CardContent>
                                      </Card>
                                    )
                                  })}
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="mt-4 flex items-center justify-between">
                            <div className="p-3 bg-muted rounded-lg flex-1">
                              <p className="text-sm text-muted-foreground">
                                Selected: {selectedIntegrations.length} integration{selectedIntegrations.length !== 1 ? 's' : ''}
                                {selectedIntegrations.length > 0 && (
                                  <span className="ml-2 text-xs">({selectedIntegrations.join(', ')})</span>
                                )}
                              </p>
                            </div>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                syncIntegrationsWithForm([])
                                console.log('Cleared all selections')
                              }}
                              className="ml-2"
                            >
                              Clear All
                            </Button>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )
                    }}
                  />
                </form>
              </Form>
            </CardContent>
          </Card>
        )

      case 3:
        return (
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Choose AI Agents</CardTitle>
                  <CardDescription>Select autonomous agents to monitor and heal your infrastructure</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Form {...agentsForm}>
                <form>
                  <FormField
                    control={agentsForm.control}
                    name="selectedAgents"
                    render={({ field }) => {
                      console.log('Local selectedAgents:', selectedAgents) // Debug log
                      console.log('Form agent field value:', field.value) // Debug log
                      
                      const handleToggle = (agentId: string) => {
                        const isCurrentlySelected = selectedAgents.includes(agentId)
                        const newSelection = isCurrentlySelected
                          ? selectedAgents.filter(id => id !== agentId)
                          : [...selectedAgents, agentId]
                        
                        syncAgentsWithForm(newSelection)
                        console.log('Agent selection changed:', { agentId, isCurrentlySelected, newSelection }) // Debug log
                      }

                      // Group agents by category
                      const groupedAgents = apiAgents.reduce((acc, agent) => {
                        const category = 'category' in agent ? agent.category : 'Other'
                        if (!acc[category]) acc[category] = []
                        acc[category].push(agent)
                        return acc
                      }, {} as Record<string, any[]>)

                      return (
                        <FormItem>
                          <div className="space-y-8">
                            {Object.entries(groupedAgents).map(([category, agents]) => (
                              <div key={category} className="space-y-4">
                                <div className="flex items-center justify-between">
                                  <h3 className="text-lg font-semibold text-foreground">{category}</h3>
                                  <Badge variant="outline" className="text-xs">
                                    {agents.length} available
                                  </Badge>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2">
                                  {agents.map((agent) => {
                                    const isSelected = selectedAgents.includes(agent.id)
                                    const IconComponent = 'icon' in agent ? agent.icon : Bot
                                    const isPopular = 'popular' in agent && agent.popular
                                    return (
                                      <Card 
                                        key={agent.id}
                                        className={cn(
                                          "transition-all duration-200 hover:shadow-md border-2 relative",
                                          isSelected 
                                            ? "ring-2 ring-primary border-primary bg-primary/5" 
                                            : "border-muted hover:border-muted-foreground/50"
                                        )}
                                      >
                                        {isPopular && (
                                          <div className="absolute -top-2 -right-2 z-10">
                                            <Badge className="bg-orange-500 text-white text-xs px-2 py-1">
                                              Popular
                                            </Badge>
                                          </div>
                                        )}
                                        <CardContent className="p-4">
                                          <div className="space-y-4">
                                            <div className="flex items-start gap-3 cursor-pointer"
                                                 onClick={(e) => {
                                                   e.preventDefault()
                                                   e.stopPropagation()
                                                   handleToggle(agent.id)
                                                 }}>
                                              <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                                                <IconComponent className="h-4 w-4" />
                                              </div>
                                              <div className="flex-1">
                                                <h4 className="font-semibold">{agent.name}</h4>
                                                <p className="text-sm text-muted-foreground mt-1">
                                                  {agent.description}
                                                </p>
                                              </div>
                                              <div className={cn(
                                                "w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0",
                                                isSelected 
                                                  ? "bg-primary border-primary text-primary-foreground" 
                                                  : "border-muted-foreground/25"
                                              )}>
                                                {isSelected && <Check className="h-3 w-3" />}
                                              </div>
                                            </div>
                                            {isSelected && (
                                              <div className="flex gap-2 pt-2 border-t">
                                                <Button 
                                                  size="sm" 
                                                  className="flex-1"
                                                  onClick={(e) => {
                                                    e.stopPropagation()
                                                    // TODO: Open setup modal
                                                    console.log(`Setup ${agent.name}`)
                                                  }}
                                                >
                                                  Configure
                                                </Button>
                                                <Button 
                                                  variant="outline" 
                                                  size="sm" 
                                                  className="flex-1"
                                                  onClick={(e) => {
                                                    e.stopPropagation()
                                                    console.log(`Skip ${agent.name} setup`)
                                                  }}
                                                >
                                                  Skip for Now
                                                </Button>
                                              </div>
                                            )}
                                          </div>
                                        </CardContent>
                                      </Card>
                                    )
                                  })}
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="mt-4 flex items-center justify-between">
                            <div className="p-3 bg-muted rounded-lg flex-1">
                              <p className="text-sm text-muted-foreground">
                                Selected: {selectedAgents.length} agent{selectedAgents.length !== 1 ? 's' : ''}
                                {selectedAgents.length > 0 && (
                                  <span className="ml-2 text-xs">({selectedAgents.join(', ')})</span>
                                )}
                              </p>
                            </div>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                syncAgentsWithForm([])
                                console.log('Cleared all agent selections')
                              }}
                              className="ml-2"
                            >
                              Clear All
                            </Button>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )
                    }}
                  />
                </form>
              </Form>
            </CardContent>
          </Card>
        )

      case 4:
        return (
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center">
                  <Settings className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Automation Policies</CardTitle>
                  <CardDescription>Configure how autonomous actions should be handled</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Form {...policiesForm}>
                <form className="space-y-6">
                  <FormField
                    control={policiesForm.control}
                    name="autoApprovalThreshold"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Auto-Approval Confidence Threshold</FormLabel>
                        <FormControl>
                          <div className="space-y-2">
                            <Input 
                              type="number" 
                              min="50" 
                              max="100" 
                              {...field}
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            />
                            <div className="text-sm text-muted-foreground">
                              Actions with {field.value}% or higher confidence will be executed automatically
                            </div>
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="space-y-4">
                    <FormField
                      control={policiesForm.control}
                      name="requireApprovalForHigh"
                      render={({ field }) => (
                        <FormItem className="flex items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">
                              Require approval for high-impact actions
                            </FormLabel>
                            <FormDescription>
                              Actions affecting critical systems will need manual approval
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={policiesForm.control}
                      name="requireApprovalForMedium"
                      render={({ field }) => (
                        <FormItem className="flex items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">
                              Require approval for medium-impact actions
                            </FormLabel>
                            <FormDescription>
                              Actions affecting non-critical systems will need manual approval
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={policiesForm.control}
                      name="enableRollback"
                      render={({ field }) => (
                        <FormItem className="flex items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base">
                              Enable automatic rollback
                            </FormLabel>
                            <FormDescription>
                              Automatically rollback changes if issues are detected
                            </FormDescription>
                          </div>
                          <FormControl>
                            <Switch
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        )


      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      <div className="container max-w-4xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
              <Zap className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Welcome to Integraite
          </h1>
          <p className="text-muted-foreground text-lg">
            Let's set up your autonomous ops platform in just a few steps
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm font-medium">
              Step {currentStep} of {steps.length}
            </div>
            <div className="text-sm text-muted-foreground">
              {Math.round(progress)}% complete
            </div>
          </div>
          <Progress value={progress} className="h-3" />
        </div>

        {/* Steps Navigation */}
        <div className="flex items-center justify-between mb-8 overflow-x-auto pb-2">
          {steps.map((step, index) => {
            const IconComponent = step.icon
            return (
              <div key={step.id} className="flex items-center min-w-0">
                <div className="flex flex-col items-center">
                  <div className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                    currentStep >= step.id
                      ? "bg-primary text-primary-foreground border-primary shadow-lg"
                      : currentStep === step.id - 1
                      ? "bg-primary/10 text-primary border-primary/30"
                      : "bg-muted text-muted-foreground border-muted-foreground/20"
                  )}>
                    {currentStep > step.id ? (
                      <CheckCircle2 className="h-6 w-6" />
                    ) : (
                      <IconComponent className="h-5 w-5" />
                    )}
                  </div>
                  <div className="mt-2 text-center min-w-0">
                    <div className={cn(
                      "text-sm font-medium truncate",
                      currentStep >= step.id ? "text-primary" : "text-muted-foreground"
                    )}>
                      {step.title}
                    </div>
                    <div className="text-xs text-muted-foreground truncate">
                      {step.description}
                    </div>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={cn(
                    "h-0.5 w-8 mx-4 transition-colors duration-300",
                    currentStep > step.id ? "bg-primary" : "bg-muted-foreground/20"
                  )} />
                )}
              </div>
            )
          })}
        </div>

        {/* Step Content */}
        <div className="mb-8">
          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="min-w-[120px]"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>

          <Button
            onClick={handleNext}
            disabled={completeOnboardingMutation.isPending}
            className="min-w-[120px]"
          >
            {completeOnboardingMutation.isPending ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Setting up...
              </>
            ) : currentStep === 4 ? (
              <>
                Complete Setup
                <CheckCircle2 className="ml-2 h-4 w-4" />
              </>
            ) : (
              <>
                Next
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}