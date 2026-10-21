# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-10-21

### Added
- Public `invalidate(*args, **kwargs)` method on every decorated function (awaitable
  for async functions) that drops the cached entry for a specific call — the key is
  `sha256(func_name + args + kwargs)`, mirroring `functools.lru_cache.cache_clear`.
- `py.typed` marker (PEP 561) so downstream users get inline type information.
- `NO_TTL` sentinel and the `Ttl` type alias on the state interface, replacing the use
  of the private `inspect._empty`.
- CI/CD and project tooling:
  - GitHub Actions CI running ruff, strict mypy and pytest across Python 3.10–3.13.
  - PyPI publishing workflow via Trusted Publishing, skipping already-published versions.
  - Codecov integration (`codecov.yml`).
  - `CONTRIBUTING.md` and `CLAUDE.md`.

### Changed
- Migrated packaging from Poetry to **uv** (PEP 621 `pyproject.toml`, `hatchling` build
  backend, `[dependency-groups]`); added `uv.lock` and dropped `poetry.lock`.
- Enabled **strict mypy** type checking across `mr/` and fully annotated the package.
- Pre-commit hooks now run through uv (ruff, ruff-format, mypy, pytest, mutatest).
- `TempFileState` pins the pickle protocol to 4 for a stable on-disk format across
  Python versions.
- Replaced the deprecated `datetime.utcnow()` with timezone-aware
  `datetime.now(timezone.utc)`.

### Fixed
- Extras re-export appended `"RedisState"` / `"TempFileState"` to `__all__`
  character-by-character instead of the module name.
- `Mime.sync_acquire_state` used the async context manager inside a synchronous `with`.
- `RedisState` passed the "no TTL" sentinel as the Redis `ex` expiry; it now maps to
  `None` (never expires).

[Unreleased]: https://github.com/CenturyBoys/my-mimic/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/CenturyBoys/my-mimic/releases/tag/v0.6.0
