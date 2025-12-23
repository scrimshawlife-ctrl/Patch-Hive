import { test, expect } from '@playwright/test';
import { execSync } from 'node:child_process';

const API_BASE = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000/api';
const DATABASE_URL = process.env.PLAYWRIGHT_DATABASE_URL;

function seedGoldenDemo() {
  const command = DATABASE_URL
    ? `python scripts/seed_golden_demo.py --database-url "${DATABASE_URL}"`
    : 'python scripts/seed_golden_demo.py';
  const output = execSync(command, { cwd: process.cwd().replace(/frontend$/, ''), encoding: 'utf-8' });
  return JSON.parse(output.trim());
}

test.describe('PatchHive MVP UI', () => {
  const seed = seedGoldenDemo();

  test('tabs appear only when meaningful', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', seed.username);
    await page.fill('input[type="password"]', seed.password);
    await page.click('button:has-text("Login")');

    await page.goto(`/rigs/99999`);
    await expect(page.getByRole('button', { name: 'Overview' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Patches' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Exports' })).toHaveCount(0);

    await page.goto(`/rigs/${seed.rig_id}`);
    await expect(page.getByRole('button', { name: 'Overview' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Patches' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Exports' })).toBeVisible();
  });

  test('tooltips present', async ({ page }) => {
    await page.goto(`/rigs/${seed.rig_id}`);
    for (const copy of [
      'This category reflects the structural role of the patch: voice, modulation, rhythm, utility, or experimental.',
      'Difficulty is calculated from modulation depth, routing density, and feedback presence.',
      'This label appears when the patch structure shows unusual complexity or self-interaction.',
      'Each run is a preserved generation. Re-running never overwrites previous results.',
      'This name was generated automatically from the patch structure. You can rename it.',
      'Exports turn patches into printable artifacts. Viewing diagrams is always free.',
      'Credits are only used when exporting. Failed exports do not consume credits.',
      'Functions describe how a jack behaves. Unknown or proprietary functions are flagged for review.',
    ]) {
      await expect(page.getByText(copy)).toBeVisible();
    }
  });

  test('export gating visible', async ({ page, request }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', seed.username);
    await page.fill('input[type="password"]', seed.password);
    await page.click('button:has-text("Login")');

    await page.goto(`/rigs/${seed.rig_id}`);
    await page.click('button:has-text("Exports")');
    const exportButton = page.getByRole('button', { name: 'Export Patch Book' });
    await expect(exportButton).toBeDisabled();
    await expect(page.getByText('Insufficient credits')).toBeVisible();

    const adminLogin = await request.post(`${API_BASE}/community/auth/login`, {
      data: { username: 'admin_demo', password: 'admin-pass' },
    });
    const adminData = await adminLogin.json();
    const token = adminData.access_token;
    await request.post(`${API_BASE}/admin/users/${seed.user_id}/credits/grant`, {
      data: { credits: 10, reason: 'ui-test' },
      headers: { Authorization: `Bearer ${token}` },
    });

    await page.reload();
    await page.click('button:has-text("Exports")');
    await expect(exportButton).toBeEnabled();
  });
});
