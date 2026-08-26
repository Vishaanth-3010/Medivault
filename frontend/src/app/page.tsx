import Link from "next/link";

export default function HomePage() {
  return (
    <div className="rounded-2xl border bg-white p-10 shadow-sm">
      <h1 className="text-4xl font-bold text-teal-800">MediVault</h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Patient-controlled digital health records with secure upload, extraction, timeline, and consent-based doctor sharing.
      </p>
      <div className="mt-8 flex gap-4">
        <Link href="/login" className="rounded-lg bg-teal-700 px-5 py-2 text-white hover:bg-teal-800">
          Login
        </Link>
        <Link href="/register" className="rounded-lg border border-teal-700 px-5 py-2 text-teal-700 hover:bg-teal-50">
          Register
        </Link>
      </div>
      <p className="mt-8 text-sm text-slate-500">
        Prototype disclaimer: extraction is assistive only and not medical advice.
      </p>
    </div>
  );
}
