# Coding standards

## Python (backend)

- Target **3.11+** (`requires-python >=3.11`); CI uses 3.11 and 3.12
- Formatter: **Black** (line length 100)
- Linter: **Ruff**
- Types: **mypy** on canonical packages (expand gradually)
- Style: frozen Pydantic contracts in `canon`; fail closed on missing truth
- Never invent module identity, voltages, or cable endpoints

## TypeScript (frontend)

- Strict TypeScript via `tsc --noEmit`
- ESLint with `--max-warnings 0`
- Prefer server-authored IDs/hashes for exports (no client invention)
- UI: loading / empty / error / retry parity on list surfaces
- Accessibility: status text not color-only

## Domain language

- Port/cable `audio` = signal class (allowed)
- Audio **processing** / DSP / hardware control = forbidden product scope

## Commits

- Conventional prefixes: `feat:`, `fix:`, `docs:`, `test:`, `chore:`
- No secrets in tree; `.env` gitignored

## Dual-path rule

Do not big-bang delete `racks`/`patches` routers while MVP UI depends on them. Prefer thin vertical slices (see `docs/CANON_ALIGNMENT.md`).
