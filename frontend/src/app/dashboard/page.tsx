"use client";

import { api, DocumentItem, getProfile, TimelineItem, UserProfile } from "@/lib/api";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [profile] = useState<UserProfile | null>(() => getProfile<UserProfile>());
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);

  useEffect(() => {
    api<DocumentItem[]>("/documents").then(setDocuments).catch(console.error);
    api<{ items: TimelineItem[] }>("/records/timeline").then((r) => setTimeline(r.items.slice(0, 5))).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Welcome, {profile?.name || "Patient"}</h1>
        <p className="mt-2 text-slate-600">Manage your health records, upload documents, and control doctor access.</p>
        <div className="mt-4 flex gap-3">
          <Link href="/upload" className="rounded bg-teal-700 px-4 py-2 text-white">Upload Document</Link>
          <Link href="/consents" className="rounded border px-4 py-2">Manage Consents</Link>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Recent Documents</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {documents.slice(0, 5).map((d) => (
              <li key={d.id} className="flex justify-between border-b py-2">
                <span>{d.filename}</span>
                <span className="text-slate-500">{d.processing_status}</span>
              </li>
            ))}
            {documents.length === 0 && <li className="text-slate-500">No documents yet.</li>}
          </ul>
        </section>
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Recent Timeline</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {timeline.map((t) => (
              <li key={t.id} className="border-b py-2">
                <div className="font-medium">{t.display_name}</div>
                <div className="text-slate-500">{t.type} {t.value ? `· ${t.value}` : ""}</div>
              </li>
            ))}
            {timeline.length === 0 && <li className="text-slate-500">No structured records yet.</li>}
          </ul>
        </section>
      </div>
    </div>
  );
}
