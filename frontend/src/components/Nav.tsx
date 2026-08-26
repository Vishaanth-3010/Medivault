"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getProfile, UserProfile } from "@/lib/api";
import { useEffect, useState } from "react";

const patientLinks = [
  ["Dashboard", "/dashboard"],
  ["Upload", "/upload"],
  ["Timeline", "/timeline"],
  ["Consents", "/consents"],
  ["Audit Logs", "/audit"],
];

const doctorLinks = [["Portal", "/doctor"]];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    setProfile(getProfile<UserProfile>());
  }, [pathname]);

  if (pathname === "/" || pathname.startsWith("/login") || pathname.startsWith("/register")) return null;

  const links = profile?.role === "doctor" ? doctorLinks : patientLinks;

  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href={profile?.role === "doctor" ? "/doctor" : "/dashboard"} className="text-lg font-semibold text-teal-700">
          MediVault
        </Link>
        <nav className="flex gap-4 text-sm">
          {links.map(([label, href]) => (
            <Link key={href} href={href} className={pathname === href ? "font-semibold text-teal-700" : "text-slate-600 hover:text-teal-700"}>
              {label}
            </Link>
          ))}
        </nav>
        <button
          className="rounded bg-slate-100 px-3 py-1 text-sm"
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
        >
          Logout
        </button>
      </div>
    </header>
  );
}
