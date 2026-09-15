import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./src/tests/e2e",
  // ponytail: serial, not parallel — these tests hit one `next dev` server (which
  // compiles routes on demand) and one shared backend/DB, so parallel workers
  // contend with each other and flake with timeouts/500s instead of the app's own
  // behavior. Upgrade path: parallelize once tests run against a production build
  // and each worker gets its own DB.
  fullyParallel: false,
  workers: 1,
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
});
