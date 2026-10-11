"use client";

import { useSession } from "next-auth/react";
import { useState } from "react";

import { AuthButton } from "@/components/AuthButton";
import { DashboardStats } from "@/components/DashboardStats";
import { JobResultsList } from "@/components/JobResultsList";
import { PortalStatusBadges } from "@/components/PortalStatusBadges";
import { SearchForm } from "@/components/SearchForm";
import { ApiError, downloadJobsCsv, searchJobs } from "@/services/api";
import type { JobPosting, JobSearchRequest, PortalResult } from "@/services/types";

const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED !== "false";

export default function HomePage() {
  const { data: session } = useSession();
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [portalStatus, setPortalStatus] = useState<PortalResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const accessToken = AUTH_ENABLED ? session?.accessToken : undefined;

  async function handleSearch(request: JobSearchRequest) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await searchJobs(request, accessToken);
      setJobs(response.results);
      setPortalStatus(response.portal_status);
      setHasSearched(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo conectar con la API.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleExportCsv(request: JobSearchRequest) {
    setIsExporting(true);
    setError(null);
    try {
      const blob = await downloadJobsCsv(request, accessToken);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ofertas_empleo.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo exportar el CSV.");
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Buscador de Empleo Chile
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Resumen ejecutivo, rango salarial y postulacion directa en un solo lugar.
          </p>
        </div>
        <AuthButton />
      </header>

      <section className="mb-6">
        <SearchForm
          onSearch={handleSearch}
          onExportCsv={handleExportCsv}
          isLoading={isLoading}
          isExporting={isExporting}
        />
      </section>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-300">
          {error}
        </div>
      )}

      {hasSearched && !isLoading && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-medium text-slate-500 dark:text-slate-400">
            Estado por portal
          </h2>
          <PortalStatusBadges statuses={portalStatus} />
        </section>
      )}

      {hasSearched && !isLoading && <DashboardStats jobs={jobs} />}

      <section>
        <JobResultsList jobs={jobs} isLoading={isLoading} hasSearched={hasSearched} />
      </section>
    </main>
  );
}
