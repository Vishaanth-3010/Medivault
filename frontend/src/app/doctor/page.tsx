"use client";

import { api, TimelineItem } from "@/lib/api";
import { useEffect, useState } from "react";

type GrantedPatient = {
  patient_id: string;
  patient_name?: string | null;
  grant_id: string;
  expires_at: string;
};

export default function DoctorPortalPage() {
  const [patients, setPatients] = useState<GrantedPatient[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<GrantedPatient[]>("/doctor/patients").then(setPatients).catch((e) => setError(e.message));
  }, []);

  async function loadTimeline(patientId: string) {
    setSelected(patientId);
    setError("");
    try {
      const data = await api<{ items: TimelineItem[] }>(`/doctor/patients/${patientId}/timeline`);
      setTimeline(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Access denied");
      setTimeline([]);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Doctor Portal</h1>
        <p className="mt-2 text-sm text-slate-600">View only records explicitly shared by patients via active grants.</p>
      </div>

      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="font-semibold">Patients With Active Grants</h2>
        <div className="mt-4 space-y-2">
          {patients.map((p) => (
            <button key={p.grant_id} onClick={() => loadTimeline(p.patient_id)} className={`block w-full rounded border px-4 py-3 text-left ${selected === p.patient_id ? "border-teal-600 bg-teal-50" : ""}`}>
              <div className="font-medium">{p.patient_name || p.patient_id}</div>
              <div className="text-xs text-slate-500">Expires {new Date(p.expires_at).toLocaleString()}</div>
            </button>
          ))}
          {patients.length === 0 && <p className="text-slate-500">No active patient grants.</p>}
        </div>
      </section>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {timeline.length > 0 && (
        <section className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="font-semibold">Shared Timeline</h2>
          <div className="mt-4 space-y-3">
            {timeline.map((item) => (
              <div key={item.id} className="rounded border p-3 text-sm">
                <div className="font-medium">{item.display_name}</div>
                <div className="text-slate-500">{item.type} {item.value ? `· ${item.value}` : ""}</div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
