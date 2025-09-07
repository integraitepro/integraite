import { MarketingLayout } from '@/components/layout/marketing-layout'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Shield, Lock, Eye, FileCheck, Database, Globe } from 'lucide-react'

export function SecurityPage() {
  return (
    <MarketingLayout>
      <section className="py-24 md:py-32">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center mb-16">
            <Badge variant="secondary" className="mb-4">
              Security & Compliance
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-6">
              <span className="text-gradient">Enterprise-Grade</span> Security
            </h1>
            <p className="text-xl text-muted-foreground">
              Your data security and compliance are our top priorities. 
              Built with enterprise security standards from day one.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <Card className="card-hover">
              <CardContent className="p-6">
                <Shield className="h-12 w-12 text-blue-600 mb-4" />
                <h3 className="font-semibold mb-2">SOC 2 Type II Certified</h3>
                <p className="text-sm text-muted-foreground">
                  Independently audited security controls and practices.
                </p>
              </CardContent>
            </Card>
            
            <Card className="card-hover">
              <CardContent className="p-6">
                <Lock className="h-12 w-12 text-green-600 mb-4" />
                <h3 className="font-semibold mb-2">End-to-End Encryption</h3>
                <p className="text-sm text-muted-foreground">
                  Data encrypted in transit and at rest with AES-256.
                </p>
              </CardContent>
            </Card>
            
            <Card className="card-hover">
              <CardContent className="p-6">
                <Eye className="h-12 w-12 text-purple-600 mb-4" />
                <h3 className="font-semibold mb-2">Zero-Trust Architecture</h3>
                <p className="text-sm text-muted-foreground">
                  Every request is verified and authenticated.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </MarketingLayout>
  )
}
