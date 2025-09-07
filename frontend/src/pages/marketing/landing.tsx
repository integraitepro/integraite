import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { MarketingLayout } from '@/components/layout/marketing-layout'
import { 
  Zap, 
  Eye, 
  Gauge, 
  RefreshCw, 
  TrendingUp, 
  Shield, 
  Clock, 
  Brain,
  ArrowRight,
  Play,
  CheckCircle2
} from 'lucide-react'

export function LandingPage() {
  return (
    <MarketingLayout>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-purple-600/5 to-indigo-600/5" />
        <div className="relative container py-24 md:py-32">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-6 px-4 py-2">
              <Zap className="mr-2 h-4 w-4" />
              Autonomous Self-Healing Operations
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl md:text-7xl">
              <span className="text-gradient">Transform Your Ops</span>
              <br />
              <span className="text-foreground">Before Incidents Happen</span>
            </h1>
            <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground sm:text-xl">
              Integraite's AI-powered platform observes, understands, and automatically fixes issues 
              in your infrastructure before they impact your users. Join thousands of teams preventing incidents.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" className="text-base px-8 py-3" asChild>
                <Link to="/signup">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="text-base px-8 py-3">
                <Play className="mr-2 h-4 w-4" />
                Watch Demo
              </Button>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              14-day free trial • No credit card required • Setup in minutes
            </p>
          </div>
          
          {/* Hero Visual */}
          <div className="mx-auto mt-16 max-w-6xl">
            <Card className="overflow-hidden border-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 backdrop-blur-sm">
              <CardContent className="p-8">
                <div className="grid gap-6 md:grid-cols-3">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500/20">
                        <Eye className="h-4 w-4 text-green-600" />
                      </div>
                      <span className="text-sm font-medium">Observing</span>
                    </div>
                    <div className="space-y-2 text-xs text-muted-foreground">
                      <div>↳ CPU usage spike detected</div>
                      <div>↳ Memory leak identified</div>
                      <div>↳ Database slowdown</div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500/20">
                        <Brain className="h-4 w-4 text-blue-600" />
                      </div>
                      <span className="text-sm font-medium">Understanding</span>
                    </div>
                    <div className="space-y-2 text-xs text-muted-foreground">
                      <div>↳ Root cause: Memory leak in service-A</div>
                      <div>↳ Impact: 15% performance degradation</div>
                      <div>↳ Confidence: 94%</div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/20">
                        <RefreshCw className="h-4 w-4 text-purple-600" />
                      </div>
                      <span className="text-sm font-medium">Acting</span>
                    </div>
                    <div className="space-y-2 text-xs text-muted-foreground">
                      <div>↳ Graceful restart initiated</div>
                      <div>↳ Health checks passed</div>
                      <div>↳ Issue resolved ✓</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Why Choose Integraite */}
      <section className="py-24 md:py-32">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Why Choose Integraite
            </h2>
            <p className="text-lg text-muted-foreground">
              Our autonomous platform transforms how teams handle operations, 
              preventing incidents before they impact your business.
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            <Card className="card-hover border-2">
              <CardContent className="p-6">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-green-500/10">
                  <Eye className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="mb-2 font-semibold">Proactive Detection</h3>
                <p className="text-sm text-muted-foreground">
                  AI-powered monitoring identifies issues before they become incidents, 
                  analyzing patterns across your entire stack.
                </p>
              </CardContent>
            </Card>
            
            <Card className="card-hover border-2">
              <CardContent className="p-6">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10">
                  <Zap className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="mb-2 font-semibold">Instant Response</h3>
                <p className="text-sm text-muted-foreground">
                  Automated remediation actions execute in seconds, not minutes. 
                  Your systems heal themselves while you sleep.
                </p>
              </CardContent>
            </Card>
            
            <Card className="card-hover border-2">
              <CardContent className="p-6">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10">
                  <Brain className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="mb-2 font-semibold">Continuous Learning</h3>
                <p className="text-sm text-muted-foreground">
                  Every incident makes the system smarter. Machine learning 
                  improves detection and response over time.
                </p>
              </CardContent>
            </Card>
            
            <Card className="card-hover border-2">
              <CardContent className="p-6">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-orange-500/10">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
                <h3 className="mb-2 font-semibold">99.9% Uptime</h3>
                <p className="text-sm text-muted-foreground">
                  Proven track record of maintaining exceptional uptime 
                  through intelligent incident prevention.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Ready to Transform CTA */}
      <section className="py-24 md:py-32 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center text-white">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">
              Ready to Transform Your Operations?
            </h2>
            <p className="text-xl mb-8 text-blue-100">
              Join thousands of teams already using autonomous ops to prevent incidents 
              and improve reliability. Start your transformation today.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" variant="secondary" className="text-base px-8 py-3" asChild>
                <Link to="/signup">
                  Get Started Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-base px-8 py-3 bg-white/10 border-white/20 text-white hover:bg-white/20">
                <Link to="/how-it-works">Learn More</Link>
              </Button>
            </div>
            <div className="mt-8 flex items-center justify-center gap-8 text-sm text-blue-100">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                <span>14-day free trial</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                <span>Setup in minutes</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </MarketingLayout>
  )
}
