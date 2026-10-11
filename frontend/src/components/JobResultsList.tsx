import type { JobPosting } from "@/services/types";

import { JobCard } from "./JobCard";

function SkeletonCard() {
  return (
    <div className="h-48 animate-pulse rounded-xl border border-slate-200 bg-slate-100 dark:border-slate-800 dark:bg-slate-900" />
  );
}

export function JobResultsList({
  jobs,
  isLoading,
  hasSearched,
}: {
  jobs: JobPosting[];
  isLoading: boolean;
  hasSearched: boolean;
}) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (hasSearched && jobs.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">
        No se encontraron ofertas con estos filtros. Prueba ampliar los cargos o portales
        seleccionados.
      </div>
    );
  }

  if (!hasSearched) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">
        Configura tu busqueda arriba y presiona &ldquo;Buscar ofertas&rdquo;.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {jobs.map((job) => (
        <JobCard key={job.url} job={job} />
      ))}
    </div>
  );
}
