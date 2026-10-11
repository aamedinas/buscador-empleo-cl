"use client";

import { useState } from "react";

import {
  ALL_PORTALS,
  CHILE_CITIES,
  DEFAULT_INDUSTRIES,
  DEFAULT_ROLES,
  PORTAL_LABELS,
  type JobSearchRequest,
  type Portal,
} from "@/services/types";

import { ChipMultiSelect } from "./ChipMultiSelect";

interface SearchFormProps {
  onSearch: (request: JobSearchRequest) => void;
  onExportCsv: (request: JobSearchRequest) => void;
  isLoading: boolean;
  isExporting: boolean;
}

const ANY_CITY = "";

export function SearchForm({ onSearch, onExportCsv, isLoading, isExporting }: SearchFormProps) {
  const [selectedRoles, setSelectedRoles] = useState<string[]>(DEFAULT_ROLES);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [selectedPortals, setSelectedPortals] = useState<Portal[]>(ALL_PORTALS);
  const [city, setCity] = useState<string>(ANY_CITY);
  const [limitPerPortal, setLimitPerPortal] = useState(20);

  function toggleRole(role: string) {
    setSelectedRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
    );
  }

  function toggleIndustry(industry: string) {
    setSelectedIndustries((prev) =>
      prev.includes(industry) ? prev.filter((i) => i !== industry) : [...prev, industry]
    );
  }

  function togglePortal(portal: Portal) {
    setSelectedPortals((prev) =>
      prev.includes(portal) ? prev.filter((p) => p !== portal) : [...prev, portal]
    );
  }

  function buildRequest(): JobSearchRequest {
    return {
      roles: selectedRoles,
      portals: selectedPortals.length > 0 ? selectedPortals : undefined,
      industries: selectedIndustries.length > 0 ? selectedIndustries : undefined,
      location: city || undefined,
      limit_per_portal: limitPerPortal,
    };
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (selectedRoles.length === 0) return;
    onSearch(buildRequest());
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <ChipMultiSelect
        label="Cargos a buscar"
        options={DEFAULT_ROLES}
        selected={selectedRoles}
        onToggle={toggleRole}
        allowCustom
        customPlaceholder="Agregar otro cargo..."
      />

      <ChipMultiSelect
        label="Rubro / industria (opcional)"
        options={DEFAULT_INDUSTRIES}
        selected={selectedIndustries}
        onToggle={toggleIndustry}
        allowCustom
        customPlaceholder="Agregar otro rubro..."
      />

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Portales
        </label>
        <div className="flex flex-wrap gap-2">
          {ALL_PORTALS.map((portal) => (
            <label
              key={portal}
              className={
                selectedPortals.includes(portal)
                  ? "flex items-center gap-1.5 rounded-full border border-brand-300 bg-brand-50 px-3 py-1.5 text-sm text-brand-700 dark:border-brand-800 dark:bg-brand-900/30 dark:text-brand-300"
                  : "flex items-center gap-1.5 rounded-full border border-slate-300 px-3 py-1.5 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400"
              }
            >
              <input
                type="checkbox"
                checked={selectedPortals.includes(portal)}
                onChange={() => togglePortal(portal)}
                className="accent-brand-600"
              />
              {PORTAL_LABELS[portal]}
            </label>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
            Ciudad
          </label>
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800"
          >
            <option value={ANY_CITY}>Todas las ciudades de Chile</option>
            {CHILE_CITIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">
            Resultados por portal: {limitPerPortal}
          </label>
          <input
            type="range"
            min={5}
            max={50}
            step={5}
            value={limitPerPortal}
            onChange={(e) => setLimitPerPortal(Number(e.target.value))}
            className="w-full accent-brand-600"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading || selectedRoles.length === 0}
          className="rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Buscando..." : "Buscar ofertas"}
        </button>
        <button
          type="button"
          disabled={isExporting || selectedRoles.length === 0}
          onClick={() => onExportCsv(buildRequest())}
          className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          {isExporting ? "Exportando..." : "Exportar CSV"}
        </button>
      </div>
    </form>
  );
}
