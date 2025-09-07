/**
 * Integrations management page
 */

import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/app-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import {
  useIntegrationProviders,
  useUserIntegrations,
  useIntegrationStats
} from '@/hooks/useIntegrations';
import type { IntegrationProvider } from '@/services/integrations';
import { IntegrationConfigurationModal } from '@/components/integration-configuration-modal';
import { RequestIntegrationModal } from '@/components/request-integration-modal';
import {
  Plus, Search, Grid, List, Settings, 
  Cloud, Database, MessageSquare, Shield, 
  Monitor, Zap, Server, Network, Mail,
  Eye, MoreHorizontal, CheckCircle2, AlertCircle,
  Clock, TrendingUp, Filter, Star, ExternalLink,
  PlayCircle, PauseCircle, Download, Upload,
  Activity, BarChart3, Workflow, Link, KeyRound
} from 'lucide-react';

// Category metadata mapping
const categoryMetadata: Record<string, {
  name: string;
  icon: any;
  color: string;
  bgColor: string;
  description: string;
}> = {
  cloud_infrastructure: { 
    name: 'Cloud Infrastructure', 
    icon: Cloud, 
    color: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    description: 'AWS, Azure, GCP services'
  },
  monitoring: { 
    name: 'Monitoring & Observability', 
    icon: Monitor, 
    color: 'text-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/20',
    description: 'Performance and health monitoring'
  },
  incident_management: { 
    name: 'Incident Management', 
    icon: AlertCircle, 
    color: 'text-red-600',
    bgColor: 'bg-red-100 dark:bg-red-900/20',
    description: 'Issue tracking and alerting'
  },
  communication: { 
    name: 'Communication', 
    icon: MessageSquare, 
    color: 'text-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    description: 'Team collaboration tools'
  },
  security: { 
    name: 'Security & Compliance', 
    icon: Shield, 
    color: 'text-orange-600',
    bgColor: 'bg-orange-100 dark:bg-orange-900/20',
    description: 'Security scanning and compliance'
  },
  other: { 
    name: 'Other', 
    icon: Settings, 
    color: 'text-gray-600',
    bgColor: 'bg-gray-100 dark:bg-gray-900/20',
    description: 'Miscellaneous integrations'
  }
};

