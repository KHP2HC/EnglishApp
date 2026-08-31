# Contributing

## Development Setup

```bash
git clone https://github.com/englishcoachpro/EnglishCoachPro.git
cd EnglishCoachPro
pip install -r requirements.txt
pip install pytest ruff
```

## Code Style

- Use **Ruff** for linting and formatting
- Follow PEP 8 conventions
- Keep functions focused and well-documented

## Running Tests

```bash
pytest tests/ -v
```

## Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This will run Ruff linting and formatting before each commit.

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit
3. Ensure tests pass: `pytest tests/ -v`
4. Open a Pull Request to `main`
5. GitHub Actions will run tests automatically

## Release Process

1. Tag a release: `git tag v1.0.0 && git push --tags`
2. GitHub Actions builds the EXE and creates a Release
3. Download from the Releases page
