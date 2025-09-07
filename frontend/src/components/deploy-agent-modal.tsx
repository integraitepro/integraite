/**
 * Beautiful Deploy Agent Modal Component
 */

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { cn } from '@/lib/utils'
import {
  Server,
  Database,
  Network,
  Shield,
  Monitor,
  Brain,
  Zap,
  Settings,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Play,
  Container,
  Cloud,
  Lock,
  Activity,
  FileText,
  TrendingUp,
  Cpu,
  HardDrive,
  MemoryStick,
  Sparkles,
  Layers,
  Code,
  Target,
  Palette,
  Globe,
  X,
  Eye
} from 'lucide-react'

// Agent deployment form schema
const deployAgentSchema = z.object({
  name: z.string().min(3, 'Agent name must be at least 3 characters').max(50, 'Agent name must be less than 50 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters').max(200, 'Description must be less than 200 characters'),
  category: z.enum(['compute', 'database', 'network', 'security', 'monitoring', 'application', 'container', 'storage']),
  layer: z.enum(['presentation', 'application', 'data', 'infrastructure']),
  autoStart: z.boolean().default(true),
  alertThreshold: z.number().min(1).max(100).default(85),
  retryAttempts: z.number().min(1).max(10).default(3),
  monitoringInterval: z.number().min(1).max(300).default(30),
  capabilities: z.array(z.string()).min(1, 'Select at least one capability'),
  priority: z.enum(['low', 'medium', 'high', 'critical']).default('medium'),
  tags: z.array(z.string()).default([])
})

type DeployAgentFormValues = z.infer<typeof deployAgentSchema>

// Available categories with beautiful styling
const agentCategories = [
  {
    id: 'compute',
    name: 'Compute',
    description: 'Manage servers, instances, and computing resources',
    icon: Server,
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    borderColor: 'border-blue-200 dark:border-blue-800'
  },
  {
    id: 'database',
    name: 'Database',
    description: 'Monitor and optimize database performance',
    icon: Database,
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    borderColor: 'border-green-200 dark:border-green-800'
  },
  {
    id: 'network',
    name: 'Network',
    description: 'Analyze traffic and ensure connectivity',
    icon: Network,
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    borderColor: 'border-purple-200 dark:border-purple-800'
  },
  {
    id: 'security',
    name: 'Security',
    description: 'Protect against threats and vulnerabilities',
    icon: Shield,
    color: 'from-red-500 to-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    borderColor: 'border-red-200 dark:border-red-800'
  },
  {
    id: 'monitoring',
    name: 'Monitoring',
    description: 'Track metrics and system health',
    icon: Monitor,
    color: 'from-orange-500 to-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    borderColor: 'border-orange-200 dark:border-orange-800'
  },
  {
    id: 'application',
    name: 'Application',
    description: 'Manage application lifecycle and performance',
    icon: Code,
    color: 'from-indigo-500 to-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    borderColor: 'border-indigo-200 dark:border-indigo-800'
  },
  {
    id: 'container',
    name: 'Container',
    description: 'Orchestrate containers and microservices',
    icon: Container,
    color: 'from-cyan-500 to-cyan-600',
    bgColor: 'bg-cyan-50 dark:bg-cyan-950/20',
    borderColor: 'border-cyan-200 dark:border-cyan-800'
  },
  {
    id: 'storage',
    name: 'Storage',
    description: 'Manage storage systems and data lifecycle',
    icon: HardDrive,
    color: 'from-pink-500 to-pink-600',
    bgColor: 'bg-pink-50 dark:bg-pink-950/20',
    borderColor: 'border-pink-200 dark:border-pink-800'
  }
]

// Available deployment layers
const deploymentLayers = [
  {
    id: 'presentation',
    name: 'Presentation Layer',
    description: 'User interfaces and client applications',
    icon: Globe,
    examples: ['Web apps', 'Mobile apps', 'API gateways']
  },
  {
    id: 'application',
    name: 'Application Layer',
    description: 'Business logic and application services',
    icon: Cpu,
    examples: ['Microservices', 'APIs', 'Business logic']
  },
  {
    id: 'data',
    name: 'Data Layer',
    description: 'Databases and data storage systems',
    icon: Database,
    examples: ['Databases', 'Caches', 'File storage']
  },
  {
    id: 'infrastructure',
    name: 'Infrastructure Layer',
    description: 'Core infrastructure and platform services',
    icon: Server,
    examples: ['Servers', 'Networks', 'Cloud services']
  }
]

