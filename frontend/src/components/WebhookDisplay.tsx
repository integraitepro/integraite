// src/components/WebhookDisplay.tsx
import { useEffect, useState } from "react";

export default function WebhookDisplay() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(
          "http://localhost:8000/webhook/servicenow/latest"
        );
        if (res.ok) {
          const json = await res.json();
          setData(json);
          console.log("res data", res, json);
        }
      } catch (err) {
        console.log("Error fetching webhook:", err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>No data received yet</div>;

  return (
    <div>
      <h2>Latest ServiceNow Incident</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
