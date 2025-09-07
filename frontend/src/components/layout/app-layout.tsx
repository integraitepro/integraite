import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ThemeToggle } from '@/components/theme-toggle'
import { OrganizationSelector } from '@/components/organization-selector'
import { useCurrentUser } from '@/hooks/useAuth'
import { 
  LayoutDashboard,
  Settings,
  Bot,
  AlertTriangle,
  Zap,
  Search,
  CheckSquare,
  Users,
  CreditCard,
  FileText,
  Archive,
  Bell,
  ChevronDown,
  LogOut,
  Menu,
  X,
  Rocket,
  Building2,
  Plus
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface AppLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/app', icon: LayoutDashboard },
  { name: 'Setup Wizard', href: '/app/onboarding', icon: Rocket },
  { name: 'Agents', href: '/app/agents', icon: Bot },
  { name: 'Incidents', href: '/app/incidents', icon: AlertTriangle },
  { name: 'Automations', href: '/app/automations', icon: Zap },
  { name: 'Integrations', href: '/app/integrations', icon: Archive },
  { name: 'Evidence', href: '/app/evidence', icon: Search },
  { name: 'Approvals', href: '/app/approvals', icon: CheckSquare },
  { name: 'Users', href: '/app/users', icon: Users },
  { name: 'Billing', href: '/app/billing', icon: CreditCard },
  { name: 'Audit', href: '/app/audit', icon: FileText },
  { name: 'Settings', href: '/app/settings', icon: Settings },
]

export function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const location = useLocation()
  const [organizationName, setOrganizationName] = useState<string>('Your Organization')
  const { data: currentUser } = useCurrentUser()

  useEffect(() => {
    // Get organization name from localStorage (set during onboarding)
    const storedOrgName = localStorage.getItem('organization_name')
    if (storedOrgName) {
      setOrganizationName(storedOrgName)
    }
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-200 ease-in-out lg:translate-x-0",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full bg-card border-r">
          {/* Logo */}
          <div className="flex flex-col border-b">
            <div className="flex items-center justify-between h-16 px-6">
              <Link to="/app" className="flex items-center space-x-2">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600">
                  <Zap className="h-5 w-5 text-white" />
                </div>
                <span className="font-bold text-xl">Integraite</span>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setIsSidebarOpen(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            {/* Organization Selector */}
            <div className="px-6 pb-4">
              <OrganizationSelector currentOrgName={organizationName} />
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t">
            <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted cursor-pointer">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white text-sm font-bold">
                {currentUser ? 
                  `${currentUser.first_name?.[0] || ''}${currentUser.last_name?.[0] || ''}`.toUpperCase() || 
                  currentUser.email[0].toUpperCase() 
                  : 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">
                  {currentUser ? 
                    `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim() || 
                    currentUser.email.split('@')[0] 
                    : 'Loading...'}
                </div>
                <div className="text-xs text-muted-foreground truncate">
                  {currentUser?.email || 'Loading...'}
                </div>
              </div>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setIsSidebarOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="hidden sm:flex">
                  <div className="w-2 h-2 rounded-full bg-green-500 mr-2" />
                  All Systems Operational
                </Badge>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full" />
              </Button>
              <ThemeToggle />
              <Button variant="ghost" size="icon">
                <LogOut className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>

      {/* Backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  )
}
