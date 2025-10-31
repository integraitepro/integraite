/**
 * ServiceNow Configuration Modal
 */

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Eye, EyeOff, Cloud } from 'lucide-react'

interface ServiceNowConfigModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (config: ServiceNowConfig) => void
  isLoading?: boolean
  error?: string
}

interface ServiceNowConfig {
  instanceUrl: string
  username: string
  password: string
}

export function ServiceNowConfigModal({ 
  open, 
  onOpenChange, 
  onSave, 
  isLoading = false,
  error 
}: ServiceNowConfigModalProps) {
  const [config, setConfig] = useState<ServiceNowConfig>({
    instanceUrl: '',
    username: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)

  const handleSave = () => {
    if (config.instanceUrl && config.username && config.password) {
      onSave(config)
    }
  }

  const isValid = config.instanceUrl && config.username && config.password

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <Cloud className="h-5 w-5 text-blue-600" />
            <DialogTitle>Configure ServiceNow Integration</DialogTitle>
          </div>
          <DialogDescription>
            Enter your ServiceNow instance details to sync incidents automatically.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="instanceUrl">ServiceNow Instance URL</Label>
            <Input
              id="instanceUrl"
              placeholder="https://your-instance.service-now.com"
              value={config.instanceUrl}
              onChange={(e) => setConfig(prev => ({ ...prev, instanceUrl: e.target.value }))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              placeholder="ServiceNow username"
              value={config.username}
              onChange={(e) => setConfig(prev => ({ ...prev, username: e.target.value }))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="ServiceNow password"
                value={config.password}
                onChange={(e) => setConfig(prev => ({ ...prev, password: e.target.value }))}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!isValid || isLoading}
          >
            {isLoading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
            Save & Test Connection
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}