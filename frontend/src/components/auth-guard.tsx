/**
 * Authentication guard component
 */

import { useEffect } from 'react'
import { useLocation, Navigate } from 'react-router-dom'
import { useCurrentUser } from '@/hooks/useAuth'
import { useOnboardingStatus } from '@/hooks/useOnboarding'

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const location = useLocation()
  const { data: user, isLoading: isLoadingUser, error } = useCurrentUser()
  const { data: onboardingStatus, isLoading: isLoadingOnboarding } = useOnboardingStatus()

  // Show loading spinner while checking authentication and onboarding
  if (isLoadingUser || isLoadingOnboarding) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  // If there's an error (e.g., no token or invalid token), redirect to login
  if (error || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check if user needs onboarding (unless they're already on the onboarding page)
  if (user && onboardingStatus && !onboardingStatus.completed && location.pathname !== '/app/onboarding') {
    return <Navigate to="/app/onboarding" replace />
  }

  // If user is on onboarding page but has already completed it, redirect to dashboard
  if (user && onboardingStatus?.completed && location.pathname === '/app/onboarding') {
    return <Navigate to="/app" replace />
  }

  // User is authenticated and has correct onboarding status, render children
  return <>{children}</>
}

// Public route guard (redirects authenticated users away from auth pages)
export function PublicGuard({ children }: AuthGuardProps) {
  const { data: user, isLoading: isLoadingUser } = useCurrentUser()
  const { data: onboardingStatus, isLoading: isLoadingOnboarding } = useOnboardingStatus()

  if (isLoadingUser || (user && isLoadingOnboarding)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  // If user is authenticated, redirect to appropriate page
  if (user) {
    // If user hasn't completed onboarding, redirect to onboarding
    if (onboardingStatus && !onboardingStatus.completed) {
      return <Navigate to="/app/onboarding" replace />
    }
    // If user has completed onboarding, redirect to app
    return <Navigate to="/app" replace />
  }

  // User is not authenticated, render children (login/signup pages)
  return <>{children}</>
}
