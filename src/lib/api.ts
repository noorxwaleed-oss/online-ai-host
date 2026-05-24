import { supabase } from './supabase';

const API_BASE_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
  'http://localhost:8000';

export interface GenerationInput {
  host_name: string;
  host_gender: string;
  guest_name: string;
  guest_gender: string;
  podcast_name: string;
  language: string;
  content: string;
  voice_id_host: string;
  voice_id_guest: string;
  host_style: string;
  guest_style: string;
  user_id: string;
}

export interface GenerationResult {
  message?: string;
  audio_url?: string;
  duration?: number;
  error?: string;
}

export interface ProjectDetail {
  user_id: string;
  project_id: string;
  metadata: Record<string, unknown> | null;
  script_url: string | null;
  audio_url: string | null;
  cover_url: string | null;
  feed_url: string | null;
}

async function authHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...(await authHeaders()),
    ...(init.headers as Record<string, string> | undefined),
  };
  const res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail: string;
    try {
      const body = await res.json();
      detail = body.detail || body.error || JSON.stringify(body);
    } catch {
      detail = res.statusText;
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return (await res.json()) as T;
}

/**
 * Fire the single backend generation endpoint. Long-running (minutes).
 * The backend's POST / takes the input fields as **query parameters**, not a JSON body.
 */
export async function generatePodcast(
  input: GenerationInput,
  signal?: AbortSignal,
): Promise<GenerationResult> {
  const params = new URLSearchParams(input as unknown as Record<string, string>);
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE_URL}/?${params.toString()}`, {
    method: 'POST',
    headers,
    signal,
  });
  if (!res.ok) {
    let detail: string;
    try {
      const body = await res.json();
      detail = body.detail || body.error || JSON.stringify(body);
    } catch {
      detail = res.statusText;
    }
    throw new Error(`Generation failed (${res.status}): ${detail}`);
  }
  return (await res.json()) as GenerationResult;
}

export function getLatestProject(userId: string): Promise<ProjectDetail> {
  return request<ProjectDetail>(`/api/projects/${encodeURIComponent(userId)}/latest`);
}

export function getProject(userId: string, projectId: string): Promise<ProjectDetail> {
  return request<ProjectDetail>(
    `/api/projects/${encodeURIComponent(userId)}/${encodeURIComponent(projectId)}`,
  );
}

export function listProjects(userId: string): Promise<{ user_id: string; project_ids: string[] }> {
  return request(`/api/projects/${encodeURIComponent(userId)}`);
}

export function getFeed(userId: string): Promise<{ user_id: string; feed_url: string | null }> {
  return request(`/api/feed/${encodeURIComponent(userId)}`);
}

/**
 * Fetch a Cloudinary-hosted JSON file (e.g. the script output) directly.
 * Cloudinary URLs are public, so no auth is needed.
 */
export async function fetchJsonUrl<T = unknown>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
  return (await res.json()) as T;
}

export interface VoicePreviewRequest {
  voice_id: string;
  language: 'english' | 'arabic';
  gender: 'male' | 'female';
  style: string;
  dialect?: string;
}

export interface VoicePreviewResult {
  audio_url: string;
  cached: boolean;
}

export function previewVoice(req: VoicePreviewRequest): Promise<VoicePreviewResult> {
  return request<VoicePreviewResult>('/api/voice-preview', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export interface UploadPdfResult {
  /** Server-local path the client must pass as `content` to POST /. */
  content: string;
  size: number;
  filename: string;
}

/**
 * Upload a PDF to the backend's temp store. The returned `content` string is
 * the server-local path; pass it straight through to generatePodcast() so the
 * backend's detect_input_type recognises it as a local PDF.
 */
export async function uploadPdf(file: File): Promise<UploadPdfResult> {
  const form = new FormData();
  form.append('file', file, file.name);
  const headers = await authHeaders(); // do NOT set Content-Type; browser will add the boundary
  const res = await fetch(`${API_BASE_URL}/api/upload-pdf`, {
    method: 'POST',
    headers,
    body: form,
  });
  if (!res.ok) {
    let detail: string;
    try {
      const body = await res.json();
      detail = body.detail || body.error || JSON.stringify(body);
    } catch {
      detail = res.statusText;
    }
    throw new Error(`PDF upload failed (${res.status}): ${detail}`);
  }
  return (await res.json()) as UploadPdfResult;
}
