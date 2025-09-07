/**
 * Organization selector component
 */

import { useState } from 'react'
import { Check, ChevronDown, Plus, Building2, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { useOrganizations, useCreateOrganization, useSwitchOrganization } from '@/hooks/useOrganizations'
import { cn } from '@/lib/utils'

interface OrganizationSelectorProps {
  currentOrgName: string
}

export function OrganizationSelector({ currentOrgName }: OrganizationSelectorProps) {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newOrgName, setNewOrgName] = useState('')
  const [newOrgDescription, setNewOrgDescription] = useState('')

  const { data: organizationsData, isLoading } = useOrganizations()
  const createOrganizationMutation = useCreateOrganization()
  const switchOrganizationMutation = useSwitchOrganization()

  const organizations = organizationsData?.organizations || []
  const currentOrgId = localStorage.getItem('current_organization_id')

  const handleCreateOrganization = async () => {
    if (!newOrgName.trim()) return

    await createOrganizationMutation.mutateAsync({
      name: newOrgName.trim(),
      description: newOrgDescription.trim() || undefined,
      timezone: 'UTC',
    })

    setNewOrgName('')
    setNewOrgDescription('')
    setIsCreateDialogOpen(false)
  }

  const handleSwitchOrganization = async (orgId: number) => {
    if (orgId.toString() === currentOrgId) return
    await switchOrganizationMutation.mutateAsync(orgId)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <div className="group cursor-pointer rounded-lg border p-3 hover:bg-muted/50 transition-colors">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 min-w-0">
              <Building2 className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium truncate">{currentOrgName}</span>
            </div>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Admin • Click to switch orgs
          </div>
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80" align="start">
        <div className="px-2 py-1.5 text-sm font-semibold">Organizations</div>
        <DropdownMenuSeparator />
        
        {isLoading ? (
          <div className="px-2 py-8 text-center text-sm text-muted-foreground">
            Loading organizations...
          </div>
        ) : organizations.length === 0 ? (
          <div className="px-2 py-8 text-center text-sm text-muted-foreground">
            No organizations found
          </div>
        ) : (
          organizations.map((org) => (
            <DropdownMenuItem
              key={org.id}
              className="flex items-center justify-between px-2 py-2 cursor-pointer"
              onClick={() => handleSwitchOrganization(org.id)}
            >
              <div className="flex items-center space-x-2 min-w-0">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <div className="min-w-0">
                  <div className="font-medium truncate">{org.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {org.user_role} • {org.team_size} member{org.team_size !== 1 ? 's' : ''}
                  </div>
                </div>
              </div>
              {org.id.toString() === currentOrgId && (
                <Check className="h-4 w-4 text-primary" />
              )}
            </DropdownMenuItem>
          ))
        )}

        <DropdownMenuSeparator />
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <DropdownMenuItem 
              className="flex items-center space-x-2 px-2 py-2 cursor-pointer"
              onSelect={(e) => e.preventDefault()}
            >
              <Plus className="h-4 w-4" />
              <span>Create Organization</span>
            </DropdownMenuItem>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Create Organization</DialogTitle>
              <DialogDescription>
                Create a new organization to manage separate workspaces and teams.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="org-name">Organization Name</Label>
                <Input
                  id="org-name"
                  placeholder="Acme Corporation"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="org-description">Description (Optional)</Label>
                <Textarea
                  id="org-description"
                  placeholder="Brief description of your organization..."
                  value={newOrgDescription}
                  onChange={(e) => setNewOrgDescription(e.target.value)}
                  rows={3}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button 
                  variant="outline" 
                  onClick={() => setIsCreateDialogOpen(false)}
                  disabled={createOrganizationMutation.isPending}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleCreateOrganization}
                  disabled={!newOrgName.trim() || createOrganizationMutation.isPending}
                >
                  {createOrganizationMutation.isPending ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      Creating...
                    </>
                  ) : (
                    'Create Organization'
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
