import { expect, test } from '@playwright/test';

test.describe('PatchHive canonical workspace', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/runs**', async (route) => {
      const rackId = new URL(route.request().url()).searchParams.get('rack_id');
      const runs =
        rackId === '99999'
          ? []
          : [
              { id: 11, rack_id: 1, status: 'succeeded', created_at: '2025-01-01T00:00:00Z' },
              { id: 12, rack_id: 1, status: 'succeeded', created_at: '2025-02-01T00:00:00Z' },
            ];
      await route.fulfill({ json: { total: runs.length, runs } });
    });
    // P1: credits read the canonical ledger, not legacy monetization.
    await page.route('**/api/canon/credits/balance', (route) =>
      route.fulfill({ json: { balance: 0 } }),
    );
    await page.route('**/api/monetization/credits/balance', (route) =>
      route.fulfill({ status: 410, json: { detail: 'use /api/canon/credits/balance' } }),
    );
  });

  test('shows only contextual tabs and defaults to the latest run', async ({ page }) => {
    await page.goto('/rigs/99999');
    await expect(page.getByRole('tab', { name: 'Overview' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Module gallery' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Patches' })).toHaveCount(0);
    await expect(page.getByRole('tab', { name: 'Exports' })).toHaveCount(0);

    await page.goto('/rigs/1');
    await expect(page.getByRole('tab', { name: 'Patches' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Exports' })).toBeVisible();
    await expect(page.getByLabel('Source run')).toHaveValue('12');
  });

  test('keeps historical social features out of active navigation', async ({ page }) => {
    await page.goto('/');
    const navigation = page.getByRole('navigation', { name: 'Primary navigation' });
    await expect(navigation.getByRole('link', { name: 'Rigs' })).toBeVisible();
    await expect(navigation.getByText('Feed')).toHaveCount(0);
    await expect(navigation.getByText('Publish')).toHaveCount(0);
    await expect(navigation.getByText('Leaderboards')).toHaveCount(0);
  });

  test('photo evidence is keyboard reachable and requires explicit resolution', async ({ page }) => {
    await page.goto('/racks/new');
    await page.getByRole('button', { name: 'Rig photo' }).setInputFiles({
      name: 'rig.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.from([0xff, 0xd8, 0xff, 0xd9]),
    });
    await page.getByRole('button', { name: 'Detect modules' }).click();
    const createRevision = page.getByRole('button', { name: 'Create immutable rig revision' });
    await expect(createRevision).toBeDisabled();
    await page.getByRole('button', { name: 'Confirm match' }).click();
    await expect(createRevision).toBeEnabled();
  });

  test('export boundary explains zero-credit state', async ({ page }) => {
    await page.goto('/rigs/1');
    await page.getByRole('tab', { name: 'Exports' }).click();
    await expect(page.getByRole('button', { name: 'Export PDF patch book' })).toBeDisabled();
    await expect(page.getByText('Credits are required only for exports.')).toBeVisible();
    await expect(page.getByText('/api/canon/exports')).toBeVisible();
  });
});
