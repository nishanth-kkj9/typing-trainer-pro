# Contributing

## Setup

```bash
git clone https://github.com/nishanth-kkj9/typing-trainer-pro.git
cd typing-trainer-pro
python -m venv .venv && .venv/Scripts/activate
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
pytest                          # all tests
pytest tests/unit               # unit-only
pytest tests/integration        # integration-only
pytest --cov=typing_trainer     # with coverage report
```

## Code Style

- `ruff` for linting + formatting (line-length: 100)
- `mypy` for type checking (strict mode)
- Pre-commit hooks: ruff → mypy → pytest

## Git Workflow

1. Create feature branch from `main`
2. Write tests first (TDD encouraged)
3. Ensure CI passes
4. Open PR with description

## Commit Conventions

```
<type>(<scope>): <description>

feat(core): add finger-to-key latency tracking
fix(ui): correct keyboard highlight overflow
test(stats): add WPM edge case coverage
</type>
```

Types: feat, fix, test, docs, refactor, chore, ci
