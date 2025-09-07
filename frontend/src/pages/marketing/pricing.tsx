import { MarketingLayout } from '@/components/layout/marketing-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

export function PricingPage() {
  const plans = [
    {
      name: "Free",
      price: "$0",
      description: "Perfect for small teams getting started",
      features: [
        "Up to 5 agents",
        "Basic monitoring",
        "Community support",
        "7-day data retention"
      ],
      cta: "Start Free",
      popular: false
    },
    {
      name: "Team",
      price: "$49",
      description: "For growing teams with advanced needs",
      features: [
        "Up to 50 agents",
        "Advanced automation",
        "Priority support",
        "30-day data retention",
        "Custom integrations",
        "Approval workflows"
      ],
      cta: "Start Trial",
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large organizations with custom requirements",
      features: [
        "Unlimited agents",
        "Enterprise features",
        "Dedicated support",
        "Unlimited data retention",
        "On-premise deployment",
        "SLA guarantees"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ]

  return (
    <MarketingLayout>
      <section className="py-24 md:py-32">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              Pricing
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-6">
              Simple, <span className="text-gradient">Transparent</span> Pricing
            </h1>
            <p className="text-xl text-muted-foreground">
              Choose the plan that fits your team. All plans include our core autonomous healing capabilities.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {plans.map((plan) => (
              <Card key={plan.name} className={`relative card-hover ${plan.popular ? 'border-blue-500 border-2' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-600 text-white px-3 py-1">
                      <Zap className="mr-1 h-3 w-3" />
                      Most Popular
                    </Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-3xl font-bold">{plan.price}</span>
                    {plan.price !== "Custom" && <span className="text-muted-foreground">/month</span>}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{plan.description}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className="w-full" 
                    variant={plan.popular ? "default" : "outline"}
                    asChild
                  >
                    <Link to="/signup">{plan.cta}</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </MarketingLayout>
  )
}
