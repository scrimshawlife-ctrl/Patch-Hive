# Audio drift classification

**Baseline SHA:** `2b72d5b10fef1ab70c74d3c40379eb1593cf8293`  
**Audit branch:** `grok/patchhive-visual-system-canon-audit`  
**Date:** 2026-07-21

## Policy

PatchHive **must not** depend on audio processing. Legitimate synthesizer **signal
domain** vocabulary (port type `audio`, cable type `audio`, control `waveform: sine`)
is preserved.

| Classification | Meaning |
|----------------|---------|
| ACTIVE_PRODUCT_REQUIREMENT | Must remain for product correctness |
| LEGITIMATE_DOMAIN_LANGUAGE | Signal/metadata vocabulary — keep |
| HISTORICAL_PROVENANCE | Past product surface; do not treat as ship authority |
| TEST_FIXTURE | Tests/fixtures only |
| STALE_DOCUMENTATION | Docs claim out-of-scope capability — fix |
| DEAD_CODE | Unreachable or unused |
| OUT_OF_SCOPE_IMPLEMENTATION | Code path that would implement audio processing |
| FALSE_POSITIVE | Match is not product-scope audio |

## Representative findings

| Location | Match | Classification | Action |
|----------|-------|----------------|--------|
| `patchhive/schemas.py` SignalKind.audio | port domain | LEGITIMATE_DOMAIN_LANGUAGE | Keep |
| VL2 patch YAML `type: audio` / `waveform: sine` | patch settings | LEGITIMATE_DOMAIN_LANGUAGE | Keep |
| `backend/export/waveform.py` | SVG approximation | LEGITIMATE_DOMAIN_LANGUAGE (symbolic viz) | Keep; docs clarify non-audio |
| `docs/PATCH_ENGINE.md` Phase 3 "Audio simulation" | future DSP | STALE_DOCUMENTATION | **Removed** this campaign |
| `docs/PATCH_ENGINE.md` "Hardware integration" | CV activation | STALE_DOCUMENTATION | **Marked OUT OF SCOPE** |
| README / CURRENT_STATE no-audio identity | product boundary | ACTIVE_PRODUCT_REQUIREMENT | Keep |
| `docs/DISCORD_SETUP.md` audio quality kbps | Discord voice | HISTORICAL_PROVENANCE | Keep; not product runtime |
| `docs/COMPONENTS.md` WaveformDisplay animated | UI wishlist | HISTORICAL_PROVENANCE | Do not implement as audio player |
| Brand SVGs "waveform" glyphs | visual brand | FALSE_POSITIVE | Keep |
| `docs/DEPLOYMENT_OPTIONS.md` "low latency" | CDN edge | FALSE_POSITIVE | Keep |
| Home.tsx "waveform approximations" | marketing copy | LEGITIMATE_DOMAIN_LANGUAGE | Optional later reword to "symbolic" |

## Forbidden concepts (must remain absent as product requirements)

- audio recording / microphone input
- waveform / spectral analysis of sound
- audio fingerprinting
- audio playback / sound synthesis / DSP
- realtime audio graphs / plugin hosting / DAW integration
- MIDI or CV **hardware activation**
- automatic control of physical equipment

## Conclusion

No active audio-processing subsystem was found. Stale documentation promising
audio simulation / hardware control as future work was corrected. Domain uses
of `audio` and `waveform` remain intentional.
