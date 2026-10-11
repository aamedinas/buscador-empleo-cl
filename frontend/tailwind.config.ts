import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "media",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f5ff",
          100: "#dde9ff",
          200: "#b9d1ff",
          300: "#8fb3ff",
          400: "#5e8dff",
          500: "#3366ff",
          600: "#254edb",
          700: "#1b3cb3",
          800: "#162f8c",
          900: "#132870",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
