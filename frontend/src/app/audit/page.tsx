"use client";

import { api, AuditItem } from "@/lib/api";
import { useEffect, useState } from "react";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditItem[]>([]);

  useEffect(() => {
    api<AuditItem[]>("/audit/logs").then(setLogs).catch(console.error);
  }, []);

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold">Access Logs</h1>
      <p className="mt-2 text-sm text-slate-600">Audit trail of sensitive actions on your records.</p>
      <table className="mt-6 w-full text-left text-sm">
        <thead>
          <tr className="border-b text-slate-500">
            <th className="py-2">Time</th>
            <th>Action</th>
            <th>Outcome</th>
            <th>Resource</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-b">
              <td className="py-2">{new Date(log.timestamp).toLocaleString()}</td>
              <td>{log.action}</td>
              <td>{log.outcome}</td>
              <td>{log.resource_type || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {logs.length === 0 && <p className="mt-4 text-slate-500">No audit events yet.</p>}
    </div>
  );
}
