import { defineConfig } from "@playwright/test";

// The browser tests run their own backend and dashboard on their own ports,
// against a database seeded fresh for each run, so they never touch yours.
const backendPort = 8001;
const dashboardPort = 5174;
export const backendUrl = `http://127.0.0.1:${String(backendPort)}`;
const dashboardUrl = `http://127.0.0.1:${String(dashboardPort)}`;

export default defineConfig({
  testDir: "e2e",
  outputDir: "e2e/test-results",
  reporter: "list",
  use: { baseURL: dashboardUrl },
  webServer: [
    {
      command: `uv run -m backend.seed && uv run -m uvicorn backend.main:app --port ${String(backendPort)}`,
      url: `${backendUrl}/api/health`,
      env: { DATABASE_PATH: "e2e/test.db" },
      reuseExistingServer: false,
    },
    {
      command: `npx vite dashboard --host 127.0.0.1 --port ${String(dashboardPort)} --strictPort`,
      url: dashboardUrl,
      env: { BACKEND_URL: backendUrl },
      reuseExistingServer: false,
    },
  ],
});
