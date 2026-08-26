"use client";

import { api, TimelineItem } from "@/lib/api";
import { useEffect, useState } from "react";

export default function TimelinePage() {
  const [items, setItems] = useState<TimelineItem[]>([]);

  useEffect(() => {
    api<{ items: TimelineItem[] }>("/records/timeline").then((r) => setItems(r.items)).catch(console.error);
  }, []);

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold">Medical Timeline</h1>
      <p className="mt-2 text-sm text-slate-600">Structured records extracted from your documents with provenance.</p>
      <div className="mt-6 space-y-3">
        {items.map((item) => (
          <div key={item.id} className="rounded border p-4">
            <div className="flex items-center justify-between">
              <span className="rounded bg-teal-100 px-2 py-0.5 text-xs uppercase text-teal-800">{item.type}</span>
              <span className="text-xs text-slate-500">{item.effective_time || "—"}</span>
            </div>
            <div className="mt-2 font-medium">{item.display_name}</div>
            {item.value && <div className="text-sm text-slate-600">{item.value}</div>}
          </div>
        ))}
        {items.length === 0 && <p className="text-slate-500">No timeline records yet. Upload a document first.</p>}
      </div>
    </div>
  );
}
