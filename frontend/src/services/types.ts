export type Portal =
  | "trabajando.com"
  | "laborum"
  | "computrabajo"
  | "getonbrd"
  | "linkedin"
  | "indeed_cl";

export const PORTAL_LABELS: Record<Portal, string> = {
  "trabajando.com": "Trabajando.com",
  laborum: "Laborum",
  computrabajo: "Computrabajo",
  getonbrd: "GetOnBrd",
  linkedin: "LinkedIn",
  indeed_cl: "Indeed Chile",
};

export interface SalaryRange {
  min_clp: number | null;
  max_clp: number | null;
  is_estimated: boolean;
  source: "keyword_heuristic" | "published" | "historical_average";
}

export interface JobPosting {
  title: string;
  company: string;
  location: string;
  portal: Portal;
  url: string;
  published_at: string | null;
  summary: string;
  salary_range: SalaryRange;
  industry: string | null;
}

export interface PortalResult {
  portal: Portal;
  ok: boolean;
  count: number;
  error: string | null;
}

export interface JobSearchResponse {
  total: number;
  results: JobPosting[];
  portal_status: PortalResult[];
}

export interface JobSearchRequest {
  roles: string[];
  portals?: Portal[];
  industries?: string[];
  location?: string;
  limit_per_portal?: number;
}

export const DEFAULT_ROLES = [
  "Sub-gerente",
  "Lider de produccion",
  "Jefe de infraestructura",
  "Gerente",
];

export const DEFAULT_INDUSTRIES = [
  "Tecnologia",
  "TI",
  "Retail",
  "Salud",
  "Mineria",
  "Construccion",
  "Finanzas",
  "Industria",
  "Logistica",
  "Educacion",
];

// Ciudades/comunas mas comunes en los portales chilenos. El backend
// filtra por coincidencia de texto contra la ubicacion publicada por
// cada oferta, asi que esta lista es solo una ayuda de UI, no una
// taxonomia cerrada: "Todas las ciudades" no envia filtro de ubicacion.
export const CHILE_CITIES = [
  "Santiago",
  "Valparaiso",
  "Vina del Mar",
  "Concepcion",
  "La Serena",
  "Antofagasta",
  "Temuco",
  "Rancagua",
  "Talca",
  "Arica",
  "Iquique",
  "Puerto Montt",
  "Chillan",
  "Osorno",
  "Punta Arenas",
  "Coyhaique",
  "Copiapo",
  "Calama",
];

export const ALL_PORTALS: Portal[] = [
  "trabajando.com",
  "laborum",
  "computrabajo",
  "getonbrd",
  "linkedin",
  "indeed_cl",
];
