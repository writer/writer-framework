# Contributing to Writer Framework

Thank you for your interest in contributing to Writer Framework.

## Ways to contribute

- **Report bugs**: Include steps to reproduce the bug. Use "Issues" on GitHub.
- **Suggest enhancements**: Use "Discussions" on GitHub for feature requests.
- **Browse Issues and Discussions**: See if you can help with existing issues.

## Development Setup

### Prerequisites

- Python 3.9.2 - 3.12
- Node.js 22.x
- [Poetry](https://python-poetry.org/) for Python dependency management

### Setup Steps

1. **Install dependencies**:
   ```sh
   poetry install --with build
   alfred install.dev
   ```

2. **Activate virtual environment**:
   ```sh
   # Bash/Zsh/Csh
   eval "$(poetry env activate)"
   
   # Fish
   eval (poetry env activate)
   
   # PowerShell
   Invoke-Expression (poetry env activate)
   ```

3. **Test the setup**:
   ```sh
   writer edit apps/hello --port 5000
   ```

## Frontend Development

For frontend development with auto-reload:

1. **Run the app on default port**:
   ```sh
   writer edit apps/hello
   ```

2. **Start the frontend dev server**:
   ```sh
   npm run dev
   ```

This will start the frontend development server with auto-reload for faster development.

## Development Workflow

1. **Create a feature branch** off `dev`:
   ```sh
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure they pass all checks

3. **Run tests locally**:
   ```sh
   alfred ci
   ```

4. **Create a pull request** to the `dev` branch

## Testing and Code Quality

### Running Tests

```sh
# Run all tests (backend + frontend)
alfred ci

# Backend only
alfred ci --back

# Frontend only  
alfred ci --front

# End-to-end tests
alfred ci --e2e chromium
```

### Code Standards

- **Backend**: Use `ruff` for linting (automatically runs in CI)
- **Frontend**: Use Prettier for formatting
- **Type checking**: `mypy` validation is required
- **Tests**: All tests must pass

### CI Requirements

Your pull request must pass all CI checks:
- Python linting (`ruff`)
- Type checking (`mypy`)
- Backend tests (`pytest`)
- Frontend linting and build
- End-to-end tests (when applicable)

The CI runs on Python versions 3.9-3.13 and Node.js 22.x.
