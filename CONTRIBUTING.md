# Contributing to my-mimic

Thanks for your interest in contributing! This guide explains how to set up the
project and the conventions we follow.

## Getting Started

1. Fork and clone the repository.
2. Make sure you have [uv](https://docs.astral.sh/uv/) installed.
3. Set up the environment (installs all extras and dev dependencies):

   ```shell
   uv sync --all-extras
   ```

4. (Optional) install the git hooks:

   ```shell
   uv run pre-commit install
   ```

## Development Setup

This project is **uv-first** — do not use `poetry` or `pip` directly. Common commands:

```shell
uv run pytest                 # run the test suite
uv run pytest --cov=mr        # run tests with coverage
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy                   # strict type-check
uv run mutatest -n 100 -s mr  # mutation testing
```

## Making Changes

### Code Style

- Code is linted and formatted with **ruff** (config in `pyproject.toml`).
- Types are checked with **mypy** in `strict` mode over `mr/`. New code must keep the
  type-check green.
- Run the full gate before opening a PR:

  ```shell
  uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest
  ```

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add sqlite state backend
fix: handle NO_TTL in redis expiry
chore: bump redis to 5.2
```

## Testing

- Add tests under `tests/` mirroring the package layout.
- Keep coverage high (see the coverage report in CI / Codecov).
- Both sync and async code paths should be covered.

## Pull Request Process

1. Create a branch off `main` (e.g. `feat/sqlite-state`).
2. Make your changes with tests and keep the quality gate green.
3. Push and open a PR against `main`. CI runs lint, format, mypy, and tests across the
   supported Python versions.
4. Address review feedback; a maintainer will merge once approved.

## Releasing (maintainers)

- Bump `version` in `pyproject.toml`.
- Publish a GitHub release — `.github/workflows/publish.yml` builds and uploads to PyPI
  via Trusted Publishing.

## License

By contributing, you agree that your contributions are licensed under the project's
Apache-2.0 License.
