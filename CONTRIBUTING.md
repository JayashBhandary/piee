# Contributing to PIEE

First off, thank you for considering contributing to PIEE! We're building a unified AI infrastructure platform, and community contributions are incredibly valuable.

## Setting Up for Development

1. Fork and clone the repository.
2. Ensure you have `python3`, `node/bun`, and `docker` installed.
3. Run `make setup` to install dependencies and configure the environment.
4. Install the git pre-commit hooks: `pip install pre-commit && pre-commit install`

## Development Workflow

We use a unified `Makefile` to handle common development tasks. 

- `make dev` — Starts both the API backend and the Next.js Dashboard.
- `make format` — Auto-formats code (Ruff for backend, Prettier for frontend).
- `make lint` — Lints code to ensure it meets our quality standards.
- `make test` — Runs the automated test suite (Pytest).

**Please make sure to run `make format`, `make lint`, and `make test` before submitting your Pull Request.**

## Pull Request Process

1. Create a descriptive branch name (`feature/add-new-provider`, `fix/token-calculation`).
2. Make your proposed changes. Write tests if adding new functionality.
3. Update related documentation in the `README.md` if necessary.
4. Open a Pull Request targeting the `main` branch.
5. Fill out the provided Pull Request template completely.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful, inclusive, and constructive in all discussions.
