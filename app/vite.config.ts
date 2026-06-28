import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: mode === "telegram" ? "telegram.html" : mode === "demo" ? "demo.html" : "index.html",
    },
  },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
  server: {
    host: "0.0.0.0",
    allowedHosts: true
  },
}));
