import type { SalaryRange } from "@/services/types";

const clpFormatter = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 0 });

function formatClp(value: number): string {
  return `$${clpFormatter.format(value)}`;
}

export function SalaryBadge({ salary }: { salary: SalaryRange }) {
  if (salary.min_clp === null) {
    return <span className="text-sm text-slate-400">Sin informacion de renta</span>;
  }

  const range =
    salary.max_clp && salary.max_clp !== salary.min_clp
      ? `${formatClp(salary.min_clp)} - ${formatClp(salary.max_clp)}`
      : formatClp(salary.min_clp);

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">{range}</span>
      <span
        className={
          salary.is_estimated
            ? "rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
            : "rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-medium text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
        }
      >
        {salary.is_estimated ? "Estimado" : "Publicado"}
      </span>
    </div>
  );
}
