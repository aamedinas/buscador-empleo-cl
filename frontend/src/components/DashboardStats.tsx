import type { JobPosting } from "@/services/types";

interface Bucket {
  label: string;
  count: number;
}

const clpFormatter = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 0 });

function countBy(jobs: JobPosting[], keyFn: (job: JobPosting) => string): Bucket[] {
  const counts = new Map<string, number>();
  for (const job of jobs) {
    const key = keyFn(job);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return Array.from(counts.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
}

function regionOf(job: JobPosting): string {
  const parts = job.location.split(",");
  const last = parts[parts.length - 1]?.trim();
  return last || "Sin especificar";
}

const SALARY_BANDS: Array<{ label: string; test: (min: number | null) => boolean }> = [
  { label: "Sin informacion", test: (min) => min === null },
  { label: "< $1.000.000", test: (min) => min !== null && min < 1_000_000 },
  { label: "$1.000.000 - $2.000.000", test: (min) => min !== null && min >= 1_000_000 && min < 2_000_000 },
  { label: "$2.000.000 - $3.000.000", test: (min) => min !== null && min >= 2_000_000 && min < 3_000_000 },
  { label: "$3.000.000 - $5.000.000", test: (min) => min !== null && min >= 3_000_000 && min < 5_000_000 },
  { label: "> $5.000.000", test: (min) => min !== null && min >= 5_000_000 },
];

function salaryBandBuckets(jobs: JobPosting[]): Bucket[] {
  return SALARY_BANDS.map(({ label, test }) => ({
    label,
    count: jobs.filter((job) => test(job.salary_range.min_clp)).length,
  })).filter((bucket) => bucket.count > 0);
}

function BarRow({ label, count, maxCount }: { label: string; count: number; maxCount: number }) {
  const widthPct = maxCount > 0 ? Math.max((count / maxCount) * 100, 4) : 4;
  return (
    <div className="flex items-center gap-3">
      <span
        className="w-36 shrink-0 truncate text-sm text-slate-600 dark:text-slate-300"
        title={label}
      >
        {label}
      </span>
      <div className="h-5 flex-1 rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className="h-5 rounded-full bg-brand-500"
          style={{ width: `${widthPct}%` }}
        />
      </div>
      <span className="w-8 shrink-0 text-right text-sm font-medium text-slate-700 dark:text-slate-200">
        {count}
      </span>
    </div>
  );
}

function BarChartPanel({ title, buckets }: { title: string; buckets: Bucket[] }) {
  const maxCount = Math.max(...buckets.map((b) => b.count), 1);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-200">{title}</h3>
      {buckets.length === 0 ? (
        <p className="text-sm text-slate-400">Sin datos.</p>
      ) : (
        <div className="flex flex-col gap-2.5">
          {buckets.map((bucket) => (
            <BarRow key={bucket.label} label={bucket.label} count={bucket.count} maxCount={maxCount} />
          ))}
        </div>
      )}
    </div>
  );
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-slate-100">{value}</p>
    </div>
  );
}

export function DashboardStats({ jobs }: { jobs: JobPosting[] }) {
  if (jobs.length === 0) return null;

  const byIndustry = countBy(jobs, (job) => job.industry ?? "Sin rubro especificado");
  const byRegion = countBy(jobs, regionOf);
  const bySalaryBand = salaryBandBuckets(jobs);

  const uniqueCompanies = new Set(jobs.map((j) => j.company)).size;
  const knownSalaries = jobs
    .map((j) => j.salary_range.min_clp)
    .filter((v): v is number => v !== null);
  const avgSalary =
    knownSalaries.length > 0
      ? Math.round(knownSalaries.reduce((a, b) => a + b, 0) / knownSalaries.length)
      : null;

  return (
    <div className="mb-6 flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatTile label="Ofertas encontradas" value={String(jobs.length)} />
        <StatTile label="Empresas distintas" value={String(uniqueCompanies)} />
        <StatTile label="Rubros distintos" value={String(byIndustry.length)} />
        <StatTile
          label="Salario minimo promedio"
          value={avgSalary ? `$${clpFormatter.format(avgSalary)}` : "Sin datos"}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <BarChartPanel title="Ofertas por rubro" buckets={byIndustry} />
        <BarChartPanel title="Ofertas por region" buckets={byRegion} />
        <BarChartPanel title="Ofertas por rango salarial" buckets={bySalaryBand} />
      </div>
    </div>
  );
}
