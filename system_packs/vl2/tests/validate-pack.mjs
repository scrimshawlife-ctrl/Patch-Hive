#!/usr/bin/env node

import { readFileSync } from 'fs';
import { createHash } from 'crypto';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import Ajv from 'ajv';
import yaml from 'js-yaml';

const __dirname = dirname(fileURLToPath(import.meta.url));
const packRoot = resolve(__dirname, '..');

// Load manifest
const manifestPath = resolve(packRoot, 'pack.manifest.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));

// Load schema
const schemaPath = resolve(packRoot, manifest.schema.file);
const schema = JSON.parse(readFileSync(schemaPath, 'utf8'));

// Initialize AJV
const ajv = new Ajv({ allErrors: true, strict: false });
const validate = ajv.compile(schema);

console.log('🔍 PatchHive VL2 Pack Validation\n');
console.log(`Pack: ${manifest.name}`);
console.log(`Version: ${manifest.version}`);
console.log(`Schema: ${manifest.schemaVersion}`);
console.log(`Total patches: ${manifest.stats.totalPatches}\n`);

let passed = 0;
let failed = 0;

// Validate each patch
for (const patchEntry of manifest.patches) {
  const patchPath = resolve(packRoot, patchEntry.file);

  try {
    // Read patch file
    const patchContent = readFileSync(patchPath, 'utf8');
    const patch = yaml.load(patchContent);

    // Validate SHA-256
    const hash = createHash('sha256').update(patchContent).digest('hex');
    if (hash !== patchEntry.sha256) {
      console.log(`❌ ${patchEntry.id}: Hash mismatch`);
      console.log(`   Expected: ${patchEntry.sha256}`);
      console.log(`   Got:      ${hash}`);
      failed++;
      continue;
    }

    // Validate against schema
    const valid = validate(patch);
    if (!valid) {
      console.log(`❌ ${patchEntry.id}: Schema validation failed`);
      console.log(`   Errors:`, validate.errors);
      failed++;
      continue;
    }

    // Verify ID matches
    if (patch.id !== patchEntry.id) {
      console.log(`❌ ${patchEntry.id}: ID mismatch in patch file`);
      console.log(`   Expected: ${patchEntry.id}`);
      console.log(`   Got:      ${patch.id}`);
      failed++;
      continue;
    }

    // All checks passed
    console.log(`✅ ${patchEntry.id}: ${patchEntry.name}`);
    passed++;

  } catch (error) {
    console.log(`❌ ${patchEntry.id}: ${error.message}`);
    failed++;
  }
}

// Summary
console.log(`\n${'─'.repeat(50)}`);
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log(`${'─'.repeat(50)}\n`);

if (failed > 0) {
  console.log('❌ Validation failed\n');
  process.exit(1);
} else {
  console.log('✅ All patches validated successfully\n');
  process.exit(0);
}
