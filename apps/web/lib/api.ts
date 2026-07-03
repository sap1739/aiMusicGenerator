import type { Job, Track } from "@auralis/shared";
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";
async function request<T>(path: string, init?: RequestInit): Promise<T> { const response = await fetch(`${API_URL}${path}`, {...init, headers: init?.body instanceof FormData ? init.headers : {"Content-Type": "application/json", ...init?.headers}}); if (!response.ok) { const data = await response.json().catch(() => ({detail: "Something went quiet on the signal path."})); throw new Error(typeof data.detail === "string" ? data.detail : "Request failed"); } return response.status === 204 ? (undefined as T) : response.json(); }
export const api = {
  tracks: (q = "") => request<Track[]>(`/api/tracks${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  track: (id: string) => request<Track & {versions: Track[]}>(`/api/tracks/${id}`),
  generate: (payload: object) => request<Job>("/api/generate", {method: "POST", body: JSON.stringify(payload)}),
  job: (id: string) => request<Job>(`/api/jobs/${id}`),
  updateTrack: (id: string, payload: object) => request<Track>(`/api/tracks/${id}`, {method: "PATCH", body: JSON.stringify(payload)}),
  deleteTrack: (id: string) => request<void>(`/api/tracks/${id}`, {method: "DELETE"}),
  upload: (body: FormData) => request<Track>("/api/upload", {method: "POST", body}),
  transform: (kind: string, payload: object) => request<Job>(`/api/${kind}`, {method: "POST", body: JSON.stringify(payload)}),
  audio: (id: string) => `${API_URL}/api/audio/${id}`,
  download: (id: string) => `${API_URL}/api/audio/${id}?download=true`,
};
