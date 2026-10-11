import { PORTAL_LABELS, type JobPosting } from "@/services/types";

import { SalaryBadge } from "./SalaryBadge";

export function JobCard({ job }: { job: JobPosting }) {
  return (
    <article className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">{job.title}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {job.company} &middot; {job.location}
          </p>
        </div>
        <span className="shrink-0 rounded-full bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-700 dark:bg-brand-900/30 dark:text-brand-300">
          {PORTAL_LABELS[job.portal]}
        </span>
      </div>

      <p className="whitespace-pre-line text-sm leading-relaxed text-slate-600 dark:text-slate-300">
        {job.summary}
      </p>

      <div className="mt-auto flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-3 dark:border-slate-800">
        <SalaryBadge salary={job.salary_range} />
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
        >
          Postular &rarr;
        </a>
      </div>
    </article>
  );
}
