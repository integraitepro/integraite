import { MarketingLayout } from '@/components/layout/marketing-layout'

export function DocsPage() {
  return (
    <MarketingLayout>
      <section className="py-24 md:py-32">
        <div className="container">
          <h1 className="text-4xl font-bold mb-6">Documentation</h1>
          <p className="text-xl text-muted-foreground">
            Complete documentation and guides coming soon...
          </p>
        </div>
      </section>
    </MarketingLayout>
  )
}
