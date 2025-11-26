# GitHub Actions Workflows

This directory contains CI/CD workflows for PatchHive.

## Workflows

### 🧪 Backend Tests (`backend-tests.yml`)

Runs comprehensive backend test suite on every push and PR.

**Triggers:**
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Only when backend files change

**Jobs:**
- **Test Matrix**: Python 3.11 and 3.12
- **Database**: PostgreSQL 15 service container
- **Test Suites**:
  - Unit tests (34 model + 33 patch engine)
  - API tests (21 endpoint tests)
- **Coverage**: Uploads to Codecov
- **Artifacts**: Test results and coverage reports

**Status Badge:**
```markdown
![Backend Tests](https://github.com/scrimshawlife-ctrl/Patch-Hive/workflows/Backend%20Tests/badge.svg)
```

### 🔍 Code Quality (`code-quality.yml`)

Checks code formatting, linting, and type safety.

**Backend Checks:**
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)

**Frontend Checks:**
- ESLint (linting)
- TypeScript type checking

**Status Badge:**
```markdown
![Code Quality](https://github.com/scrimshawlife-ctrl/Patch-Hive/workflows/Code%20Quality/badge.svg)
```

## Local Testing

Before pushing, run these commands to catch issues locally:

### Backend

```bash
cd backend

# Run tests
python3 -m pytest tests/ -v

# Format code
black .
isort .

# Lint
flake8 .
```

### Frontend

```bash
cd frontend

# Run tests
npm test

# Lint
npm run lint

# Type check
npm run type-check

# Format
npm run format
```

## Coverage Reports

Coverage reports are automatically uploaded to [Codecov](https://codecov.io/gh/scrimshawlife-ctrl/Patch-Hive) on every CI run.

Local coverage:
```bash
cd backend
python3 -m pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Secrets Required

The following GitHub secrets should be configured:

- `CODECOV_TOKEN` - Codecov upload token (optional but recommended)

## Workflow Triggers

| Event | backend-tests.yml | code-quality.yml |
|-------|------------------|------------------|
| Push to main | ✅ | ✅ |
| Push to develop | ✅ | ✅ |
| Push to claude/** | ✅ | ✅ |
| Pull Request | ✅ | ✅ |
| Manual dispatch | ❌ | ❌ |

## Performance

- **Backend Tests**: ~2-4 minutes
- **Code Quality**: ~1-2 minutes
- **Total**: ~3-6 minutes for full CI pipeline

## Debugging Failed Workflows

1. **Check the Actions tab** on GitHub
2. **Expand failed step** to see error details
3. **Download artifacts** for detailed logs
4. **Run locally** with same Python/Node version
5. **Check for flaky tests** if intermittent failures

## Future Enhancements

- [ ] Frontend component tests (Jest + React Testing Library)
- [ ] Integration tests (E2E with Playwright)
- [ ] Security scanning (Snyk, Dependabot)
- [ ] Performance testing (load tests)
- [ ] Deployment workflows (staging, production)
- [ ] Docker image building and pushing
- [ ] Release automation
