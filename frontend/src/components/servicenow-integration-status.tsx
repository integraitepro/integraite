/**
 * ServiceNow Integration Status Component
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useServiceNowStatus, useSyncFromServiceNow } from '@/hooks/useIncidents'
import { Loader2, RefreshCw, CheckCircle, XCircle, AlertTriangle, Cloud } from 'lucide-react'

export function ServiceNowIntegrationStatus() {
  const { data: status, isLoading: statusLoading, error: statusError } = useServiceNowStatus()
  const syncMutation = useSyncFromServiceNow()

  const handleManualSync = () => {
    syncMutation.mutate()
  }

  const getStatusIcon = () => {
    if (!status) return <AlertTriangle className="h-4 w-4" />
    if (status.connected) return <CheckCircle className="h-4 w-4 text-green-500" />
    if (status.configured) return <XCircle className="h-4 w-4 text-red-500" />
    return <AlertTriangle className="h-4 w-4 text-yellow-500" />
  }

  const getStatusBadge = () => {
    if (!status) return <Badge variant="secondary">Unknown</Badge>
    if (status.connected) return <Badge variant="default" className="bg-green-600">Connected</Badge>
    if (status.configured) return <Badge variant="destructive">Connection Failed</Badge>
    return <Badge variant="secondary">Not Configured</Badge>
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Cloud className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">ServiceNow Integration</CardTitle>
          </div>
          {getStatusBadge()}
        </div>
        <CardDescription>
          Sync incidents directly from your ServiceNow instance
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {statusLoading ? (
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Checking ServiceNow status...</span>
          </div>
        ) : statusError ? (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              Failed to check ServiceNow status. Please try again.
            </AlertDescription>
          </Alert>
        ) : status ? (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-sm">
              {getStatusIcon()}
              <span className="font-medium">Status:</span>
              <span className={status.connected ? 'text-green-600' : 'text-red-600'}>
                {status.message}
              </span>
            </div>

            {status.configured && (
              <div className="flex items-center space-x-2">
                <Button
                  onClick={handleManualSync}
                  disabled={syncMutation.isPending || !status.connected}
                  size="sm"
                  variant={status.connected ? "default" : "secondary"}
                >
                  {syncMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  Sync Now
                </Button>
              </div>
            )}

            {syncMutation.isSuccess && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertTitle>Sync Successful</AlertTitle>
                <AlertDescription>
                  {syncMutation.data?.detail || 'Incidents synced successfully'}
                </AlertDescription>
              </Alert>
            )}

            {syncMutation.isError && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertTitle>Sync Failed</AlertTitle>
                <AlertDescription>
                  {syncMutation.error?.message || 'Failed to sync incidents from ServiceNow'}
                </AlertDescription>
              </Alert>
            )}

            {!status.configured && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Configuration Required</AlertTitle>
                <AlertDescription>
                  ServiceNow credentials need to be configured in the backend environment variables:
                  <ul className="mt-2 list-disc list-inside text-xs space-y-1">
                    <li>SERVICENOW_INSTANCE_URL</li>
                    <li>SERVICENOW_USERNAME</li>
                    <li>SERVICENOW_PASSWORD</li>
                  </ul>
                </AlertDescription>
              </Alert>
            )}
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}