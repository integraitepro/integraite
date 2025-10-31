/**
 * Agent Creation and Configuration Component
 */

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog'
import {
  Upload,
  Key,
  Server,
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Bot
} from 'lucide-react'

interface AgentConfig {
  name: string
  description: string
  agentType: string
  sshConfig: {
    username: string
    keyFile: File | null
    defaultPort: number
  }
  serverTargets: ServerTarget[]
  capabilities: string[]
  environmentVariables: Record<string, string>
}

interface ServerTarget {
  id: string
  name: string
  ipAddress: string
  port: number
  description: string
}

export function AgentCreationModal({ 
  open, 
  onOpenChange, 
  onSave,
  isLoading = false 
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (config: AgentConfig) => void
  isLoading?: boolean
}) {
  const [config, setConfig] = useState<AgentConfig>({
    name: '',
    description: '',
    agentType: 'sre',
    sshConfig: {
      username: '',
      keyFile: null,
      defaultPort: 22
    },
    serverTargets: [],
    capabilities: [],
    environmentVariables: {}
  })

  const [currentTab, setCurrentTab] = useState('basic')
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  const agentTypes = [
    { value: 'sre', label: 'SRE (Site Reliability Engineer)', description: 'Handles infrastructure incidents and system recovery' },
    { value: 'network', label: 'Network Engineer', description: 'Diagnoses and fixes network connectivity issues' },
    { value: 'database', label: 'Database Administrator', description: 'Manages database performance and recovery' },
    { value: 'security', label: 'Security Analyst', description: 'Handles security incidents and threat response' },
    { value: 'application', label: 'Application Support', description: 'Troubleshoots application-specific issues' }
  ]

  const availableCapabilities = [
    'System Diagnostics',
    'Service Management',
    'Log Analysis',
    'Performance Monitoring',
    'Configuration Management',
    'Network Troubleshooting',
    'Database Operations',
    'Security Scanning',
    'File System Operations',
    'Process Management'
  ]

  const handleKeyFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setConfig(prev => ({
        ...prev,
        sshConfig: {
          ...prev.sshConfig,
          keyFile: file
        }
      }))
    }
  }

  const addServerTarget = () => {
    const newServer: ServerTarget = {
      id: Date.now().toString(),
      name: '',
      ipAddress: '',
      port: config.sshConfig.defaultPort,
      description: ''
    }
    setConfig(prev => ({
      ...prev,
      serverTargets: [...prev.serverTargets, newServer]
    }))
  }

  const updateServerTarget = (id: string, updates: Partial<ServerTarget>) => {
    setConfig(prev => ({
      ...prev,
      serverTargets: prev.serverTargets.map(server =>
        server.id === id ? { ...server, ...updates } : server
      )
    }))
  }

  const removeServerTarget = (id: string) => {
    setConfig(prev => ({
      ...prev,
      serverTargets: prev.serverTargets.filter(server => server.id !== id)
    }))
  }

  const toggleCapability = (capability: string) => {
    setConfig(prev => ({
      ...prev,
      capabilities: prev.capabilities.includes(capability)
        ? prev.capabilities.filter(c => c !== capability)
        : [...prev.capabilities, capability]
    }))
  }

  const addEnvironmentVariable = () => {
    const key = prompt('Environment Variable Name:')
    if (key && !config.environmentVariables[key]) {
      setConfig(prev => ({
        ...prev,
        environmentVariables: {
          ...prev.environmentVariables,
          [key]: ''
        }
      }))
    }
  }

  const updateEnvironmentVariable = (key: string, value: string) => {
    setConfig(prev => ({
      ...prev,
      environmentVariables: {
        ...prev.environmentVariables,
        [key]: value
      }
    }))
  }

  const removeEnvironmentVariable = (key: string) => {
    setConfig(prev => ({
      ...prev,
      environmentVariables: Object.fromEntries(
        Object.entries(prev.environmentVariables).filter(([k]) => k !== key)
      )
    }))
  }

  const toggleSecretVisibility = (key: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const handleSave = () => {
    onSave(config)
  }

  const isValid = config.name && config.agentType && config.sshConfig.username && config.sshConfig.keyFile

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <Bot className="h-6 w-6 text-blue-600" />
            <DialogTitle>Create New Agent</DialogTitle>
          </div>
          <DialogDescription>
            Configure an autonomous agent to handle specific types of incidents
          </DialogDescription>
        </DialogHeader>

        <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="basic">Basic Info</TabsTrigger>
            <TabsTrigger value="ssh">SSH Configuration</TabsTrigger>
            <TabsTrigger value="servers">Target Servers</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Agent Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Production SRE Agent"
                  value={config.name}
                  onChange={(e) => setConfig(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this agent does and when it should be used..."
                  value={config.description}
                  onChange={(e) => setConfig(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div>
                <Label htmlFor="agentType">Agent Type</Label>
                <Select value={config.agentType} onValueChange={(value) => setConfig(prev => ({ ...prev, agentType: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select agent type" />
                  </SelectTrigger>
                  <SelectContent>
                    {agentTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        <div>
                          <div className="font-medium">{type.label}</div>
                          <div className="text-xs text-muted-foreground">{type.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Capabilities</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {availableCapabilities.map(capability => (
                    <div key={capability} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={capability}
                        checked={config.capabilities.includes(capability)}
                        onChange={() => toggleCapability(capability)}
                        className="rounded"
                      />
                      <Label htmlFor={capability} className="text-sm">{capability}</Label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="ssh" className="space-y-4">
            <Alert>
              <Shield className="h-4 w-4" />
              <AlertTitle>Secure SSH Configuration</AlertTitle>
              <AlertDescription>
                Upload your SSH private key to enable the agent to connect to target servers securely.
              </AlertDescription>
            </Alert>

            <div className="space-y-4">
              <div>
                <Label htmlFor="sshUsername">SSH Username</Label>
                <Input
                  id="sshUsername"
                  placeholder="e.g., ubuntu, ec2-user, root"
                  value={config.sshConfig.username}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    sshConfig: { ...prev.sshConfig, username: e.target.value }
                  }))}
                />
              </div>

              <div>
                <Label htmlFor="defaultPort">Default SSH Port</Label>
                <Input
                  id="defaultPort"
                  type="number"
                  value={config.sshConfig.defaultPort}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    sshConfig: { ...prev.sshConfig, defaultPort: parseInt(e.target.value) }
                  }))}
                />
              </div>

              <div>
                <Label htmlFor="keyFile">SSH Private Key</Label>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <input
                      type="file"
                      id="keyFile"
                      accept=".pem,.ppk,.key"
                      onChange={handleKeyFileUpload}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                  </div>
                  {config.sshConfig.keyFile && (
                    <div className="flex items-center space-x-2 text-sm text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      <span>{config.sshConfig.keyFile.name} uploaded</span>
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Supported formats: .pem, .ppk, .key. The key will be encrypted and stored securely.
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="servers" className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">Target Servers</h3>
                <p className="text-sm text-muted-foreground">
                  Configure the servers this agent can access and manage
                </p>
              </div>
              <Button onClick={addServerTarget} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Server
              </Button>
            </div>

            <div className="space-y-4">
              {config.serverTargets.map(server => (
                <Card key={server.id}>
                  <CardContent className="p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Server Name</Label>
                        <Input
                          placeholder="e.g., Production Web Server"
                          value={server.name}
                          onChange={(e) => updateServerTarget(server.id, { name: e.target.value })}
                        />
                      </div>
                      <div>
                        <Label>IP Address</Label>
                        <Input
                          placeholder="e.g., 192.168.1.100"
                          value={server.ipAddress}
                          onChange={(e) => updateServerTarget(server.id, { ipAddress: e.target.value })}
                        />
                      </div>
                      <div>
                        <Label>SSH Port</Label>
                        <Input
                          type="number"
                          value={server.port}
                          onChange={(e) => updateServerTarget(server.id, { port: parseInt(e.target.value) })}
                        />
                      </div>
                      <div className="flex items-end">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeServerTarget(server.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="col-span-2">
                        <Label>Description</Label>
                        <Input
                          placeholder="Brief description of this server's role"
                          value={server.description}
                          onChange={(e) => updateServerTarget(server.id, { description: e.target.value })}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {config.serverTargets.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Server className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No servers configured yet</p>
                  <p className="text-sm">Add servers that this agent should manage</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-medium">Environment Variables</h3>
                  <p className="text-sm text-muted-foreground">
                    Configure environment variables for the agent (API keys, etc.)
                  </p>
                </div>
                <Button onClick={addEnvironmentVariable} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Variable
                </Button>
              </div>

              <div className="space-y-2">
                {Object.entries(config.environmentVariables).map(([key, value]) => (
                  <div key={key} className="flex items-center space-x-2">
                    <Input
                      value={key}
                      readOnly
                      className="flex-1"
                    />
                    <div className="relative flex-2">
                      <Input
                        type={showSecrets[key] ? "text" : "password"}
                        placeholder="Value"
                        value={value}
                        onChange={(e) => updateEnvironmentVariable(key, e.target.value)}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3"
                        onClick={() => toggleSecretVisibility(key)}
                      >
                        {showSecrets[key] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeEnvironmentVariable(key)}
                      className="text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!isValid || isLoading}>
            {isLoading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />}
            Create Agent
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}