export default function IntegrationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<IntegrationProvider | null>(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false);

  const { data: providers, isLoading: providersLoading, error: providersError } = useIntegrationProviders({
    search: searchQuery || undefined,
    category: selectedCategory || undefined
  });
  const { data: userIntegrations, isLoading: userIntegrationsLoading } = useUserIntegrations();
  const { data: stats, isLoading: statsLoading, error: statsError } = useIntegrationStats();

  // Debug API responses
  React.useEffect(() => {
    console.log('🔍 Integration API Debug:', {
      providers: {
        data: providers,
        loading: providersLoading,
        error: providersError?.message,
        hasData: !!providers,
        length: providers?.length
      },
      stats: {
        data: stats,
        loading: statsLoading,
        error: statsError?.message,
        hasData: !!stats
      },
      userIntegrations: {
        data: userIntegrations,
        loading: userIntegrationsLoading,
        hasData: !!userIntegrations,
        length: userIntegrations?.length
      }
    });
  }, [providers, providersLoading, providersError, stats, statsLoading, statsError, userIntegrations, userIntegrationsLoading]);

  const handleConfigureProvider = (provider: IntegrationProvider) => {
    setSelectedProvider(provider);
    setIsConfigModalOpen(true);
  };

  const handleRequestIntegration = () => {
    setIsRequestModalOpen(true);
  };

  const getProviderIcon = (provider: IntegrationProvider) => {
    if (provider.icon_url) {
      return (
        <img 
          src={provider.icon_url} 
          alt={provider.display_name}
          className="w-8 h-8 object-contain"
          onError={(e) => {
            e.currentTarget.style.display = 'none';
            e.currentTarget.nextElementSibling?.classList.remove('hidden');
          }}
        />
      );
    }
    return <Settings className="w-8 h-8 text-muted-foreground" />;
  };

  const getCategoryIcon = (categoryId: string) => {
    return categoryMetadata[categoryId]?.icon || Settings;
  };

  const getCategoryColor = (categoryId: string) => {
    return categoryMetadata[categoryId]?.color || 'text-gray-600';
  };

  // Create dynamic categories from API stats
  const integrationCategories = React.useMemo(() => {
    if (!stats?.providers_by_category) return [];
    
    return Object.entries(stats.providers_by_category).map(([categoryId, count]) => ({
      id: categoryId,
      name: categoryMetadata[categoryId]?.name || categoryId.replace('_', ' '),
      icon: categoryMetadata[categoryId]?.icon || Settings,
      color: categoryMetadata[categoryId]?.color || 'text-gray-600',
      bgColor: categoryMetadata[categoryId]?.bgColor || 'bg-gray-100 dark:bg-gray-900/20',
      count: count as number,
      description: categoryMetadata[categoryId]?.description || 'Various integrations'
    }));
  }, [stats]);

  // Use real stats from API
  const displayStats = stats || {
    total_providers: 0,
    active_providers: 0,
    total_user_integrations: 0,
    active_user_integrations: 0,
    pending_requests: 0,
    providers_by_category: {},
    integrations_by_category: {},
    popular_providers: []
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
            <p className="text-muted-foreground mt-2">
              Connect your tools and services to enable autonomous operations across your entire stack
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex items-center space-x-2">
            <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-200">
              <div className="w-2 h-2 rounded-full bg-blue-500 mr-2" />
              {displayStats.active_providers} Active Providers
            </Badge>
            <Button onClick={handleRequestIntegration}>
              <Plus className="mr-2 h-4 w-4" />
              Request Integration
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Available Providers
              </CardTitle>
              <Cloud className="h-5 w-5 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{displayStats.active_providers}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <TrendingUp className="mr-1 h-3 w-3 text-green-600" />
                of {displayStats.total_providers} total
              </div>
              <p className="text-xs text-muted-foreground mt-1">Ready to integrate</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Your Integrations
              </CardTitle>
              <Link className="h-5 w-5 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{displayStats.active_user_integrations}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <Activity className="mr-1 h-3 w-3 text-green-600" />
                active connections
              </div>
              <p className="text-xs text-muted-foreground mt-1">Currently configured</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending Requests
              </CardTitle>
              <Clock className="h-5 w-5 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{displayStats.pending_requests}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <Clock className="mr-1 h-3 w-3 text-orange-600" />
                awaiting approval
              </div>
              <p className="text-xs text-muted-foreground mt-1">Custom integrations</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Categories
              </CardTitle>
              <BarChart3 className="h-5 w-5 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {displayStats.providers_by_category ? Object.keys(displayStats.providers_by_category).length : 0}
              </div>
              <div className="flex items-center text-xs text-muted-foreground">
                <Workflow className="mr-1 h-3 w-3 text-purple-600" />
                integration types
              </div>
              <p className="text-xs text-muted-foreground mt-1">Covering all services</p>
            </CardContent>
          </Card>
        </div>

        {/* Categories Overview */}
        {integrationCategories.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Integration Categories
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </CardTitle>
              <CardDescription>
                Browse integrations by category to find the tools that match your needs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-5">
                {integrationCategories.map((category) => {
                  const Icon = category.icon;
                  const isSelected = selectedCategory === category.id;
                  
                  return (
                    <Card 
                      key={category.id}
                      className={cn(
                        "cursor-pointer transition-all duration-200 hover:shadow-md",
                        isSelected ? "ring-2 ring-primary ring-offset-2" : "hover:border-muted-foreground/50"
                      )}
                      onClick={() => setSelectedCategory(isSelected ? null : category.id)}
                    >
                      <CardContent className="p-4 text-center">
                        <div className={cn(
                          "w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center",
                          category.bgColor
                        )}>
                          <Icon className={cn("h-6 w-6", category.color)} />
                        </div>
                        <div className="font-medium text-sm mb-1">{category.name}</div>
                        <div className="text-xs text-muted-foreground mb-2">{category.description}</div>
                        <Badge variant="secondary" className="text-xs">
                          {category.count} available
                        </Badge>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search integrations by name, description, or technology..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
            <div className="flex rounded-lg border p-1">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('grid')}
                className="h-8"
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('list')}
                className="h-8"
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Content Tabs */}
        <Tabs defaultValue="available" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="available">Available Integrations</TabsTrigger>
            <TabsTrigger value="configured">Your Integrations ({displayStats.active_user_integrations})</TabsTrigger>
            <TabsTrigger value="requests">Requests ({displayStats.pending_requests})</TabsTrigger>
          </TabsList>

          <TabsContent value="available" className="space-y-6">
            {selectedCategory && (
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="flex items-center space-x-2">
                  {(() => {
                    const Icon = getCategoryIcon(selectedCategory);
                    return <Icon className="h-3 w-3" />;
                  })()}
                  <span>
                    {categoryMetadata[selectedCategory]?.name || selectedCategory.replace('_', ' ')}
                  </span>
                </Badge>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setSelectedCategory(null)}
                  className="h-6 px-2 text-xs"
                >
                  Clear filter
                </Button>
              </div>
            )}

            {providersLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  <span>Loading integrations...</span>
                </div>
              </div>
            ) : providersError ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Failed to Load Integrations</h3>
                  <p className="text-muted-foreground mb-4">
                    Error: {providersError?.message || 'Unknown error'}
                  </p>
                  <Button variant="outline" onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                </CardContent>
              </Card>
            ) : providers && providers.length > 0 ? (
              <div className={cn(
                "grid gap-6",
                viewMode === 'grid' 
                  ? "md:grid-cols-2 lg:grid-cols-3" 
                  : "grid-cols-1"
              )}>
                {providers.map((provider) => {
                  const Icon = getCategoryIcon(provider.category);
                  const categoryColor = getCategoryColor(provider.category);
                  
                  return (
                    <Card key={provider.id} className="card-hover group">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="relative">
                              {getProviderIcon(provider)}
                              <Icon className={cn("w-4 h-4 hidden", categoryColor)} />
                            </div>
                            <div>
                              <CardTitle className="text-lg group-hover:text-primary transition-colors">
                                {provider.display_name}
                              </CardTitle>
                              <div className="flex items-center space-x-2">
                                <Badge variant="secondary" className="text-xs">
                                  {provider.category.replace('_', ' ')}
                                </Badge>
                                <Badge 
                                  variant={provider.status === 'active' ? 'default' : 'secondary'}
                                  className="text-xs"
                                >
                                  {provider.status}
                                </Badge>
                                {provider.is_featured && (
                                  <Star className="h-3 w-3 text-yellow-500 fill-current" />
                                )}
                              </div>
                            </div>
                          </div>
                          <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <CardDescription className="mb-4 line-clamp-2">
                          {provider.description}
                        </CardDescription>
                        
                        {provider.supported_features && (
                          <div className="mb-4">
                            <div className="text-xs font-medium text-muted-foreground mb-2">Features:</div>
                            <div className="flex flex-wrap gap-1">
                              {provider.supported_features.slice(0, 3).map((feature, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {feature}
                                </Badge>
                              ))}
                              {provider.supported_features.length > 3 && (
                                <Badge variant="outline" className="text-xs">
                                  +{provider.supported_features.length - 3} more
                                </Badge>
                              )}
                            </div>
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <Button 
                            size="sm" 
                            className="flex-1"
                            onClick={() => handleConfigureProvider(provider)}
                          >
                            <PlayCircle className="mr-2 h-4 w-4" />
                            Configure
                          </Button>
                          {provider.documentation_url && (
                            <Button variant="ghost" size="sm" className="ml-2">
                              <ExternalLink className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Settings className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Integrations Found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery 
                      ? "No integrations match your search criteria. Try adjusting your filters."
                      : "We're working on adding more integration providers."
                    }
                  </p>
                  <Button variant="outline" onClick={handleRequestIntegration}>
                    <Plus className="mr-2 h-4 w-4" />
                    Request New Integration
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="configured" className="space-y-6">
            {userIntegrationsLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  <span>Loading your integrations...</span>
                </div>
              </div>
            ) : userIntegrations && userIntegrations.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {userIntegrations.map((integration) => (
                  <Card key={integration.id} className="card-hover">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getProviderIcon(integration.provider)}
                          <div>
                            <CardTitle className="text-lg">{integration.name}</CardTitle>
                            <div className="flex items-center space-x-2">
                              <Badge 
                                variant={integration.is_active ? 'default' : 'secondary'}
                                className="text-xs"
                              >
                                {integration.is_active ? (
                                  <>
                                    <CheckCircle2 className="mr-1 h-3 w-3" />
                                    Active
                                  </>
                                ) : (
                                  <>
                                    <PauseCircle className="mr-1 h-3 w-3" />
                                    Inactive
                                  </>
                                )}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {integration.provider.display_name}
                              </span>
                            </div>
                          </div>
                        </div>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      {integration.description && (
                        <CardDescription className="mb-4">
                          {integration.description}
                        </CardDescription>
                      )}
                      
                      <div className="space-y-3">
                        <div className="text-xs font-medium text-muted-foreground">
                          Connected: {new Date(integration.created_at).toLocaleDateString()}
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <Button variant="outline" size="sm" className="flex-1 mr-2">
                            <Settings className="mr-2 h-4 w-4" />
                            Manage
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            className={integration.is_active ? "text-orange-600" : "text-green-600"}
                          >
                            {integration.is_active ? (
                              <PauseCircle className="h-4 w-4" />
                            ) : (
                              <PlayCircle className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Link className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Integrations Configured</h3>
                  <p className="text-muted-foreground mb-4">
                    Start connecting your tools and services to enable autonomous operations.
                  </p>
                  <Button onClick={() => {/* Switch to available tab */}}>
                    <Plus className="mr-2 h-4 w-4" />
                    Browse Available Integrations
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="requests" className="space-y-6">
            <Card>
              <CardContent className="p-8 text-center">
                <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Pending Requests</h3>
                <p className="text-muted-foreground mb-4">
                  You haven't requested any custom integrations yet.
                </p>
                <Button onClick={handleRequestIntegration}>
                  <Plus className="mr-2 h-4 w-4" />
                  Request Custom Integration
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Configuration Modal */}
        <IntegrationConfigurationModal
          provider={selectedProvider}
          open={isConfigModalOpen}
          onOpenChange={setIsConfigModalOpen}
        />

        {/* Request Integration Modal */}
        <RequestIntegrationModal
          open={isRequestModalOpen}
          onOpenChange={setIsRequestModalOpen}
        />
      </div>
    </AppLayout>
  );
}