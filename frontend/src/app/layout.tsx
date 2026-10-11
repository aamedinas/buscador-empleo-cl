import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Providers } from "@/components/Providers";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Buscador de Empleo Chile",
  description: "Busqueda ejecutiva de ofertas laborales en portales chilenos.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
