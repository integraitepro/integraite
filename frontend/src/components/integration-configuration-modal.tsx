/**
 * Integration configuration modal component
 */

import React, { useState, useEffect } from 'react';
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
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, TestTube, Save, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  useCreateIntegration,
  useTestIntegrationConfig,
  useUserIntegrations
} from '@/hooks/useIntegrations';
import type { IntegrationProvider, ConfigurationField } from '@/services/integrations';

interface IntegrationConfigurationModalProps {
  provider: IntegrationProvider | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

// Dynamic form schema generation
const createFormSchema = (fields: ConfigurationField[]) => {
  const schemaFields: Record<string, z.ZodTypeAny> = {
    name: z.string().min(1, 'Integration name is required'),
    description: z.string().optional(),
  };

  fields.forEach((field) => {
    let fieldSchema: z.ZodTypeAny;

    switch (field.field_type) {
      case 'email':
        fieldSchema = z.string().email('Invalid email format');
        break;
      case 'url':
        fieldSchema = z.string().url('Invalid URL format');
        break;
      case 'number':
        fieldSchema = z.coerce.number();
        break;
      case 'boolean':
        fieldSchema = z.boolean();
        break;
      case 'json':
        fieldSchema = z.string().refine((val) => {
          try {
            JSON.parse(val);
            return true;
          } catch {
            return false;
          }
        }, 'Invalid JSON format');
        break;
      default:
        fieldSchema = z.string();
    }

    if (field.validation_regex) {
      fieldSchema = (fieldSchema as z.ZodString).regex(
        new RegExp(field.validation_regex),
        field.validation_message || 'Invalid format'
      );
    }

    if (!field.is_required) {
      fieldSchema = fieldSchema.optional();
    } else if (field.field_type !== 'boolean') {
      fieldSchema = (fieldSchema as z.ZodString).min(1, `${field.display_label} is required`);
    }

    schemaFields[field.field_name] = fieldSchema;
  });

  return z.object(schemaFields);
};

export function IntegrationConfigurationModal({
  provider,
  open,
  onOpenChange,
}: IntegrationConfigurationModalProps) {
  const [showSensitiveFields, setShowSensitiveFields] = useState<Record<string, boolean>>({});
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
    tested: boolean;
  } | null>(null);

  const createIntegrationMutation = useCreateIntegration();
  const testConfigMutation = useTestIntegrationConfig();
  const { data: userIntegrations } = useUserIntegrations();

  // Check if integration already exists for this provider
  const existingIntegration = userIntegrations?.find(
    integration => integration.provider_id === provider?.id && integration.is_active
  );

