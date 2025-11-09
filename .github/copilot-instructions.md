# Codigo Facilito Downloader - AI Agent Instructions

## Project Overview

Python-based web scraper and downloader for Codigo Facilito courses/bootcamps using **Playwright** for browser automation and **asyncio** for async operations. The project provides both a CLI (`facilito`) and an async API (`AsyncFacilito`).

## Architecture Pattern: Collector-Downloader Separation

The codebase follows a **two-phase architecture** that separates data collection from downloading:

### 1. Collectors (`src/facilito/collectors/`)

Scrape course/bootcamp metadata using Playwright selectors:

- `bootcamp.py`: Extracts bootcamp structure (modules → units), handles collapsible sections
- `course.py`: Extracts course structure (chapters → units)
- `unit.py`: Fetches unit-level metadata, follows redirects for bootcamp lessons
- `video.py`: Extracts video URLs and IDs from page DOM

### 2. Downloaders (`src/facilito/downloaders/`)

Handle actual file downloads:

- `bootcamp.py`: Downloads bootcamps with structure `Facilito/{bootcamp-slug}/{NN}_{module-slug}/{NN}_{unit-slug}.ext`
- `course.py`: Downloads courses with structure `Facilito/{course-slug}/{NN}_{chapter-slug}/{NN}_{unit-slug}.ext`
- `unit.py`: Downloads individual units (videos as `.mp4`, lectures/quizzes as `.mhtml`)
- `video.py`: Uses external `vsd` binary for HLS streaming, auto-downloads platform-specific binary on first use

## Critical Developer Workflows

### Setup & Dependencies

```bash
poetry install                    # Install dependencies
playwright install chromium       # Required: Playwright browser
```

### Development Tools

```bash
ruff format .                     # Format code (required before commits)
mypy .                           # Type checking
pytest                           # Run tests (limited coverage currently)
```

### CLI Usage Pattern

```bash
facilito login                    # Browser-based auth (uses Playwright stealth)
facilito set-cookies cookies.json # Alternative: cookie-based auth
facilito download <url> -q 720p -t 10  # Quality + thread options
```

## Key Conventions & Patterns

### 1. Entity Model Hierarchy

Defined in `models.py` using Pydantic:

- **Course**: `chapters` → **Chapter**: `units` → **Unit**
- **Bootcamp**: `modules` → **Module**: `units` → **Unit**
- **Unit**: Has `type` (VIDEO | LECTURE | QUIZ) and `slug` for file naming

### 2. Authentication State Management

- Session stored in `tempfile.gettempdir()/Facilito/state.json` (see `constants.py`)
- Uses `@login_required` decorator in `async_api.py` to gate authenticated operations
- Cookies normalized via `normalize_cookies()` to handle browser-specific `sameSite` values

### 3. Context Manager Pattern

Always use `AsyncFacilito` as async context manager:

```python
async with AsyncFacilito() as client:
    bootcamp = await client.fetch_bootcamp(url)
    await client.download(url, quality=Quality.P720)
```

### 4. URL-Based Routing

URL patterns determine entity types (`utils.py`):

- `/programas/` → Bootcamp (NEW in feature/bootcamps branch)
- `/cursos/` → Course
- `/videos/` → Video
- `/articulos/` → Lecture
- `/quizzes/` → Quiz

### 5. Error Handling Strategy

- `@try_except_request` decorator wraps all API methods to log exceptions without crashing
- Custom exceptions inherit from `BaseError` (see `errors.py`)
- Errors logged to both console (INFO level, colored) and `facilito.log` (DEBUG level)

### 6. File Naming Convention

Use `slugify()` from `helpers.py` for all filenames:

```python
slugify("Café! Frío?")  # → "cafe-frio"
```

### 7. Playwright Stealth Mode

Browser context uses `playwright-stealth` to bypass detection (see `async_api.py` `__aenter__`)

## External Dependencies

- **FFmpeg**: Required subprocess for video merging (not installed by project)
- **VSD Binary**: Auto-downloaded HLS downloader (v0.3.2), platform-specific, cached in `Facilito/.bin/` directory

## Testing Strategy

Minimal test coverage (only `test_helpers.py` exists). Use `pytest.mark.parametrize` for helper function tests. **TODO item**: Write integration tests for collectors/downloaders.

## Semantic Commit Convention (Required)

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(cli):` - New CLI features
- `fix(parser):` - Bug fixes
- `refactor(collectors):` - Code improvements
- `docs:`, `test:`, `chore:` - Documentation, tests, maintenance

## Project-Specific Gotchas

1. **Mobile Context**: Playwright uses `is_mobile=True` for better selector reliability with Codigo Facilito's responsive design
2. **Progressive Scrolling**: `save_page()` uses `progressive_scroll()` before saving `.mhtml` to ensure lazy-loaded content renders
3. **Quality Enum**: `Quality.MAX` dynamically selects highest available resolution, not hardcoded 1080p
4. **Thread Parameter**: Controls concurrent downloads via `vsd` binary, not Python threads
5. **Override Flag**: Must explicitly set `-w/--override` to re-download existing files (default: skip)
6. **Bootcamp Redirects**: Bootcamp lesson URLs (`/cursos/bootcamp-...?play=true`) redirect to actual video URLs; collectors must follow redirects

## Entry Points

- **CLI**: `facilito` command → `src/facilito/cli.py:app` (Typer app)
- **API**: Import `AsyncFacilito` from `facilito` package
- **Poetry Script**: Defined in `pyproject.toml` `[tool.poetry.scripts]`

## Code Style Notes

- **Import Order**: Ruff enforces standard library → third-party → local imports
- **Type Hints**: Use `str | None` (PEP 604) not `Optional[str]`
- **Pydantic Models**: Defined in `models.py` for type safety
- **Async Everywhere**: All I/O operations use `async/await` pattern
