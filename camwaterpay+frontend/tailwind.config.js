/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { primary: { DEFAULT: "#2563EB" } },
      boxShadow: { soft: "0 10px 25px -10px rgba(37,99,235,.35)" }
    }
  },
  plugins: []
}
