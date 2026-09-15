import type { Config } from "tailwindcss";

// The six values from BUILD_PROMPT §5. Used strictly — sodium is the single accent,
// signal is warnings only. Don't add colors here; if a screen needs a seventh value,
// that's a sign the design has drifted from the brief.
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12140F",
        pine: "#24503F",
        asphalt: "#6B7169",
        sodium: "#E8A33D",
        snow: "#FAFAF7",
        signal: "#C1462E",
      },
      fontFamily: {
        sans: ["var(--font-overpass)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-overpass-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
} satisfies Config;
