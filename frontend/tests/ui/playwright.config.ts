import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev -- --host 0.0.0.0 --port 5173',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    env: {
      VITE_API_BASE_URL: process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000/api',
    },
  },
});
