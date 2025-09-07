/**
 * Request integration modal component
 */

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send } from 'lucide-react';
import { useCreateIntegrationRequest } from '@/hooks/useIntegrations';
import { integrationsService } from '@/services/integrations';

interface RequestIntegrationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const formSchema = z.object({
  service_name: z.string().min(1, 'Service name is required').max(255),
  service_url: z.string().url('Invalid URL format').optional().or(z.literal('')),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  business_justification: z.string().optional(),
  expected_usage: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  category: z.string().optional(),
  estimated_users: z.coerce.number().int().min(1).optional(),
});

type FormData = z.infer<typeof formSchema>;

export function RequestIntegrationModal({
  open,
  onOpenChange,
}: RequestIntegrationModalProps) {
  const createRequestMutation = useCreateIntegrationRequest();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      service_name: '',
      service_url: '',
      description: '',
      business_justification: '',
      expected_usage: '',
      priority: 'medium',
      category: '',
      estimated_users: undefined,
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      await createRequestMutation.mutateAsync({
        ...data,
        service_url: data.service_url || undefined,
        business_justification: data.business_justification || undefined,
        expected_usage: data.expected_usage || undefined,
        category: data.category || undefined,
        estimated_users: data.estimated_users || undefined,
      });

      form.reset();
      onOpenChange(false);
    } catch (error) {
      // Error handling is done in the mutation
    }
  };

  const categories = [
    { value: 'cloud_infrastructure', label: 'Cloud Infrastructure' },
    { value: 'monitoring', label: 'Monitoring & Observability' },
    { value: 'incident_management', label: 'Incident Management' },
    { value: 'communication', label: 'Communication' },
    { value: 'version_control', label: 'Version Control' },
    { value: 'ci_cd', label: 'CI/CD' },
    { value: 'security', label: 'Security' },
    { value: 'database', label: 'Database' },
    { value: 'container', label: 'Container' },
    { value: 'logging', label: 'Logging' },
    { value: 'analytics', label: 'Analytics' },
    { value: 'storage', label: 'Storage' },
    { value: 'networking', label: 'Networking' },
    { value: 'other', label: 'Other' },
  ];

  const priorities = [
    { value: 'low', label: 'Low - Nice to have' },
    { value: 'medium', label: 'Medium - Would be helpful' },
    { value: 'high', label: 'High - Important for our workflow' },
    { value: 'critical', label: 'Critical - Blocking our operations' },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Request New Integration</DialogTitle>
          <DialogDescription>
            Let us know about a service or tool you'd like to integrate with Integraite.
            We'll review your request and prioritize it based on demand and feasibility.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Service Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Service Information</h3>
              
              <FormField
                control={form.control}
                name="service_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Service Name *</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="e.g., Jira, GitHub, Splunk" 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      The name of the service or tool you want to integrate
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="service_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Service Website (Optional)</FormLabel>
                    <FormControl>
                      <Input 
                        type="url"
                        placeholder="https://example.com" 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      Official website or documentation URL for the service
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category (Optional)</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a category" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {categories.map((category) => (
                          <SelectItem key={category.value} value={category.value}>
                            {category.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      What type of service is this?
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Request Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Request Details</h3>
              
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description *</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe the service and what kind of integration you need..."
                        className="min-h-[100px]"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Provide details about the service and the type of integration you're looking for
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="business_justification"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Business Justification (Optional)</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Explain how this integration would benefit your organization..."
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Help us understand the business value and impact of this integration
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="expected_usage"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Expected Usage (Optional)</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="How do you plan to use this integration..."
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Describe specific use cases and workflows you have in mind
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Priority and Impact */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Priority & Impact</h3>
              
              <FormField
                control={form.control}
                name="priority"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Priority *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {priorities.map((priority) => (
                          <SelectItem key={priority.value} value={priority.value}>
                            {priority.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      How important is this integration for your operations?
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="estimated_users"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Estimated Users (Optional)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        placeholder="e.g., 10"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      How many people in your organization would use this integration?
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={createRequestMutation.isPending}
                className="flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                {createRequestMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
