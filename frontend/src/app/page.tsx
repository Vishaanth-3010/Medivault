import Link from "next/link";

const features = [
  { title: "Private vault", body: "Original PDFs and images stay under patient control with hashed integrity checks." },
  { title: "Structured extraction", body: "Labs, vitals, meds, conditions, procedures, and allergies are pulled only when labeled in the document." },
  { title: "Consent grants", body: "Share scoped, time-bound access with a doctor. Revoke instantly — tokens cannot outlive the grant." },
  { title: "FHIR export", body: "Download a FHIR R4 collection bundle for interoperability without claiming ABDM certification." },
];

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="card overflow-hidden p-8 md:p-12">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">Patient-controlled health records</p>
        <h1 className="mt-3 max-w-3xl text-4xl font-bold tracking-tight text-slate-900 md:text-5xl">
          Your medical history, structured, auditable, and shared only when you say so.
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-600">
          Upload reports, extract a lifelong timeline, and grant doctors exactly the records they need — nothing more.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/login" className="btn-primary px-5 py-2.5">
            Login
          </Link>
          <Link href="/register" className="btn-secondary px-5 py-2.5">
            Create account
          </Link>
        </div>
        <p className="mt-6 text-sm text-slate-500">
          Demo: <code>patient@demo.medivault</code> / <code>doctor@demo.medivault</code> · password <code>password123</code>
        </p>
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        {features.map((feature) => (
          <article key={feature.title} className="card p-6">
            <h2 className="font-semibold text-teal-900">{feature.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{feature.body}</p>
          </article>
        ))}
      </section>
      <p className="text-xs text-slate-500">
        Prototype disclaimer: extraction is assistive only and is not medical advice, diagnosis, or a certified clinical system.
      </p>
    </div>
  );
}
