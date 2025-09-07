import { MarketingLayout } from '@/components/layout/marketing-layout'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Eye, Brain, Lightbulb, Play, CheckCircle, RotateCcw } from 'lucide-react'

export function HowItWorksPage() {
  const steps = [
    {
      icon: Eye,
      title: "Observe",
      description: "Continuously monitor your entire infrastructure, applications, and services across all environments.",
      details: ["Real-time metrics collection", "Log aggregation and analysis", "Distributed tracing", "Performance monitoring"]
    },
    {
      icon: Brain,
      title: "Understand", 
      description: "AI analyzes patterns, correlates data points, and identifies potential issues before they escalate.",
      details: ["Pattern recognition", "Anomaly detection", "Root cause analysis", "Impact assessment"]
    },
    {
      icon: Lightbulb,
      title: "Plan",
      description: "Generate intelligent remediation plans with confidence scores and blast radius calculations.",
      details: ["Automated planning", "Risk assessment", "Approval workflows", "Rollback strategies"]
    },
    {
      icon: Play,
      title: "Act",
      description: "Execute remediation actions automatically or with human approval based on configured policies.",
      details: ["Automated execution", "Manual approval gates", "Canary deployments", "Safe rollouts"]
    },
    {
      icon: CheckCircle,
      title: "Verify",
      description: "Validate that actions resolved the issue and monitor for any side effects or regressions.",
      details: ["Health validation", "SLO monitoring", "Side effect detection", "Performance verification"]
    },
    {
      icon: RotateCcw,
      title: "Learn",
      description: "Continuously improve the system by learning from each incident and successful remediation.",
      details: ["Pattern learning", "Model updates", "Playbook refinement", "Knowledge accumulation"]
    }
  ]

  return (
    <MarketingLayout>
      {/* Hero Section */}
      <section className="py-24 md:py-32">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              How It Works
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-6">
              The Six-Step <span className="text-gradient">Autonomous Cycle</span>
            </h1>
            <p className="text-xl text-muted-foreground">
              Our AI-powered platform follows a proven methodology to prevent incidents 
              and maintain system reliability through continuous learning and adaptation.
            </p>
          </div>

          {/* Visual Stepper */}
          <div className="grid gap-8 md:gap-12">
            {steps.map((step, index) => {
              const Icon = step.icon
              const isLast = index === steps.length - 1
              
              return (
                <div key={step.title} className="relative">
                  <div className="flex flex-col md:flex-row items-start gap-8">
                    {/* Step indicator */}
                    <div className="flex flex-col items-center">
                      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
                        <Icon className="h-8 w-8" />
                      </div>
                      <div className="mt-2 text-sm font-medium text-center">
                        Step {index + 1}
                      </div>
                      {!isLast && (
                        <div className="mt-4 h-16 w-px bg-gradient-to-b from-blue-600 to-purple-600 opacity-30 hidden md:block" />
                      )}
                    </div>

                    {/* Content */}
                    <Card className="flex-1 card-hover">
                      <CardContent className="p-8">
                        <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
                        <p className="text-lg text-muted-foreground mb-6">
                          {step.description}
                        </p>
                        <div className="grid gap-3 md:grid-cols-2">
                          {step.details.map((detail) => (
                            <div key={detail} className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 text-green-600" />
                              <span className="text-sm">{detail}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {/* Connection line for mobile */}
                  {!isLast && (
                    <div className="mt-8 h-px bg-gradient-to-r from-blue-600 to-purple-600 opacity-30 md:hidden" />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </section>
    </MarketingLayout>
  )
}
