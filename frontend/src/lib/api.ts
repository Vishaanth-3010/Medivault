const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

export type ApiError = { error: { code: string; message: string; request_id?: string } };

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("medivault_token");
}

export function setToken(token: string) {
  localStorage.setItem("medivault_token", token);
}

export function clearToken() {
  localStorage.removeItem("medivault_token");
  localStorage.removeItem("medivault_profile");
}

export function getProfile<T>(): T | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("medivault_profile");
  return raw ? JSON.parse(raw) as T : null;
}

export function setProfile(profile: unknown) {
  localStorage.setItem("medivault_profile", JSON.stringify(profile));
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({ error: { code: "UNKNOWN", message: res.statusText } }))) as ApiError;
    throw new Error(err.error?.message || "Request failed");
  }
  return res.json() as Promise<T>;
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  return api<DocumentItem>("/documents/upload", { method: "POST", body: form });
}

export type UserProfile = {
  user_id: string;
  email: string;
  role: "patient" | "doctor";
  patient_id?: string;
  doctor_id?: string;
  name?: string;
};

export type DocumentItem = {
  id: string;
  filename: string;
  mime_type: string;
  file_size: number;
  processing_status: string;
  document_date?: string | null;
  uploaded_at: string;
};

export type TimelineItem = {
  type: string;
  id: string;
  display_name: string;
  value?: string | null;
  effective_time?: string | null;
  document_id?: string | null;
};

export type ConsentItem = {
  id: string;
  patient_id: string;
  doctor_id: string;
  doctor_name?: string | null;
  scope: Record<string, unknown>;
  permissions: string[];
  issued_at: string;
  expires_at: string;
  revoked_at?: string | null;
  status: string;
};

export type AuditItem = {
  id: string;
  action: string;
  outcome: string;
  timestamp: string;
  actor_role: string;
  resource_type?: string | null;
};

export type DoctorOption = { id: string; name: string; specialization?: string | null };
