import { defineConfig } from "@playwright/test";

const API = "http://127.0.0.1:8100";

export default defineConfig({
  testDir: "e2e",
  outputDir: "e2e/test-results",
  reporter: "list",
  use: { baseURL: "http://localhost:5174" },
  webServer: [
    {
      command:
        "node e2e/fresh-db.mjs && uv run -m uvicorn backend.main:app --port 8100",
      url: `${API}/api/health`,
      env: { UNDERCOVER_DB: "e2e/test.db", UNDERCOVER_API: API },
      reuseExistingServer: false,
    },
    {
      command: "npx vite dashboard --port 5174 --strictPort",
      url: "http://localhost:5174",
      env: { UNDERCOVER_API: API },
      reuseExistingServer: false,
    },
  ],
});
