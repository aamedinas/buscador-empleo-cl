import type { JobSearchRequest, JobSearchResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

async function postJson<T>(path: string, body: unknown, accessToken?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(detail || `Error ${response.status} consultando ${path}`, response.status);
  }

  return (await response.json()) as T;
}

export function searchJobs(request: JobSearchRequest, accessToken?: string): Promise<JobSearchResponse> {
  return postJson<JobSearchResponse>("/jobs/search", request, accessToken);
}

export async function downloadJobsCsv(request: JobSearchRequest, accessToken?: string): Promise<Blob> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}/jobs/search/csv`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new ApiError(`Error ${response.status} exportando CSV`, response.status);
  }

  return await response.blob();
}
