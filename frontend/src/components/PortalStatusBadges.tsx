import { PORTAL_LABELS, type PortalResult } from "@/services/types";

export function PortalStatusBadges({ statuses }: { statuses: PortalResult[] }) {
  if (statuses.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {statuses.map((status) => (
        <span
          key={status.portal}
          title={status.error ?? undefined}
          className={
            status.ok
              ? "rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300"
              : "rounded-full border border-red-200 bg-red-50 px-3 py-1 text-xs font-medium text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-300"
          }
        >
          {PORTAL_LABELS[status.portal]}: {status.ok ? `${status.count} resultados` : "error"}
        </span>
      ))}
    </div>
  );
}
