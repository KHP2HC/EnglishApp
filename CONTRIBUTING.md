# Contributing to EnglishCoach Pro

Thank you for your interest in contributing to EnglishCoach Pro! This is an open-source, non-profit English learning platform, and we welcome contributions of all kinds.

## Development Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm** (for the web frontend)
- **Git**

### Backend (Desktop App + API)

```bash
# Clone the repository
git clone https://github.com/KHP2HC/EnglishApp.git
cd EnglishApp

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the desktop app
python main.py

# Or run the FastAPI backend only
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Web App)

```bash
cd web
npm install
cp .env.example .env.local  # Fill in Supabase credentials if available
npm run dev
```

### Environment Variables

1. Copy `.env.example` to `.env` at the project root.
2. Copy `web/.env.example` to `web/.env.local` for frontend variables.
3. **Never commit `.env` or `.env.local` files.**

## Branch Naming

Use descriptive branch names with a prefix:

- `feature/add-new-feature`
- `fix/resolve-bug-description`
- `docs/update-readme`
- `refactor/simplify-module`

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Build, dependencies, tooling |
| `ci` | CI/CD changes |

**Examples:**

```
feat(vocabulary): add IPA pronunciation display
fix(planner): handle string exam types in schedule generation
docs(readme): update installation instructions
test(speaking): add mock for edge-tts dependency
```

## Pull Requests

1. Create a feature branch from `main`.
2. Make your changes with clear, focused commits.
3. Ensure all tests pass:
   ```bash
   # Backend tests
   python -m pytest tests/ -v

   # Frontend lint and build
   cd web && npm run lint && npm run build
   ```
4. Write a clear PR description explaining what changed and why.
5. Link any related issues.

### PR Checklist

- [ ] Code follows existing style conventions
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] No secrets or `.env` files committed
- [ ] No `__pycache__`, `node_modules`, or build artifacts committed
- [ ] Documentation updated if needed

## Testing Requirements

- All new features must include tests.
- Bug fixes should include a regression test.
- Run the full test suite before submitting a PR:

```bash
python -m pytest tests/ -v
```

## Code Quality

- Python: [Ruff](https://docs.astral.sh/ruff/) is configured via `.pre-commit-config.yaml`.
- TypeScript: ESLint and Prettier are configured in `web/`.
- Install pre-commit hooks:
  ```bash
  pip install pre-commit
  pre-commit install
  ```

## Reporting Issues

When reporting an issue, please include:

1. **Description** of the problem
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment** (OS, Python version, Node version)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
