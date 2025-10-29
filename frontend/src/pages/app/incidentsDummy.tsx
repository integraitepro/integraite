"use client";
import { useEffect, useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangle,
  Clock,
  CheckCircle2,
  Eye,
  Activity,
  XCircle,
  ArrowUpRight,
  CalendarDays,
} from "lucide-react";
import { cn } from "@/lib/utils";

// 🧱 Default structure to avoid null UI errors
const defaultIncident = {
  id: "temp-incident",
  incident_id: "INC-DUMMY",
  title: "No title provided",
  description: "No description yet",
  severity: "low",
  status: "investigating",
  impact: "Low",
  assigned_agent: "Unassigned",
  assignment_group: "N/A",
  agents_involved: 1,
  confidence: 50,
  estimated_resolution: "2 hours",
  actions: [
    {
      type: "detect",
      description: "No actions yet",
      time: new Date().toLocaleTimeString(),
    },
  ],
  start_time: new Date().toISOString(),
  last_update: new Date().toISOString(),
  affected_services: [] as string[],
  u_ip_address: "192.168.0.1",
  u_service_name: "N/A",
  u_environment: "N/A",
  u_alert_type: "N/A",
  u_severity: "N/A",
};

const mapUrgencyToSeverity = (urgency?: string, priority?: string) => {
  if (urgency === "1" || priority === "1") return "critical";
  if (urgency === "2" || priority === "2") return "high";
  if (urgency === "3" || priority === "3") return "medium";
  return "low";
};

const mapStateToStatus = (state?: string) => {
  switch (state) {
    case "1":
      return "investigating";
    case "2":
      return "remediating";
    case "3":
      return "resolved";
    case "4":
      return "closed";
    default:
      return "investigating";
  }
};

export function IncidentsDummyPage() {
  const [incident, setIncident] = useState<any>(defaultIncident);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(
          "http://localhost:8000/webhook/servicenow/latest"
        );
        if (res.ok) {
          const json = await res.json();
          console.log("Webhook incident payload:", json);

          setIncident((prev: any) => ({
            ...prev,
            incident_id: json.number || prev.incident_id,
            title: json.short_description || prev.title,
            description:
              json.description || json.short_description || prev.description,
            severity:
              mapUrgencyToSeverity(json.urgency, json.priority) ||
              prev.severity,
            status: mapStateToStatus(json.state) || prev.status,
            impact: json.impact || prev.impact,
            assigned_agent: json.assigned_to || prev.assigned_agent,
            assignment_group: json.assignment_group || prev.assignment_group,
            start_time: json.opened_at || prev.start_time,
            last_update: json.updated_at || prev.last_update,
            u_ip_address: json.u_ip_address || prev.u_ip_address,
            u_service_name: json.u_service_name || prev.u_service_name,
            u_environment: json.u_environment || prev.u_environment,
            u_alert_type: json.u_alert_type || prev.u_alert_type,
            u_severity: json.u_severity || prev.u_severity,
            affected_services: json.u_service_name
              ? [json.u_service_name]
              : prev.affected_services,
          }));
        }
      } catch (err) {
        console.error("Error fetching webhook:", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400";
      case "low":
        return "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "investigating":
        return "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400";
      case "remediating":
        return "bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400";
      case "resolved":
        return "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400";
      case "closed":
        return "bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400";
      default:
        return "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "investigating":
        return <Eye className="h-3 w-3" />;
      case "remediating":
        return <Activity className="h-3 w-3" />;
      case "resolved":
        return <CheckCircle2 className="h-3 w-3" />;
      case "closed":
        return <XCircle className="h-3 w-3" />;
      default:
        return <Clock className="h-3 w-3" />;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMinutes = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60)
    );
    if (diffInMinutes < 60) return `${diffInMinutes} min ago`;
    if (diffInMinutes < 1440)
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
    return `${Math.floor(diffInMinutes / 1440)} days ago`;
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Incidents</h1>
            <p className="text-muted-foreground mt-2">
              Monitor and manage incidents with real-time ServiceNow updates
            </p>
          </div>
        </div>

        <Card
          className="hover:shadow-md transition-all duration-200 border-l-4"
          style={{
            borderLeftColor:
              incident.severity === "critical"
                ? "#dc2626"
                : incident.severity === "high"
                ? "#ea580c"
                : incident.severity === "medium"
                ? "#ca8a04"
                : "#16a34a",
          }}
        >
          <CardHeader>
            <div className="flex justify-between">
              <CardTitle>{incident.title}</CardTitle>
              <ArrowUpRight className="h-5 w-5 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">{incident.description}</p>

            <div className="flex space-x-2">
              <Badge
                className={cn(
                  "text-xs border",
                  getSeverityColor(incident.severity)
                )}
              >
                {incident.severity.toUpperCase()}
              </Badge>
              <Badge
                className={cn(
                  "text-xs border flex items-center space-x-1",
                  getStatusColor(incident.status)
                )}
              >
                {getStatusIcon(incident.status)}
                <span>{incident.status}</span>
              </Badge>
              <Badge variant="outline" className="text-xs">
                {incident.impact}
              </Badge>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-3 border-t border-b">
              <div className="text-center">
                <p className="text-xs text-muted-foreground">IP Address</p>
                <p className="text-sm font-medium">
                  {incident.u_ip_address || "N/A"}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Assigned Agent</p>
                <p className="text-sm font-medium">
                  {incident.assigned_agent || "Unassigned"}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Service</p>
                <p className="text-sm font-medium">
                  {incident.u_service_name || "N/A"}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Environment</p>
                <p className="text-sm font-medium">
                  {incident.u_environment || "N/A"}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">
                Recent Actions
              </p>
              <div className="space-y-1">
                {incident.actions.map((action: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center space-x-2 text-xs"
                  >
                    <div
                      className={cn(
                        "w-2 h-2 rounded-full",
                        action.type === "detect"
                          ? "bg-blue-500"
                          : action.type === "analyze"
                          ? "bg-purple-500"
                          : action.type === "remediate"
                          ? "bg-orange-500"
                          : action.type === "optimize"
                          ? "bg-green-500"
                          : "bg-gray-500"
                      )}
                    />
                    <span>{action.description}</span>
                    <span>•</span>
                    <span>{action.time}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-muted-foreground pt-2">
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1">
                  <CalendarDays className="h-3 w-3" />
                  <span>Started {formatTimeAgo(incident.start_time)}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>Updated {formatTimeAgo(incident.last_update)}</span>
                </span>
              </div>
              <div>
                Affected: {incident.affected_services.length} service
                {incident.affected_services.length !== 1 ? "s" : ""}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
