import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthGuard, PublicGuard } from '@/components/auth-guard'

// Marketing pages
import { LandingPage } from '@/pages/marketing/landing'
import { HowItWorksPage } from '@/pages/marketing/how-it-works'
import { IntegrationsPage } from '@/pages/marketing/integrations'
import { SecurityPage } from '@/pages/marketing/security'
import { PricingPage } from '@/pages/marketing/pricing'
import { DocsPage } from '@/pages/marketing/docs'
import { StatusPage } from '@/pages/marketing/status'
import { PrivacyPage } from '@/pages/marketing/privacy'
import { TermsPage } from '@/pages/marketing/terms'

// Auth pages
import { LoginPage } from '@/pages/auth/login'
import { SignupPage } from '@/pages/auth/signup'

// App pages
import { DashboardPage } from '@/pages/app/dashboard'
import { OnboardingPage } from '@/pages/app/onboarding'
import { AgentsPage } from '@/pages/app/agents'
import { IncidentsPage } from '@/pages/app/incidents'
import { IncidentDetailPage } from '@/pages/app/incident-detail'
import { AutomationsPage } from '@/pages/app/automations'
import AppIntegrationsPage from '@/pages/app/integrations'
import { EvidencePage } from '@/pages/app/evidence'
import { ApprovalsPage } from '@/pages/app/approvals'
import { UsersPage } from '@/pages/app/users'
import { BillingPage } from '@/pages/app/billing'
import { AuditPage } from '@/pages/app/audit'
import { SettingsPage } from '@/pages/app/settings'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="integraite-theme">
        <Router>
          <Routes>
            {/* Marketing routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />
            <Route path="/integrations" element={<IntegrationsPage />} />
            <Route path="/security" element={<SecurityPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/docs" element={<DocsPage />} />
            <Route path="/status" element={<StatusPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/terms" element={<TermsPage />} />
            
            {/* Auth routes */}
            <Route path="/login" element={<PublicGuard><LoginPage /></PublicGuard>} />
            <Route path="/signup" element={<PublicGuard><SignupPage /></PublicGuard>} />
            
            {/* App routes */}
            <Route path="/app" element={<AuthGuard><DashboardPage /></AuthGuard>} />
            <Route path="/app/onboarding" element={<AuthGuard><OnboardingPage /></AuthGuard>} />
          <Route path="/app/agents" element={<AuthGuard><AgentsPage /></AuthGuard>} />
          <Route path="/app/incidents" element={<AuthGuard><IncidentsPage /></AuthGuard>} />
          <Route path="/app/incident/:id" element={<AuthGuard><IncidentDetailPage /></AuthGuard>} />
          <Route path="/app/integrations" element={<AuthGuard><AppIntegrationsPage /></AuthGuard>} />
            <Route path="/app/automations" element={<AuthGuard><AutomationsPage /></AuthGuard>} />
            <Route path="/app/evidence" element={<AuthGuard><EvidencePage /></AuthGuard>} />
            <Route path="/app/approvals" element={<AuthGuard><ApprovalsPage /></AuthGuard>} />
            <Route path="/app/users" element={<AuthGuard><UsersPage /></AuthGuard>} />
            <Route path="/app/billing" element={<AuthGuard><BillingPage /></AuthGuard>} />
            <Route path="/app/audit" element={<AuthGuard><AuditPage /></AuthGuard>} />
            <Route path="/app/settings" element={<AuthGuard><SettingsPage /></AuthGuard>} />
          </Routes>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
