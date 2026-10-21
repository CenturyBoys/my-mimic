# CLAUDE.md

Guidance for Claude Code (and other AI agents) when working in this repository.

## Project Overview

`my-mimic` (import name `mr`, "Mr. Mime") is a small cache/memoization library. It
exposes a `Mime` decorator that memoizes sync and async functions, backed by a
pluggable `IState` storage interface. Three state implementations ship with it:
in-memory (default), Redis (extra `redis_edition`), and temp-file (extra
`temp_edition`).

## Tooling

This project is **uv-first**. Do not use `poetry` or `pip` directly.

```shell
uv sync --all-extras          # create/refresh the virtualenv with all extras + dev deps
uv run pytest                 # run the test suite
uv run pytest --cov=mr --cov-report=term-missing   # tests with coverage
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy                   # strict type-check (config in pyproject.toml)
uv run mutatest -n 100 -s mr  # mutation testing
uv build                      # build sdist + wheel
```

Run `uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest`
before committing — this mirrors the CI gate.

## Architecture

- `mr/mime.py` — the `Mime` decorator. It is a `meeseeks` singleton keyed by args
  (`by_args_hash=True`). `__call__` hashes `func_name + args + sorted(kwargs)` with
  SHA-256, looks the key up in the configured state, and stores misses. Classes are
  rejected (`TypeError`). Sync and async callables are detected with `inspect` and
  wrapped separately. The returned wrapper also exposes `.invalidate(*args, **kwargs)`
  (awaitable for async functions), which recomputes the same key and drops that entry
  from the state — mirroring how `functools.lru_cache` attaches `cache_clear`.
- `mr/config/__init__.py` — `Config`, a frozen slotted dataclass holding the state
  class + its kwargs. `initialized_state` lazily instantiates the state (once).
- `mr/states/interface.py` — `IState` ABC. Defines `NO_TTL` (the "never expires"
  sentinel) and the `Ttl` type alias (`int | type[_empty]`). Implement this to add a
  new backend.
- `mr/states/implementations/` — `MemoryState` (default), `RedisState`, `TempFileState`.
- `mr/states/__init__.py` — re-exports the extras, guarded by `try/except ImportError`
  so the package imports cleanly without the optional deps installed.

## Conventions

- **Types:** mypy runs in `strict` mode over `mr/`. Keep it green — annotate fully.
  `Any` is acceptable at the cache boundary (values are arbitrary). Third-party libs
  without stubs (`meeseeks`, `aiofile`) are whitelisted in `[[tool.mypy.overrides]]`.
- **TTL:** use the `NO_TTL` sentinel for "never expires", never a bare `None` or the
  private `inspect._empty`.
- **Serialization:** `TempFileState` and `RedisState` pickle values. `TempFileState`
  pins `protocol=4` so the on-disk format is stable across Python versions — do not
  change it without a migration story.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, …), matching the
  existing history.
- **Versioning:** bump `version` in `pyproject.toml`; publishing happens on a GitHub
  release via `.github/workflows/publish.yml`.
- `py.typed` ships with the package (PEP 561) — keep it.
