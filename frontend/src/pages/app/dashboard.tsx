import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useDashboardStats, useRecentActions, useActiveAgents, useAgentCategories } from '@/hooks/useDashboard'
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Shield, 
  Zap, 
  AlertTriangle,
  CheckCircle2,
  RotateCcw,
  BookOpen,
  Activity,
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  MoreHorizontal
} from 'lucide-react'

// Map icon names to components
const iconMap = {
  Clock,
  Zap,
  RotateCcw,
  Activity,
  BookOpen,
  AlertTriangle,
}

// Mock data for KPIs (fallback)
const fallbackKpiData = [
  {
    title: "MTTR Delta",
    value: "-34%",
    description: "vs last month",
    trend: "down",
    color: "text-green-600",
    icon: Clock,
    details: "2.3 min avg resolution time"
  },
  {
    title: "Auto-Resolved",
    value: "94.7%",
    description: "incidents handled automatically",
    trend: "up",
    color: "text-blue-600",
    icon: Zap,
    details: "847 of 894 total incidents"
  },
  {
    title: "Rollback Rate",
    value: "0.3%",
    description: "of all deployments",
    trend: "down",
    color: "text-green-600",
    icon: RotateCcw,
    details: "3 of 1,247 deployments"
  },
  {
    title: "Error Budget Burn",
    value: "12.4%",
    description: "this month",
    trend: "up",
    color: "text-yellow-600",
    icon: Activity,
    details: "Well within SLO limits"
  },
  {
    title: "Doc Coverage",
    value: "89.2%",
    description: "runbooks documented",
    trend: "up",
    color: "text-blue-600",
    icon: BookOpen,
    details: "156 of 175 procedures"
  },
  {
    title: "Open Incidents",
    value: "3",
    description: "requiring attention",
    trend: "stable",
    color: "text-orange-600",
    icon: AlertTriangle,
    details: "2 low, 1 medium priority"
  }
]

const recentActions = [
  {
    id: 1,
    title: "Auto-scaled database cluster",
    description: "CPU usage exceeded 80% threshold",
    timestamp: "2 minutes ago",
    status: "completed",
    confidence: 96
  },
  {
    id: 2,
    title: "Restarted payment service",
    description: "Memory leak detected in payment-api-v2",
    timestamp: "15 minutes ago",
    status: "completed",
    confidence: 91
  },
  {
    id: 3,
    title: "Applied rate limiting",
    description: "Unusual traffic spike detected",
    timestamp: "1 hour ago",
    status: "completed",
    confidence: 88
  },
  {
    id: 4,
    title: "Rollback deployment",
    description: "Error rate increased after release",
    timestamp: "3 hours ago",
    status: "completed",
    confidence: 94
  }
]

const activeAgents = [
  { name: "EC2 Monitor", status: "active", incidents: 12, confidence: 94 },
  { name: "Database Healer", status: "active", incidents: 8, confidence: 91 },
  { name: "Network Analyzer", status: "active", incidents: 15, confidence: 89 },
  { name: "Log Processor", status: "active", incidents: 6, confidence: 97 },
]

export function DashboardPage() {
  const { data: statsData, isLoading: isLoadingKpis, error: kpiError } = useDashboardStats()
  const { data: recentActionsData, isLoading: isLoadingActions, error: actionsError } = useRecentActions()
  const { data: activeAgentsData, isLoading: isLoadingAgents, error: agentsError } = useActiveAgents()

  // Use API data if available, otherwise fallback to mock data
  const kpiData = statsData?.stats || fallbackKpiData
  const actionsData = recentActionsData?.actions || recentActions
  const agentsData = activeAgentsData?.agents || activeAgents

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground mt-2">
              Welcome back! Here's what's happening with your infrastructure.
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex items-center space-x-2">
            <Badge variant="secondary" className="bg-green-50 text-green-700 border-green-200">
              <div className="w-2 h-2 rounded-full bg-green-500 mr-2" />
              All Systems Healthy
            </Badge>
            <Button variant="outline" size="sm">
              <Eye className="mr-2 h-4 w-4" />
              View Details
            </Button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {kpiData.map((kpi) => {
            const Icon = kpi.icon
            const TrendIcon = kpi.trend === 'up' ? TrendingUp : kpi.trend === 'down' ? TrendingDown : Activity
            
            return (
              <Card key={kpi.title} className="card-hover">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {kpi.title}
                  </CardTitle>
                  <Icon className={cn("h-5 w-5", kpi.color)} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{kpi.value}</div>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <TrendIcon className={cn("mr-1 h-3 w-3", 
                      kpi.trend === 'up' ? 'text-green-600' : 
                      kpi.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                    )} />
                    {kpi.description}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{kpi.details}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Recent Actions
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </CardTitle>
              <CardDescription>
                Latest autonomous actions taken by the system
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {actionsData.map((action) => (
                <div key={action.id} className="flex items-start space-x-4 p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium truncate">{action.title}</p>
                      <Badge variant="secondary" className="ml-2 text-xs">
                        {action.confidence}% confidence
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{action.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">{action.timestamp}</p>
                  </div>
                </div>
              ))}
              <Button variant="outline" className="w-full">
                View All Actions
                <ArrowUpRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>

          {/* Active Agents */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Active Agents
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </CardTitle>
              <CardDescription>
                AI agents currently monitoring your infrastructure
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {agentsData.map((agent) => (
                <div key={agent.name} className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 cursor-pointer">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                      <Shield className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-sm font-medium">{agent.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {agent.incidents} incidents handled
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary" className="text-xs">
                      {agent.confidence}%
                    </Badge>
                    <div className="text-xs text-muted-foreground mt-1">
                      {agent.status}
                    </div>
                  </div>
                </div>
              ))}
              <Button variant="outline" className="w-full">
                Manage Agents
                <ArrowUpRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts for managing your autonomous operations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <AlertTriangle className="h-6 w-6 text-orange-600" />
                <span className="text-sm font-medium">View Incidents</span>
                <span className="text-xs text-muted-foreground">3 open</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <Zap className="h-6 w-6 text-blue-600" />
                <span className="text-sm font-medium">Create Automation</span>
                <span className="text-xs text-muted-foreground">New playbook</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <Shield className="h-6 w-6 text-green-600" />
                <span className="text-sm font-medium">Deploy Agent</span>
                <span className="text-xs text-muted-foreground">Add monitoring</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <BookOpen className="h-6 w-6 text-purple-600" />
                <span className="text-sm font-medium">Review Docs</span>
                <span className="text-xs text-muted-foreground">Update runbooks</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
