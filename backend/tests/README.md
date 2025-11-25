# PatchHive Backend Tests

Comprehensive test suite for the PatchHive backend, focusing on deterministic patch generation and ABX-Core v1.2 compliance.

## Test Structure

```
tests/
├── conftest.py           # Pytest fixtures and test database setup
├── unit/
│   └── test_patch_engine.py  # Patch generation engine tests (33 tests)
└── integration/          # Integration tests (TODO)
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov

# Install backend dependencies
pip install -r requirements.txt  # or use pyproject.toml
```

### Run All Tests

```bash
cd backend
python3 -m pytest tests/ -v
```

### Run Specific Test Suite

```bash
# Run only patch engine tests
python3 -m pytest tests/unit/test_patch_engine.py -v

# Run only determinism tests
python3 -m pytest tests/unit/test_patch_engine.py::TestDeterminism -v

# Run specific test
python3 -m pytest tests/unit/test_patch_engine.py::TestDeterminism::test_same_seed_produces_same_patches -v
```

### Generate Coverage Report

```bash
python3 -m pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Categories

### 1. **Module Analyzer Tests** (6 tests)
Tests the `ModuleAnalyzer` class which categorizes modules by type (VCO, VCF, VCA, etc.).

- `test_analyzer_empty_rack` - Empty rack handling
- `test_analyzer_basic_rack` - Basic VCO/VCF/VCA detection
- `test_analyzer_full_rack` - Multi-module type detection
- `test_analyzer_categorization_*` - Module type categorization

### 2. **Patch Generator Tests** (10 tests)
Tests the `PatchGenerator` class which creates patches based on available modules.

- `test_generator_basic_config` - Configuration handling
- `test_can_generate_*` - Capability detection for different patch types
- `test_generate_*` - Patch generation for various types
- `test_patch_has_valid_structure` - Output validation
- `test_connection_has_valid_structure` - Connection validation

### 3. **Determinism Tests** (4 tests)
**Critical tests** for ABX-Core v1.2 compliance - verifies deterministic generation.

- `test_same_seed_produces_same_patches` - Same seed → identical patches
- `test_different_seeds_produce_different_patches` - Different seeds → different patches
- `test_determinism_across_multiple_runs` - Consistency across runs
- `test_seed_provenance` - SEED tracking in generated patches

### 4. **Patch Type Tests** (4 tests)
Tests specific patch type generation logic.

- `test_subtractive_patch_structure` - VCO→VCF→VCA chains
- `test_generative_patch_has_sequencer_or_lfo` - Generative patch requirements
- `test_percussion_patch_structure` - Noise-based percussion
- `test_fx_chain_structure` - Effects processing chains

### 5. **Edge Cases Tests** (6 tests)
Tests error conditions and boundary cases.

- `test_empty_rack_generates_no_patches` - Empty rack handling
- `test_single_module_generates_no_patches` - Insufficient modules
- `test_default_seed_used_when_none_provided` - Default seed handling
- `test_default_config_used_when_none_provided` - Default config handling
- `test_patch_to_dict` - Serialization
- `test_connection_to_dict` - Connection serialization

### 6. **Configuration Tests** (3 tests)
Tests `PatchEngineConfig` settings.

- `test_max_patches_limit` - Respects max_patches setting
- `test_config_defaults` - Default configuration values
- `test_config_custom_values` - Custom configuration handling

## Test Database

Tests use an in-memory SQLite database for speed and isolation:

- Each test function gets a fresh database
- Fixtures create sample modules, cases, and racks
- No test pollution between runs

### Available Fixtures

```python
# Database
db_engine     # SQLite engine
db_session    # Database session

# Test Data
sample_user       # Test user account
sample_case       # 84HP Eurorack case
sample_vco        # VCO module
sample_vcf        # Filter module
sample_vca        # Amplifier module
sample_envelope   # Envelope generator
sample_lfo        # LFO module
sample_sequencer  # Sequencer module
sample_noise      # Noise source
sample_effect     # Effects module
sample_mixer      # Mixer module

# Racks
sample_rack_empty  # Empty rack
sample_rack_basic  # VCO + VCF + VCA
sample_rack_full   # All module types
```

## Key Test Principles

### 1. **Determinism is Critical**
Every patch generation must be 100% deterministic. Same seed + same rack = identical patch, always.

```python
seed = 12345
patches1 = generate_patches_for_rack(db, rack, seed)
patches2 = generate_patches_for_rack(db, rack, seed)
assert patches1 == patches2  # Must be identical
```

### 2. **SEED Provenance**
Every generated patch must track its generation_seed for reproducibility.

```python
patch = generate_patches_for_rack(db, rack, seed=42)[0]
assert patch.generation_seed == 42  # or derivative
```

### 3. **Rule-Based Logic**
Patch generation follows Eurorack conventions:
- VCO → VCF → VCA (subtractive synthesis)
- Sequencer/LFO → Modulation (generative)
- Noise → VCF → VCA (percussion)

## Known Issues

### Database Schema Mismatches
Some tests may fail due to model field name differences between test fixtures and actual models. If you see errors like:

```
TypeError: 'field_name' is an invalid keyword argument for Model
```

Check the actual model definition in the corresponding `models.py` file and update the fixtures in `conftest.py`.

### SQLite vs PostgreSQL Differences
- JSON fields may behave differently
- Some Postgres-specific features (like JSONB) aren't available in SQLite
- Date/time handling may differ

For production-like testing, use PostgreSQL:

```python
# In conftest.py
engine = create_engine("postgresql://test:test@localhost/test_patchhive")
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: patchhive
          POSTGRES_PASSWORD: patchhive
          POSTGRES_DB: patchhive_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install pytest pytest-cov
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          python3 -m pytest tests/ -v --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Writing New Tests

### Test Structure Template

```python
class TestFeature:
    """Tests for Feature."""

    def test_feature_behavior(self, db_session: Session, sample_rack: Rack):
        """Test specific behavior of feature."""
        # Arrange
        config = SomeConfig()

        # Act
        result = do_something(db_session, sample_rack, config)

        # Assert
        assert result.is_valid
        assert len(result.items) > 0
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** - describe what's being tested
3. **Use fixtures** - don't create test data inline
4. **Test edge cases** - empty inputs, null values, etc.
5. **Test determinism** - run generation multiple times
6. **Verify SEED provenance** - check generation_seed field

## ABX-Core v1.2 Compliance

These tests verify compliance with ABX-Core v1.2 requirements:

✅ **Deterministic Behavior** - `TestDeterminism` suite
✅ **SEED Provenance** - All patches track generation_seed
✅ **Reproducibility** - Same inputs always produce same outputs
✅ **Entropy Minimization** - No untracked randomness
✅ **Modular Architecture** - Clear separation of concerns

## Contributing

When adding new features to the patch engine:

1. Write tests first (TDD)
2. Ensure determinism is maintained
3. Add tests to appropriate test class
4. Run full test suite before committing
5. Aim for >90% code coverage

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [ABX-Core Specification](../docs/ABX_CORE_COMPLIANCE.md)
- [Patch Engine Documentation](../docs/PATCH_ENGINE.md)

---

**Questions?** Check the [main README](../../README.md) or open an issue on GitHub.
