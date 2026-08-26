"use client";

import { uploadDocument, DocumentItem } from "@/lib/api";
import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<DocumentItem | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const doc = await uploadDocument(file);
      setResult(doc);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-xl rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold">Upload Medical Document</h1>
      <p className="mt-2 text-sm text-slate-600">Supported: PDF, JPEG, PNG. Max 25MB. Processing runs in background.</p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="rounded bg-teal-700 px-4 py-2 text-white disabled:opacity-50" type="submit">
          {loading ? "Uploading..." : "Upload & Process"}
        </button>
      </form>
      {result && (
        <div className="mt-6 rounded border bg-teal-50 p-4 text-sm">
          <p><strong>Uploaded:</strong> {result.filename}</p>
          <p><strong>Status:</strong> {result.processing_status}</p>
          <p className="mt-2 text-slate-600">Check Timeline in a few seconds after extraction completes.</p>
        </div>
      )}
    </div>
  );
}