// Available capabilities for agents
const agentCapabilities = [
  'Auto-healing', 'Performance monitoring', 'Resource optimization', 'Anomaly detection',
  'Load balancing', 'Backup management', 'Security scanning', 'Cost optimization',
  'Compliance checking', 'Log analysis', 'Metric collection', 'Alert management',
  'Auto-scaling', 'Fault tolerance', 'Data validation', 'Network optimization',
  'Cache management', 'Error tracking', 'Health checks', 'Disaster recovery'
]

interface DeployAgentModalProps {
  isOpen: boolean
  onClose: () => void
  onDeploy: (agentData: DeployAgentFormValues) => void
}

export function DeployAgentModal({ isOpen, onClose, onDeploy }: DeployAgentModalProps) {
  const [isDeploying, setIsDeploying] = useState(false)
  const [newTag, setNewTag] = useState('')

  const form = useForm<DeployAgentFormValues>({
    resolver: zodResolver(deployAgentSchema),
    defaultValues: {
      name: '',
      description: '',
      category: 'compute',
      layer: 'infrastructure',
      autoStart: true,
      alertThreshold: 85,
      retryAttempts: 3,
      monitoringInterval: 30,
      capabilities: [],
      priority: 'medium',
      tags: []
    }
  })

  const selectedCategory = agentCategories.find(cat => cat.id === form.watch('category'))
  const selectedLayer = deploymentLayers.find(layer => layer.id === form.watch('layer'))

  const handleDeploy = async (data: DeployAgentFormValues) => {
    setIsDeploying(true)
    try {
      // Simulate deployment time
      await new Promise(resolve => setTimeout(resolve, 3000))
      onDeploy(data)
    } catch (error) {
      console.error('Failed to deploy agent:', error)
    } finally {
      setIsDeploying(false)
    }
  }

  const handleClose = () => {
    form.reset()
    setIsDeploying(false)
    setNewTag('')
    onClose()
  }

  const addTag = () => {
    if (newTag.trim() && !form.getValues('tags').includes(newTag.trim())) {
      const currentTags = form.getValues('tags')
      form.setValue('tags', [...currentTags, newTag.trim()])
      setNewTag('')
    }
  }

  const removeTag = (tagToRemove: string) => {
    const currentTags = form.getValues('tags')
    form.setValue('tags', currentTags.filter(tag => tag !== tagToRemove))
  }

  const toggleCapability = (capability: string) => {
    const currentCapabilities = form.getValues('capabilities')
    if (currentCapabilities.includes(capability)) {
      form.setValue('capabilities', currentCapabilities.filter(cap => cap !== capability))
    } else {
      form.setValue('capabilities', [...currentCapabilities, capability])
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-6xl max-h-[95vh] overflow-hidden flex flex-col">
        <DialogHeader className="pb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <DialogTitle className="text-2xl font-bold">Create Custom Agent</DialogTitle>
              <DialogDescription className="text-base">
                Design and deploy a personalized AI agent tailored to your specific needs
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleDeploy)} className="space-y-8">
              
              {/* Basic Information Section */}
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="h-5 w-5 text-blue-600" />
                    <span>Basic Information</span>
                  </CardTitle>
                  <CardDescription>
                    Define the core identity and purpose of your agent
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid gap-6 md:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base font-medium">Agent Name</FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., Database Guardian Pro" 
                              className="h-11 text-base"
                              {...field} 
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="priority"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base font-medium">Priority Level</FormLabel>
                          <FormControl>
                            <select 
                              className="flex h-11 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background"
                              {...field}
                            >
                              <option value="low">Low Priority</option>
                              <option value="medium">Medium Priority</option>
                              <option value="high">High Priority</option>
                              <option value="critical">Critical Priority</option>
                            </select>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base font-medium">Description</FormLabel>
                        <FormControl>
                          <Textarea 
                            placeholder="Describe what your agent will do, how it will help your infrastructure, and its key responsibilities..."
                            className="min-h-[100px] text-base resize-none"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          A clear description helps the AI understand your agent's purpose and optimize its behavior
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>

              {/* Category Selection */}
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Palette className="h-5 w-5 text-purple-600" />
                    <span>Agent Category</span>
                  </CardTitle>
                  <CardDescription>
                    Choose the primary domain your agent will operate in
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FormField
                    control={form.control}
                    name="category"
                    render={({ field }) => (
                      <FormItem>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                          {agentCategories.map((category) => {
                            const Icon = category.icon
                            const isSelected = field.value === category.id
                            return (
                              <Card
                                key={category.id}
                                className={cn(
                                  "cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105",
                                  isSelected 
                                    ? `ring-2 ring-offset-2 ring-blue-500 ${category.bgColor} ${category.borderColor}` 
                                    : "hover:shadow-md"
                                )}
                                onClick={() => field.onChange(category.id)}
                              >
                                <CardContent className="p-4 text-center">
                                  <div className={cn(
                                    "w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center bg-gradient-to-br",
                                    category.color
                                  )}>
                                    <Icon className="h-6 w-6 text-white" />
                                  </div>
                                  <h3 className="font-semibold mb-1">{category.name}</h3>
                                  <p className="text-xs text-muted-foreground leading-relaxed">
                                    {category.description}
                                  </p>
                                  {isSelected && (
                                    <div className="mt-3">
                                      <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100">
                                        Selected
                                      </Badge>
                                    </div>
                                  )}
                                </CardContent>
                              </Card>
                            )
                          })}
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>

              {/* Deployment Layer */}
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Layers className="h-5 w-5 text-green-600" />
                    <span>Deployment Layer</span>
                  </CardTitle>
                  <CardDescription>
                    Select where in your architecture this agent will operate
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FormField
                    control={form.control}
                    name="layer"
                    render={({ field }) => (
                      <FormItem>
                        <div className="grid gap-4 md:grid-cols-2">
                          {deploymentLayers.map((layer) => {
                            const Icon = layer.icon
                            const isSelected = field.value === layer.id
                            return (
                              <Card
                                key={layer.id}
                                className={cn(
                                  "cursor-pointer transition-all duration-200 hover:shadow-md",
                                  isSelected 
                                    ? "ring-2 ring-offset-2 ring-green-500 bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800" 
                                    : "hover:shadow-md"
                                )}
                                onClick={() => field.onChange(layer.id)}
                              >
                                <CardContent className="p-4">
                                  <div className="flex items-start space-x-3">
                                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center flex-shrink-0">
                                      <Icon className="h-5 w-5 text-white" />
                                    </div>
                                    <div className="flex-1">
                                      <h3 className="font-semibold mb-1">{layer.name}</h3>
                                      <p className="text-sm text-muted-foreground mb-2">{layer.description}</p>
                                      <div className="flex flex-wrap gap-1">
                                        {layer.examples.map((example, index) => (
                                          <Badge key={index} variant="outline" className="text-xs">
                                            {example}
                                          </Badge>
                                        ))}
                                      </div>
                                    </div>
                                    {isSelected && (
                                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                                    )}
                                  </div>
                                </CardContent>
                              </Card>
                            )
                          })}
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>

              {/* Agent Capabilities */}
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-indigo-600" />
                    <span>Agent Capabilities</span>
                  </CardTitle>
                  <CardDescription>
                    Select the capabilities your agent should have
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FormField
                    control={form.control}
                    name="capabilities"
                    render={({ field }) => (
                      <FormItem>
                        <div className="grid gap-2 md:grid-cols-3 lg:grid-cols-4">
                          {agentCapabilities.map((capability) => {
                            const isSelected = field.value.includes(capability)
                            return (
                              <Button
                                key={capability}
                                type="button"
                                variant={isSelected ? "default" : "outline"}
                                size="sm"
                                className={cn(
                                  "justify-start text-left h-auto py-2 px-3",
                                  isSelected && "bg-indigo-600 hover:bg-indigo-700"
                                )}
                                onClick={() => toggleCapability(capability)}
                              >
                                {capability}
                              </Button>
                            )
                          })}
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>

              {/* Configuration Settings */}
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="h-5 w-5 text-orange-600" />
                    <span>Configuration Settings</span>
                  </CardTitle>
                  <CardDescription>
                    Fine-tune your agent's behavior and performance
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid gap-6 md:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="alertThreshold"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base font-medium">Alert Threshold: {field.value}%</FormLabel>
                          <FormControl>
                            <Slider
                              value={[field.value]}
                              onValueChange={(value) => field.onChange(value[0])}
                              max={100}
                              min={1}
                              step={1}
                              className="py-4"
                            />
                          </FormControl>
                          <FormDescription>
                            Agent will trigger alerts when confidence falls below this threshold
                          </FormDescription>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="monitoringInterval"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base font-medium">Monitoring Interval: {field.value}s</FormLabel>
                          <FormControl>
                            <Slider
                              value={[field.value]}
                              onValueChange={(value) => field.onChange(value[0])}
                              max={300}
                              min={1}
                              step={5}
                              className="py-4"
                            />
                          </FormControl>
                          <FormDescription>
                            How often the agent checks system status
                          </FormDescription>
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid gap-6 md:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="retryAttempts"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-base font-medium">Retry Attempts</FormLabel>
                          <FormControl>
                            <Input 
                              type="number" 
                              min="1" 
                              max="10" 
                              className="h-11"
                              {...field}
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            />
                          </FormControl>
                          <FormDescription>
                            Number of retry attempts before marking an action as failed
                          </FormDescription>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="autoStart"
                      render={({ field }) => (
                        <FormItem className="flex items-center justify-between rounded-lg border p-4">
                          <div className="space-y-0.5">
                            <FormLabel className="text-base font-medium">Auto-start Agent</FormLabel>
                            <FormDescription>
                              Automatically start the agent after deployment
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
                </CardContent>
              </Card>

              {/* Tags */}
              <Card className="border-2">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-cyan-600" />
                    <span>Tags & Labels</span>
                  </CardTitle>
                  <CardDescription>
                    Add tags to organize and identify your agent
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex gap-2">
                      <Input
                        placeholder="Add a tag..."
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                        className="flex-1"
                      />
                      <Button type="button" onClick={addTag} variant="outline">
                        Add Tag
                      </Button>
                    </div>
                    {form.watch('tags').length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {form.watch('tags').map((tag, index) => (
                          <Badge key={index} variant="secondary" className="flex items-center gap-1">
                            {tag}
                            <X 
                              className="h-3 w-3 cursor-pointer hover:text-destructive" 
                              onClick={() => removeTag(tag)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Preview Section */}
              <Card className="border-2 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Eye className="h-5 w-5 text-purple-600" />
                    <span>Agent Preview</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <div className="flex items-center space-x-3 mb-4">
                        {selectedCategory && (
                          <div className={cn(
                            "w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br",
                            selectedCategory.color
                          )}>
                            <selectedCategory.icon className="h-6 w-6 text-white" />
                          </div>
                        )}
                        <div>
                          <h3 className="font-bold text-lg">{form.watch('name') || 'Agent Name'}</h3>
                          <p className="text-sm text-muted-foreground">
                            {selectedCategory?.name} • {selectedLayer?.name}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mb-4">
                        {form.watch('description') || 'Agent description will appear here...'}
                      </p>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span>Priority:</span>
                        <Badge variant="outline" className="capitalize">{form.watch('priority')}</Badge>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Alert Threshold:</span>
                        <span>{form.watch('alertThreshold')}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Monitoring Interval:</span>
                        <span>{form.watch('monitoringInterval')}s</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Capabilities:</span>
                        <span>{form.watch('capabilities').length} selected</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </form>
          </Form>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-6 border-t bg-muted/20 -mx-6 -mb-6 px-6 pb-6">
          <Button variant="outline" onClick={handleClose} className="min-w-[100px]">
            Cancel
          </Button>
          
          <Button 
            onClick={form.handleSubmit(handleDeploy)}
            disabled={isDeploying || !form.formState.isValid}
            className="min-w-[140px] bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            {isDeploying ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Deploying...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Deploy Agent
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}