import { MarketingLayout } from '@/components/layout/marketing-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ExternalLink, CheckCircle } from 'lucide-react'

export function IntegrationsPage() {
  const categories = [
    {
      title: "Observability & Monitoring",
      description: "Connect your monitoring and observability tools",
      integrations: [
        { name: "Prometheus", description: "Metrics collection and alerting", status: "available" },
        { name: "Datadog", description: "Full-stack monitoring platform", status: "available" },
        { name: "New Relic", description: "Application performance monitoring", status: "available" },
        { name: "Grafana", description: "Analytics and monitoring", status: "available" },
        { name: "Splunk", description: "Search, monitoring, and analysis", status: "coming-soon" },
        { name: "Elastic", description: "Search and analytics engine", status: "available" }
      ]
    },
    {
      title: "Incident Management",
      description: "Integrate with your incident response tools",
      integrations: [
        { name: "PagerDuty", description: "Digital operations management", status: "available" },
        { name: "Opsgenie", description: "Modern incident management", status: "available" },
        { name: "VictorOps", description: "Real-time incident management", status: "available" },
        { name: "xMatters", description: "Service reliability platform", status: "coming-soon" }
      ]
    },
    {
      title: "Ticketing & ITSM",
      description: "Connect with your service management platforms",
      integrations: [
        { name: "ServiceNow", description: "Enterprise service management", status: "available" },
        { name: "Jira Service Management", description: "IT service management", status: "available" },
        { name: "Zendesk", description: "Customer service platform", status: "available" },
        { name: "Freshservice", description: "IT service management", status: "coming-soon" }
      ]
    },
    {
      title: "Cloud Platforms",
      description: "Deploy and manage across cloud providers",
      integrations: [
        { name: "AWS", description: "Amazon Web Services", status: "available" },
        { name: "Google Cloud", description: "Google Cloud Platform", status: "available" },
        { name: "Microsoft Azure", description: "Microsoft cloud platform", status: "available" },
        { name: "Digital Ocean", description: "Cloud infrastructure", status: "available" },
        { name: "Kubernetes", description: "Container orchestration", status: "available" }
      ]
    },
    {
      title: "CI/CD & DevOps",
      description: "Integrate with your development workflow",
      integrations: [
        { name: "GitHub", description: "Development platform", status: "available" },
        { name: "GitLab", description: "DevOps platform", status: "available" },
        { name: "Jenkins", description: "Automation server", status: "available" },
        { name: "CircleCI", description: "Continuous integration", status: "available" },
        { name: "GitHub Actions", description: "Workflow automation", status: "available" }
      ]
    },
    {
      title: "Communication",
      description: "Keep your team informed and connected",
      integrations: [
        { name: "Slack", description: "Team collaboration", status: "available" },
        { name: "Microsoft Teams", description: "Collaboration platform", status: "available" },
        { name: "Discord", description: "Voice and text chat", status: "coming-soon" },
        { name: "Email", description: "Email notifications", status: "available" }
      ]
    }
  ]

  return (
    <MarketingLayout>
      {/* Hero Section */}
      <section className="py-24 md:py-32">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              Integrations
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-6">
              Connect Your <span className="text-gradient">Entire Stack</span>
            </h1>
            <p className="text-xl text-muted-foreground">
              Integraite seamlessly connects with your existing tools and platforms. 
              No rip-and-replace needed – just enhanced automation and intelligence.
            </p>
          </div>

          {/* Integration Stats */}
          <div className="grid gap-8 md:grid-cols-3 mb-16">
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-3xl font-bold text-blue-600 mb-2">50+</div>
                <div className="text-sm text-muted-foreground">Supported Integrations</div>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-3xl font-bold text-green-600 mb-2">&lt; 5min</div>
                <div className="text-sm text-muted-foreground">Average Setup Time</div>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="text-3xl font-bold text-purple-600 mb-2">99.9%</div>
                <div className="text-sm text-muted-foreground">Uptime SLA</div>
              </CardContent>
            </Card>
          </div>

          {/* Integration Categories */}
          <div className="space-y-12">
            {categories.map((category) => (
              <div key={category.title}>
                <div className="mb-8">
                  <h2 className="text-2xl font-bold mb-2">{category.title}</h2>
                  <p className="text-muted-foreground">{category.description}</p>
                </div>
                
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {category.integrations.map((integration) => (
                    <Card key={integration.name} className="card-hover">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">{integration.name}</CardTitle>
                          {integration.status === 'available' ? (
                            <Badge variant="success" className="text-xs">
                              <CheckCircle className="mr-1 h-3 w-3" />
                              Available
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-xs">
                              Coming Soon
                            </Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <p className="text-sm text-muted-foreground mb-4">
                          {integration.description}
                        </p>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          disabled={integration.status !== 'available'}
                          className="w-full"
                        >
                          {integration.status === 'available' ? (
                            <>
                              View Details
                              <ExternalLink className="ml-2 h-3 w-3" />
                            </>
                          ) : (
                            'Notify Me'
                          )}
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Custom Integration CTA */}
          <Card className="mt-16 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/50 dark:to-purple-950/50 border-2">
            <CardContent className="p-8 text-center">
              <h3 className="text-xl font-bold mb-4">Don't see your tool?</h3>
              <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                We're constantly adding new integrations. If you don't see the tool you need, 
                let us know and we'll prioritize it for our next release.
              </p>
              <Button size="lg">
                Request Integration
                <ExternalLink className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </MarketingLayout>
  )
}
