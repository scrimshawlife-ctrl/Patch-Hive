# PatchHive developer and AI-agent task runner
# Install: https://github.com/casey/just
# Usage: just <recipe>

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

root := justfile_directory()

default:
	@just --list

# Install backend+frontend deps and build local AI indexes
setup:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}/backend"
	if command -v uv >/dev/null 2>&1; then
		uv venv --allow-existing .venv 2>/dev/null || uv venv .venv
		# shellcheck disable=SC1091
		source .venv/bin/activate
		uv pip install -e '.[dev]'
	else
		python3 -m pip install -e '.[dev]'
	fi
	cd "{{root}}/frontend"
	npm ci
	cd "{{root}}"
	just index
	@echo "setup complete"

lint:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}/backend"
	python -m ruff check canon evidence core patches/inventory_gate.py runs/bridge.py || python3 -m ruff check canon evidence
	python -m black --check canon evidence || true
	cd "{{root}}/frontend"
	npm run lint
	npm run type-check

test:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}/backend"
	env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance -q
	cd "{{root}}/frontend"
	npm test -- --run

coverage:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}/backend"
	env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance --cov -q

# Rebuild symbol/graph indexes under .codebase-memory/
index:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}"
	bash scripts/ai/rebuild_indexes.sh

memory: index
	@echo "codebase-memory indexes refreshed"

clean:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}"
	rm -rf .codebase-memory/indexes/* .codebase-memory/embeddings/* cache/* artifacts/* 2>/dev/null || true
	find . -type d -name __pycache__ -not -path './.git/*' -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/coverage backend/.coverage htmlcov frontend/test-results frontend/playwright-report 2>/dev/null || true
	@echo "clean complete (indexes may need just index)"

validate:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}"
	just lint
	just test
	@echo "validate ok"

build:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}/frontend"
	npm run build

docs:
	@echo "Engineering docs: docs/engineering/"
	@ls -1 "{{root}}/docs/engineering"
	@echo "AI: AI_CONTEXT.md SYSTEM_CONTEXT.md"

# Optional security-ish local scans (best-effort)
scan:
	#!/usr/bin/env bash
	set -euo pipefail
	cd "{{root}}"
	if command -v gitleaks >/dev/null; then gitleaks detect --source . --no-git -v || true; fi
	if command -v codespell >/dev/null; then codespell backend frontend docs README.md --skip="*.json,*.lock,node_modules,.git" || true; fi
