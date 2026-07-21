/** SHA-256 hex digest for browser and test environments. */
export async function sha256Hex(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

/** Build a deterministic 64-char manifest hash for legacy run → canon export bridge. */
export async function legacyRunManifestHash(runId: number | string, rigId: number | string): Promise<string> {
  return sha256Hex(`patchhive:legacy-run:${runId}:rig:${rigId}`);
}
