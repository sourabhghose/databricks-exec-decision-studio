/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#0f1f3d",
          800: "#162850",
          700: "#1e3a6e",
        },
        gold: {
          DEFAULT: "#c4962a",
          light: "#d4aa4a",
          dark: "#a67d1f",
        },
        alinta: {
          orange: "#F47920",
          "orange-light": "#FFF3E8",
          "orange-dark": "#C4611A",
          red: "#D4500A",
          amber: "#F5A623",
        },
        dark: {
          bg: "#0a0f1e",
          card: "#111827",
          border: "#1e2d4d",
        },
      },
      animation: {
        shimmer: "shimmer 3s ease-in-out infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "pulse-dot": "pulseDot 1.4s ease-in-out infinite",
      },
      keyframes: {
        shimmer: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(10px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        pulseDot: {
          "0%, 80%, 100%": { transform: "scale(0)", opacity: "0" },
          "40%": { transform: "scale(1)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
