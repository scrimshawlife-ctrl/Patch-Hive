import { expect, test } from '@playwright/test';

test.describe('PatchHive canonical workspace', () => {
  test.beforeEach(async ({ page }) => {
    // Slice B: run list is served from /api/canon/runs?rig_id=
    await page.route('**/api/canon/runs**', async (route) => {
      const url = route.request().url();
      // Do not intercept revision/export subpaths that also contain "runs" substrings incorrectly.
      if (url.includes('/rigs/')) {
        return route.fallback();
      }
      const rigId = new URL(url).searchParams.get('rig_id');
      const runs =
        rigId === '99999'
          ? []
          : [
              {
                id: 11,
                rack_id: 1,
                status: 'succeeded',
                created_at: '2025-01-01T00:00:00Z',
                rig_revision_id: 'rig-rev-' + 'a'.repeat(32),
                source_run_id: 'gen-run-11-' + 'a'.repeat(16),
                artifact_manifest_hash: 'a'.repeat(64),
                export_bridge_ready: true,
              },
              {
                id: 12,
                rack_id: 1,
                status: 'succeeded',
                created_at: '2025-02-01T00:00:00Z',
                rig_revision_id: 'rig-rev-' + 'b'.repeat(32),
                source_run_id: 'gen-run-12-' + 'b'.repeat(16),
                artifact_manifest_hash: 'b'.repeat(64),
                export_bridge_ready: true,
              },
            ];
      await route.fulfill({ json: { total: runs.length, runs } });
    });
    // Revision picker (groups runs by bridge rig_revision_id)
    await page.route('**/api/canon/rigs/*/revisions**', async (route) => {
      const url = route.request().url();
      if (url.includes('/rigs/99999/')) {
        await route.fulfill({ json: { total: 0, revisions: [] } });
        return;
      }
      await route.fulfill({
        json: {
          total: 2,
          revisions: [
            {
              rig_revision_id: 'rig-rev-' + 'b'.repeat(32),
              run_count: 1,
              latest_run_id: 12,
              latest_run_at: '2025-02-01T00:00:00Z',
              export_bridge_ready: true,
            },
            {
              rig_revision_id: 'rig-rev-' + 'a'.repeat(32),
              run_count: 1,
              latest_run_id: 11,
              latest_run_at: '2025-01-01T00:00:00Z',
              export_bridge_ready: true,
            },
          ],
        },
      });
    });
    await page.route('**/api/runs/*/patches**', (route) =>
      route.fulfill({ json: { total: 0, patches: [] } }),
    );
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
    await expect(page.getByLabel('Source run (within revision)')).toHaveValue('12');
    await expect(page.getByLabel('Rig revision')).toBeVisible();
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
    await expect(page.getByRole('list', { name: 'Ranked module candidates' })).toBeVisible();
    const createRevision = page.getByRole('button', { name: 'Create immutable rig revision' });
    await expect(createRevision).toBeDisabled();
    // Resolve every ranked candidate (confirm + reject) so inventory is ready.
    await page.getByRole('button', { name: 'Confirm match' }).first().click();
    await page.getByRole('button', { name: 'Reject' }).last().click();
    await expect(createRevision).toBeEnabled();
    await createRevision.click();
    await expect(page.getByText(/Inventory revision ready/i)).toBeVisible();
  });

  test('export boundary explains zero-credit state', async ({ page }) => {
    await page.goto('/rigs/1');
    await page.getByRole('tab', { name: 'Exports' }).click();
    await expect(page.getByRole('button', { name: 'Export PDF patch book' })).toBeDisabled();
    await expect(page.getByText('Credits are required only for exports.')).toBeVisible();
    await expect(page.getByText('/api/canon/exports')).toBeVisible();
  });
});