  // Create form schema based on provider configuration fields
  const formSchema = provider ? createFormSchema(provider.configuration_fields) : z.object({});
  
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: `${provider?.display_name} Integration`,
      description: '',
      ...provider?.configuration_fields.reduce((acc, field) => {
        acc[field.field_name] = field.default_value || '';
        return acc;
      }, {} as Record<string, any>)
    }
  });

  // Reset form when provider changes
  useEffect(() => {
    if (provider) {
      const defaultValues = {
        name: `${provider.display_name} Integration`,
        description: '',
        ...provider.configuration_fields.reduce((acc, field) => {
          acc[field.field_name] = field.default_value || (field.field_type === 'boolean' ? false : '');
          return acc;
        }, {} as Record<string, any>)
      };
      
      form.reset(defaultValues);
      setTestResult(null);
    }
  }, [provider, form]);

  const toggleSensitiveField = (fieldName: string) => {
    setShowSensitiveFields(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const handleTestConfiguration = async () => {
    if (!provider) return;

    try {
      const formData = form.getValues();
      const configuration = { ...formData };
      delete configuration.name;
      delete configuration.description;

      const result = await testConfigMutation.mutateAsync({
        providerId: provider.id,
        testData: { configuration }
      });

      setTestResult({
        success: result.success,
        message: result.message,
        tested: true
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Failed to test configuration',
        tested: true
      });
    }
  };

  const onSubmit = async (data: any) => {
    if (!provider) return;

    try {
      const { name, description, ...configuration } = data;
      
      await createIntegrationMutation.mutateAsync({
        provider_id: provider.id,
        name,
        description,
        configuration,
        integration_metadata: {},
      });

      onOpenChange(false);
    } catch (error) {
      // Error handling is done in the mutation
    }
  };

  const renderField = (field: ConfigurationField) => {
    const isPassword = field.field_type === 'password' || field.is_sensitive;
    const showPassword = showSensitiveFields[field.field_name];

    return (
      <FormField
        key={field.id}
        control={form.control}
        name={field.field_name}
        render={({ field: formField }) => (
          <FormItem>
            <FormLabel className="flex items-center gap-2">
              {field.display_label}
              {field.is_required && <span className="text-red-500">*</span>}
              {field.is_sensitive && <Badge variant="outline" className="text-xs">Sensitive</Badge>}
            </FormLabel>
            <FormControl>
              <div className="relative">
                {field.field_type === 'textarea' || field.field_type === 'json' ? (
                  <Textarea
                    placeholder={field.placeholder}
                    {...formField}
                    className={field.field_type === 'json' ? 'font-mono text-sm' : ''}
                  />
                ) : field.field_type === 'boolean' ? (
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={formField.value}
                      onCheckedChange={formField.onChange}
                    />
                    <span className="text-sm text-muted-foreground">
                      {formField.value ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                ) : field.field_type === 'select' && field.field_options ? (
                  <select
                    {...formField}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="">Select an option</option>
                    {field.field_options.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <Input
                    type={isPassword && !showPassword ? 'password' : 'text'}
                    placeholder={field.placeholder}
                    {...formField}
                  />
                )}
                
                {isPassword && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => toggleSensitiveField(field.field_name)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                )}
              </div>
            </FormControl>
            {field.description && (
              <FormDescription>{field.description}</FormDescription>
            )}
            <FormMessage />
          </FormItem>
        )}
      />
    );
  };

  const groupedFields = provider?.configuration_fields.reduce((acc, field) => {
    const group = field.field_group || 'general';
    if (!acc[group]) acc[group] = [];
    acc[group].push(field);
    return acc;
  }, {} as Record<string, ConfigurationField[]>) || {};

  // Sort fields within groups by sort_order
  Object.values(groupedFields).forEach(fields => {
    fields.sort((a, b) => a.sort_order - b.sort_order);
  });

  if (!provider) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            {provider.icon_url && (
              <img src={provider.icon_url} alt={provider.display_name} className="w-6 h-6" />
            )}
            Configure {provider.display_name}
          </DialogTitle>
          <DialogDescription>
            {existingIntegration 
              ? `Update your existing ${provider.display_name} integration.`
              : `Set up a new ${provider.display_name} integration to connect your services.`
            }
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Basic Information</h3>
              
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Integration Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="My AWS Integration" {...field} />
                    </FormControl>
                    <FormDescription>
                      A friendly name to identify this integration
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Optional description for this integration"
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Configuration Fields */}
            {Object.entries(groupedFields).map(([groupName, fields], groupIndex) => (
              <div key={groupName} className="space-y-4">
                {groupIndex > 0 && <Separator />}
                <h3 className="text-lg font-medium capitalize">
                  {groupName === 'general' ? 'Configuration' : groupName.replace('_', ' ')}
                </h3>
                <div className="grid gap-4">
                  {fields.map(renderField)}
                </div>
              </div>
            ))}

            {/* Test Result */}
            {testResult && (
              <Alert className={testResult.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className={testResult.success ? 'text-green-800' : 'text-red-800'}>
                  {testResult.message}
                </AlertDescription>
              </Alert>
            )}

            <DialogFooter className="flex justify-between">
              <Button
                type="button"
                variant="outline"
                onClick={handleTestConfiguration}
                disabled={testConfigMutation.isPending}
                className="flex items-center gap-2"
              >
                <TestTube className="w-4 h-4" />
                {testConfigMutation.isPending ? 'Testing...' : 'Test Connection'}
              </Button>
              
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={createIntegrationMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {createIntegrationMutation.isPending ? 'Saving...' : existingIntegration ? 'Update' : 'Create Integration'}
                </Button>
              </div>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
