"use client";

import { api, ConsentItem, DoctorOption } from "@/lib/api";
import { useEffect, useState } from "react";

export default function ConsentsPage() {
  const [doctors, setDoctors] = useState<DoctorOption[]>([]);
  const [consents, setConsents] = useState<ConsentItem[]>([]);
  const [doctorId, setDoctorId] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setConsents(await api<ConsentItem[]>("/consents"));
    setDoctors(await api<DoctorOption[]>("/audit/doctors"));
  }

  useEffect(() => {
    load().catch(console.error);
  }, []);

  async function createGrant() {
    if (!doctorId) return;
    setError("");
    const expires = new Date();
    expires.setDate(expires.getDate() + 7);
    try {
      await api("/consents", {
        method: "POST",
        body: JSON.stringify({
          doctor_id: doctorId,
          scope: { record_types: ["observations", "medications", "conditions", "procedures"], include_timeline: true },
          permissions: ["read"],
          expires_at: expires.toISOString(),
        }),
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create grant");
    }
  }

  async function revoke(id: string) {
    await api(`/consents/${id}/revoke`, { method: "PATCH" });
    await load();
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Consent Manager</h1>
        <p className="mt-2 text-sm text-slate-600">Grant scoped, time-bound access to doctors. Revoke anytime.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <select className="rounded border px-3 py-2" value={doctorId} onChange={(e) => setDoctorId(e.target.value)}>
            <option value="">Select doctor</option>
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>{d.name}{d.specialization ? ` · ${d.specialization}` : ""}</option>
            ))}
          </select>
          <button onClick={createGrant} className="rounded bg-teal-700 px-4 py-2 text-white">Create 7-day grant</button>
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </section>

      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="font-semibold">Your Share Grants</h2>
        <div className="mt-4 space-y-3">
          {consents.map((c) => (
            <div key={c.id} className="flex items-center justify-between rounded border p-4 text-sm">
              <div>
                <div className="font-medium">{c.doctor_name || c.doctor_id}</div>
                <div className="text-slate-500">Status: {c.status} · Expires: {new Date(c.expires_at).toLocaleString()}</div>
              </div>
              {c.status === "active" && (
                <button onClick={() => revoke(c.id)} className="rounded bg-red-100 px-3 py-1 text-red-700">Revoke</button>
              )}
            </div>
          ))}
          {consents.length === 0 && <p className="text-slate-500">No grants yet.</p>}
        </div>
      </section>
    </div>
  );
}
