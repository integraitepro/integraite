/**
 * Agent Execution Monitoring Component
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Bot,
  Play,
  Pause,
  Square,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Terminal,
  Search,
  Shield,
  FileText,
  Activity,
  Zap,
  Eye,
  Settings
} from 'lucide-react'

interface AgentExecution {
  id: number
  execution_id: string
  agent_name: string
  status: string
  progress_percentage: number
  current_step: string
  started_at: string
  completed_at?: string
  duration_seconds?: number
  summary?: string
  final_status?: string
  error_message?: string
}

interface TimelineEntry {
  id: number
  step_number: number
  action_type: string
  title: string
  description?: string
  command?: string
  target_host?: string
  success: boolean
  stdout?: string
  stderr?: string
  exit_code?: number
  duration_ms?: number
  timestamp: string
}

interface Hypothesis {
  id: number
  hypothesis_text: string
  confidence_score: number
  category?: string
  status: string
  test_plan?: string
  test_results?: string
  created_at: string
}

interface Verification {
  id: number
  verification_type: string
  title: string
  description?: string
  expected_result?: string
  actual_result?: string
  status: string
  success?: boolean
  error_message?: string
  completed_at?: string
}

interface Evidence {
  id: number
  evidence_type: string
  title: string
  description?: string
  content: string
  source?: string
  relevance_score: number
  category?: string
  collected_at: string
}

export function AgentExecutionMonitor({ 
  executionId, 
  onClose 
}: { 
  executionId: string
  onClose: () => void 
}) {
  const [execution, setExecution] = useState<AgentExecution | null>(null)
  const [timeline, setTimeline] = useState<TimelineEntry[]>([])
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([])
  const [verifications, setVerifications] = useState<Verification[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState('timeline')
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    if (executionId) {
      fetchExecutionData()
    }
  }, [executionId])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (autoRefresh && execution?.status === 'running') {
      interval = setInterval(fetchExecutionData, 2000) // Refresh every 2 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, execution?.status])

  const fetchExecutionData = async () => {
    try {
      // Fetch execution details
      const execResponse = await fetch(`/api/agents/executions/${executionId}`)
      const execData = await execResponse.json()
      setExecution(execData)

      // Fetch timeline
      const timelineResponse = await fetch(`/api/agents/executions/${executionId}/timeline`)
      const timelineData = await timelineResponse.json()
      setTimeline(timelineData)

      // Fetch hypotheses
      const hypothesesResponse = await fetch(`/api/agents/executions/${executionId}/hypotheses`)
      const hypothesesData = await hypothesesResponse.json()
      setHypotheses(hypothesesData)

      // Fetch verifications
      const verificationsResponse = await fetch(`/api/agents/executions/${executionId}/verifications`)
      const verificationsData = await verificationsResponse.json()
      setVerifications(verificationsData)

      // Fetch evidence
      const evidenceResponse = await fetch(`/api/agents/executions/${executionId}/evidence`)
      const evidenceData = await evidenceResponse.json()
      setEvidence(evidenceData)

      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch execution data:', error)
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'cancelled':
        return <Square className="h-4 w-4 text-gray-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A'
    
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          <span>Loading execution data...</span>
        </div>
      </div>
    )
  }

  if (!execution) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Execution Not Found</AlertTitle>
        <AlertDescription>
          Could not find execution with ID: {executionId}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Bot className="h-6 w-6 text-blue-600" />
            <h2 className="text-2xl font-bold">{execution.agent_name}</h2>
          </div>
          <Badge className={getStatusColor(execution.status)}>
            {getStatusIcon(execution.status)}
            <span className="ml-1">{execution.status.toUpperCase()}</span>
          </Badge>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            {autoRefresh ? 'Pause' : 'Resume'}
          </Button>
          <Button variant="outline" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Execution Progress</h3>
                <p className="text-sm text-muted-foreground">
                  {execution.current_step || 'Waiting for next step...'}
                </p>
              </div>
              <div className="text-right">
                <div className="font-bold text-2xl">{execution.progress_percentage}%</div>
                <div className="text-sm text-muted-foreground">
                  {formatDuration(execution.duration_seconds)}
                </div>
              </div>
            </div>
            
            <Progress value={execution.progress_percentage} className="w-full" />
            
            {execution.summary && (
              <div className="mt-4 p-3 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Summary</h4>
                <p className="text-sm">{execution.summary}</p>
              </div>
            )}

            {execution.error_message && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertTitle>Execution Error</AlertTitle>
                <AlertDescription>{execution.error_message}</AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="timeline">
            <Terminal className="h-4 w-4 mr-2" />
            Timeline ({timeline.length})
          </TabsTrigger>
          <TabsTrigger value="hypotheses">
            <Search className="h-4 w-4 mr-2" />
            Hypotheses ({hypotheses.length})
          </TabsTrigger>
          <TabsTrigger value="verifications">
            <Shield className="h-4 w-4 mr-2" />
            Verifications ({verifications.length})
          </TabsTrigger>
          <TabsTrigger value="evidence">
            <FileText className="h-4 w-4 mr-2" />
            Evidence ({evidence.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="space-y-4">
          <ScrollArea className="h-96">
            <div className="space-y-4">
              {timeline.map(entry => (
                <Card key={entry.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 text-sm font-medium">
                          {entry.step_number}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium">{entry.title}</h4>
                            <Badge variant={entry.success ? "default" : "destructive"} className="text-xs">
                              {entry.action_type}
                            </Badge>
                          </div>
                          {entry.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {entry.description}
                            </p>
                          )}
                          {entry.command && (
                            <div className="mt-2 p-2 bg-black text-green-400 rounded text-xs font-mono">
                              {entry.target_host && <span className="text-blue-400">{entry.target_host}$ </span>}
                              {entry.command}
                            </div>
                          )}
                          {entry.stdout && (
                            <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono max-h-32 overflow-y-auto">
                              <div className="text-gray-600 font-bold mb-1">STDOUT:</div>
                              <pre className="whitespace-pre-wrap">{entry.stdout}</pre>
                            </div>
                          )}
                          {entry.stderr && (
                            <div className="mt-2 p-2 bg-red-50 rounded text-xs font-mono max-h-32 overflow-y-auto">
                              <div className="text-red-600 font-bold mb-1">STDERR:</div>
                              <pre className="whitespace-pre-wrap">{entry.stderr}</pre>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <div>{formatTimestamp(entry.timestamp)}</div>
                        {entry.duration_ms && (
                          <div>{entry.duration_ms}ms</div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="hypotheses" className="space-y-4">
          <ScrollArea className="h-96">
            <div className="space-y-4">
              {hypotheses.map(hypothesis => (
                <Card key={hypothesis.id}>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <Badge variant={hypothesis.status === 'confirmed' ? 'default' : 
                                         hypothesis.status === 'rejected' ? 'destructive' : 'secondary'}>
                              {hypothesis.status}
                            </Badge>
                            {hypothesis.category && (
                              <Badge variant="outline">{hypothesis.category}</Badge>
                            )}
                          </div>
                          <p className="text-sm">{hypothesis.hypothesis_text}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">
                            {Math.round(hypothesis.confidence_score * 100)}%
                          </div>
                          <div className="text-xs text-muted-foreground">confidence</div>
                        </div>
                      </div>
                      
                      {hypothesis.test_plan && (
                        <div className="p-2 bg-blue-50 rounded">
                          <div className="text-xs font-medium text-blue-800 mb-1">Test Plan:</div>
                          <p className="text-xs text-blue-700">{hypothesis.test_plan}</p>
                        </div>
                      )}
                      
                      {hypothesis.test_results && (
                        <div className="p-2 bg-green-50 rounded">
                          <div className="text-xs font-medium text-green-800 mb-1">Test Results:</div>
                          <p className="text-xs text-green-700">{hypothesis.test_results}</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="verifications" className="space-y-4">
          <ScrollArea className="h-96">
            <div className="space-y-4">
              {verifications.map(verification => (
                <Card key={verification.id}>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{verification.title}</h4>
                          {verification.description && (
                            <p className="text-sm text-muted-foreground">
                              {verification.description}
                            </p>
                          )}
                        </div>
                        <Badge variant={
                          verification.status === 'passed' ? 'default' :
                          verification.status === 'failed' ? 'destructive' : 'secondary'
                        }>
                          {verification.status}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        {verification.expected_result && (
                          <div>
                            <div className="font-medium text-muted-foreground mb-1">Expected:</div>
                            <div className="p-2 bg-gray-50 rounded font-mono">
                              {verification.expected_result}
                            </div>
                          </div>
                        )}
                        {verification.actual_result && (
                          <div>
                            <div className="font-medium text-muted-foreground mb-1">Actual:</div>
                            <div className={`p-2 rounded font-mono ${
                              verification.success ? 'bg-green-50' : 'bg-red-50'
                            }`}>
                              {verification.actual_result}
                            </div>
                          </div>
                        )}
                      </div>

                      {verification.error_message && (
                        <Alert variant="destructive">
                          <AlertDescription className="text-xs">
                            {verification.error_message}
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="evidence" className="space-y-4">
          <ScrollArea className="h-96">
            <div className="space-y-4">
              {evidence.map(item => (
                <Card key={item.id}>
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium">{item.title}</h4>
                            <Badge variant="outline">{item.evidence_type}</Badge>
                          </div>
                          {item.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {item.description}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">
                            {Math.round(item.relevance_score * 100)}%
                          </div>
                          <div className="text-xs text-muted-foreground">relevance</div>
                        </div>
                      </div>

                      {item.source && (
                        <div className="text-xs text-muted-foreground">
                          Source: {item.source}
                        </div>
                      )}

                      <div className="p-2 bg-gray-50 rounded text-xs font-mono max-h-40 overflow-y-auto">
                        <pre className="whitespace-pre-wrap">{item.content}</pre>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  )
}