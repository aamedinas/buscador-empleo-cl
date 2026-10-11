"use client";

import { signIn, signOut, useSession } from "next-auth/react";

const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED !== "false";

export function AuthButton() {
  // useSession() se llama siempre, incluso en modo dev, para no violar
  // las reglas de hooks de React (no se puede llamar condicionalmente).
  const { data: session, status } = useSession();

  if (!AUTH_ENABLED) {
    return (
      <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
        Modo desarrollo (sin Keycloak)
      </span>
    );
  }

  if (status === "loading") {
    return <div className="h-9 w-24 animate-pulse rounded-full bg-slate-200 dark:bg-slate-800" />;
  }

  if (session?.user) {
    return (
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-600 dark:text-slate-300">
          {session.user.name ?? session.user.email}
        </span>
        <button
          onClick={() => signOut()}
          className="rounded-full border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          Cerrar sesion
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => signIn("keycloak")}
      className="rounded-full bg-brand-600 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-brand-700"
    >
      Iniciar sesion
    </button>
  );
}
