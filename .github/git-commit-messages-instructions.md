# GitHub Copilot Custom Instructions - Git Conventional Commit Messages

These instructions guide GitHub Copilot in generating Git commit messages that adhere to the Conventional Commits specification for the **Codigo Facilito Downloader** project.

---

## ⚠️ CRITICAL: COPILOT MUST ALWAYS FOLLOW ALL RULES IN THIS FILE

**MANDATORY REQUIREMENTS:**

1. ✅ **ALWAYS apply ALL rules from this document when generating commit messages**
2. ✅ **NEVER generate simple/generic messages** - always follow the structure, scope, and body guidelines
3. ✅ **ALWAYS include body for multi-file commits** (2+ files) unless title is completely self-explanatory
4. ✅ **ALWAYS list modified files in body** (for 2-10 files) with brief descriptions in past tense
5. ✅ **ALWAYS use correct type hierarchy** for mixed commits: code > docs > chore
6. ✅ **NEVER use forbidden patterns**: `feat(docs)`, `refactor(docs)`, `fix(docs)`, `chore(docs)`, `feat(settings)`, `refactor(config)`

**⚠️ SPECIAL CASE: MODIFYING THIS FILE ITSELF (.github/git-commit-messages-instructions.md)**

- **EVEN THOUGH this is a .md file, you MUST still follow ALL rules**
- **NEVER generate simple messages like "Add instructions" or "Update rules"**
- **ALWAYS include proper body with file list and explanations**
- **Example**: When modifying this file + settings.json, use type `docs` with FULL body structure
- **This file being .md does NOT exempt it from requiring detailed commit messages**

**IF YOU GENERATE A COMMIT MESSAGE THAT VIOLATES THESE RULES, YOU HAVE FAILED.**

---

**I. Conventional Commits Specification:**

- "Generate commit messages that follow the Conventional Commits specification ([https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/))."
- "Structure commit messages with a type, an optional scope, and a description: `<type>[optional scope]: <description>`"
- "A complete commit message follows this structure:"

  ```
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  ```

- "Separate the header from the optional body and footer with a blank line."

**II. Commit Message Structure:**

- **Header:**
  - **Type:**
    - "Use one of the following types (in lowercase) based on these specific criteria:"
      - `feat`: **NEW FUNCTIONALITY** - Adding new features, CLI commands, or capabilities that provide value to users. Examples:
        - Adding new CLI commands (e.g., `facilito export`, `facilito list-courses`)
        - Implementing support for new content types (e.g., bootcamps, exams)
        - Adding new download quality options or formats
        - Creating new collectors for additional content types
        - Adding authentication methods (e.g., OAuth, SSO support)
        - Implementing progress tracking or resume capabilities
      - `fix`: **BUG RESOLUTION** - Correcting existing functionality that was not working as intended. Examples:
        - Fixing authentication issues (cookie handling, session persistence)
        - Resolving video download failures or incomplete downloads
        - Correcting Playwright selectors that no longer match page structure
        - Fixing file naming issues (slugify, special characters, duplicates)
        - Resolving threading or async/await issues in downloaders
        - Correcting URL parsing or entity detection logic
      - `refactor`: **CODE IMPROVEMENT WITHOUT BEHAVIOR CHANGE** - Restructuring existing code without changing its external behavior or adding new features. Examples:
        - Extracting methods or functions for better organization
        - Renaming variables/functions for clarity (e.g., `get_data` to `fetch_course_metadata`)
        - Simplifying complex logic in collectors/downloaders while maintaining same functionality
        - Reorganizing file structure (moving files between folders)
        - Applying design patterns (Factory, Strategy, etc.)
        - Converting synchronous code to asynchronous without adding features
        - Removing unused code, imports, or dependencies
        - Improving type hints or Pydantic models
      - `perf`: **PERFORMANCE OPTIMIZATION** - Code changes that specifically improve performance without adding new features. Examples:
        - Optimizing Playwright page navigation or selector queries
        - Implementing parallel downloads or async batching
        - Reducing memory usage in video processing
        - Caching API responses or course metadata
        - Improving VSD binary download speed or retry logic
        - Optimizing file I/O operations (chunked reads/writes)
      - `build`: Changes that affect the build system or external dependencies (e.g., Poetry, pyproject.toml, VSD binary).
      - `ci`: Changes to CI/CD configuration files and scripts (e.g., GitHub Actions, pre-commit hooks).
      - `docs`: **DOCUMENTATION FILES ONLY** - Changes exclusively to standalone documentation files (.md, .rst, .txt). Examples:
        - Modifying Markdown (.md) files (README.md, CONTRIBUTING.md, CHANGELOG.md, git-commit-messages-instructions.md, etc.)
        - Creating new documentation files (.md, .rst, .txt, etc.)
        - **CRITICAL RULE**: If ONLY .md or documentation files are modified/created, use `docs` type
        - **⚠️ IMPORTANT**: Being a .md file does NOT mean "use simple commit message" - ALL rules still apply!
        - **⚠️ MULTI-FILE .md COMMITS**: 2+ .md files REQUIRE body with file list, same as any other type
        - **ABSOLUTELY FORBIDDEN**: `feat(docs)`, `refactor(docs)`, `fix(docs)`, `chore(docs)` ← NEVER EVER USE THESE
        - **ALWAYS CORRECT**: `docs` or `docs(scope)` where scope is optional filename (e.g., `docs(readme)`, `docs(git-commit)`, or just `docs`)
        - **WHY**: `docs` IS the type (describes WHAT changed), NOT a scope. Scope describes WHERE (which file).
        - **PATTERN**: `docs` type + optional `(filename)` scope → `docs(readme): ...` ✅ NOT `feat(docs): ...` ❌
        - **FOR MIXED COMMITS** (code + docs): Use code type (feat/fix/refactor), mention docs in body, NEVER use `feat(docs)`
        - **IMPORTANT**: Docstrings and inline comments in .py files are NOT `docs` type - they follow the code change type (see Python-Specific Guidelines)
        - **REMEMBER**: docs type ≠ simple message allowed. Same structure requirements apply (body, file list, etc.)
      - `style`: Changes that do not affect the meaning of the code (whitespace, formatting with ruff, import ordering, etc.).
      - `test`: Adding missing tests or correcting existing tests (pytest).
      - `revert`: Reverts a previous commit (use footer to reference reverted commits).
      - `chore`: Miscellaneous commits. Other changes that don't modify `src` or test files (e.g., .gitignore, .vscode/, .bin/ files, state.json, editor config, package updates)
        - **CRITICAL RULE**: Configuration files (.vscode/settings.json, .editorconfig, etc.) should use `chore`, NOT `feat(settings)` or `refactor(settings)`
        - **Examples**: `chore: update VSCode settings`, `chore: add editor configuration`, `chore: update .gitignore`
    - "**IMPORTANT**: If you're restructuring code without adding new functionality or changing behavior, use `refactor`, NOT `feat`."
    - "**CRITICAL FOR DOCUMENTATION FILES**: Use `docs` type ONLY for standalone documentation files (.md, .rst, .txt). If modifying Python code with docstrings/comments, use the appropriate code type (refactor, feat, fix) based on what the code does. NEVER combine with other types like `feat(docs)` or `refactor(docs)`. The scope is optional (e.g., `docs(readme):` or just `docs:`)."
    - "**CRITICAL FOR CONFIG FILES**: Configuration files (.vscode/, .editorconfig, .gitignore, etc.) should use `chore`, NOT `feat(config)` or `refactor(config)`. These are tooling/environment changes, not code changes."
    - "If none of the types apply, use 'chore'."
  - **Scope (Optional but Strongly Recommended for this project):**
    - "**STRONGLY RECOMMENDED to include a scope** to provide context about what part of the codebase was affected."
    - "Scope is OPTIONAL per Conventional Commits spec, but provides valuable context."
    - "Use the following scope hierarchy (most specific applicable level):"
      - **Module Level**: `cli`, `api`, `collectors`, `downloaders`, `auth`, `models`, `utils`, `helpers`, `logger`
      - **Feature/Component Level**: `course`, `video`, `unit`, `lecture`, `quiz`, `bootcamp`, `playlist`
      - **File-Specific Level**: `async_api`, `constants`, `errors`, `parsers`
    - "**Scope Examples for Codigo Facilito Downloader:**"
      - `feat(cli): add export command to save course metadata`
      - `fix(collectors/video): correct HLS stream URL extraction`
      - `refactor(downloaders/course): extract directory creation logic`
      - `perf(downloaders/video): optimize VSD binary thread usage`
      - `test(helpers): add parametrized tests for slugify function`
      - `docs(readme): update installation instructions for Poetry`
      - `feat(auth): add support for OAuth authentication`
      - `fix(cli): handle missing quality parameter gracefully`
    - "If the change affects multiple scopes, use the most general applicable scope or omit parentheses for cross-cutting changes."
  - **Description:**
    - "A concise description of the change in imperative, present tense (e.g., 'fix: correct typos in documentation', not 'fixed typos...')."
    - "Capitalize the first letter of the description."
    - "Do not end the description with a period."
    - "Limit the description to 50 characters."
- **Body (Optional but Recommended for Complex Changes):**
  - "**WHEN TO INCLUDE BODY:**"
    - "**REQUIRED when modifying multiple files** unless the title is self-explanatory"
    - "When the change needs explanation beyond the title"
    - "When explaining WHY the change was made (motivation)"
    - "When describing the impact or side effects"
    - "For complex refactoring or architectural changes"
  - "**WHEN BODY CAN BE OMITTED:**"
    - "Simple, self-explanatory single-file changes"
    - "The title completely describes the change"
    - "Trivial fixes or updates (e.g., 'docs: fix typo in README')"
    - "**⚠️ CRITICAL**: Multi-file changes (.md or not) ALWAYS need body - no exceptions!"
    - "**⚠️ CRITICAL**: 'docs' type does NOT mean body is optional for 2+ files"
    - "Example: 2 .md files changed = body REQUIRED, even if both are documentation"
  - "**BODY FORMAT AND STYLE:**"
    - "Write in **past tense** (describe what was done, not what to do)"
    - "Examples: 'Added feature X', 'Implemented Y', 'Fixed Z', 'Updated configuration'"
    - "Use complete sentences with proper capitalization and punctuation"
    - "Wrap lines at 72 characters for readability"
    - "Separate paragraphs with blank lines for better structure"
  - "**LISTING MODIFIED FILES:**"
    - "For **2-10 files**: List files with brief description of changes"
    - "Format: 'Modified files (X):' or 'Affected files (X):' followed by bulleted list"
    - "Use `-` (hyphen) for bullet points, not `•`"
    - "Example format: `- FileName.cs: Brief description of change`"
    - "File descriptions should use past tense (e.g., 'Added method', 'Updated logic')"
    - "For **>10 files**: Group by layer/component instead of listing all files"
    - "Example: 'This change spans multiple layers (15 files modified):'"
    - "Then list high-level changes by component/layer, not individual files"
    - "For **1 file**: Generally omit file listing (it's in the commit diff)"
  - "Explain the motivation for the change and how it differs from previous behavior."
  - "For significant changes, include performance metrics, testing notes, or migration guidance."
- **Footer (Optional):**
  - "Use the footer to reference issue trackers, breaking changes, or other metadata."
  - "**Breaking Changes:** Start with `BREAKING CHANGE: ` (or `BREAKING-CHANGE:`) followed by a description. Alternatively, append `!` after type/scope (e.g., `feat!:` or `feat(api)!:`)."
  - "**Issue References:** Use `Closes #issueNumber`, `Fixes #issueNumber`, `Resolves #issueNumber` to link to issues."
  - "**Other Footers:** May include `Reviewed-by:`, `Refs:`, `Acked-by:`, etc. following git trailer format."

**II.A. Breaking Changes - Detailed Guidelines:**

**When to Mark as BREAKING CHANGE (correlates with MAJOR version bump):**

A breaking change is ANY modification that requires users of the CLI or API to make changes to their scripts or workflow. Use `BREAKING CHANGE:` footer or `!` suffix when:

**1. API Contract Changes (AsyncFacilito):**

- **Changing method signatures:**
  - Removing parameters from public async methods
  - Changing parameter types or order
  - Changing return types (Pydantic models)
  - Example: `download(url: str)` → `download(url: str, quality: Quality)`
- **Removing or renaming public methods:**
  - Deleting public methods in AsyncFacilito class
  - Renaming methods (e.g., `fetch_course` → `get_course_metadata`)
  - Removing CLI commands (e.g., removing `facilito set-cookies`)
- **Changing Pydantic model structures:**
  - Removing fields from Course, Chapter, Unit, or Video models
  - Changing field types (e.g., `id: int` → `id: str`)
  - Renaming model properties (e.g., `course_name` → `title`)
  - Example: `Video(id=123, url="...")` → `Video(video_id="abc", stream_url="...")`

**2. Behavior Changes:**

- **Changing default behavior:**
  - Modifying default values that affect functionality
  - Changing validation rules that reject previously valid input
  - Altering error handling or exception types
  - Example: Changing default quality from "max" to "720p"
- **Changing download logic:**
  - Modifying file naming conventions that break existing patterns
  - Changing directory structure for saved files
  - Altering authentication/session requirements
  - Example: Changing from `.mp4` to `.mkv` default format

**3. File System Changes:**

- **Directory structure changes:**
  - Changing output directory naming patterns
  - Modifying course/chapter/unit folder hierarchy
  - Example: `{NN}_{slug}` → `{slug}-{NN}`
- **File naming changes:**
  - Changing slugify behavior that affects filenames
  - Modifying file extension mapping (e.g., lectures as `.html` vs `.mhtml`)
  - Removing or renaming state/cache files (e.g., `state.json` location)

**4. Configuration Changes:**

- **Removing or renaming configuration files:**
  - `state.json` structure changes requiring migration
  - Cookie file format changes
  - Example: Moving from `tempfile.gettempdir()/Facilito/` to `.config/facilito/`
- **Changing required configuration:**
  - Adding new required CLI arguments without defaults
  - Removing previously optional flags that become required
  - Example: Requiring explicit `--quality` parameter

**5. Dependency Changes:**

- **Major Python version upgrades:**
  - Python 3.10 → 3.11 or 3.11 → 3.12
  - Playwright 1.39 → 1.40 with breaking selector changes
  - Example: Requiring new Python features unavailable in older versions
- **Removing dependencies:**
  - Removing packages that users might import directly
  - Changing VSD binary interface or parameters
  - Example: Replacing `vsd` with different HLS downloader

**6. Authentication/Authorization Changes:**

- **Changing security requirements:**
  - Modifying cookie handling or session persistence
  - Changing `sameSite` cookie validation rules
  - Requiring different authentication flow (e.g., removing cookie auth)
  - Example: Forcing browser-based login, disabling `set-cookies` command

**When NOT to mark as BREAKING CHANGE:**

❌ **Pure refactoring (no external impact):**

- Internal code reorganization (moving files, renaming private functions)
- Extracting private helper functions or classes
- Improving internal algorithms with same output
- Example: `refactor(downloaders): extract retry logic to decorator` (internal change only)

❌ **Backward-compatible additions:**

- Adding new optional CLI flags with defaults
- Adding new AsyncFacilito methods without removing existing ones
- Adding new fields to Pydantic models (additive only)
- Example: `feat(cli): add optional --threads parameter` (old commands still work)

❌ **Bug fixes that restore intended behavior:**

- Fixing incorrect Playwright selectors that broke
- Correcting download logic errors
- Example: `fix(collectors/video): correct quality selection logic` (fixing broken behavior)

❌ **Internal dependency updates (no API changes):**

- Updating packages that don't affect public API or CLI
- Minor/patch version bumps of dependencies
- Example: `build: update aiohttp from 3.11.6 to 3.11.7`

❌ **Performance improvements (same behavior):**

- Optimizing VSD binary calls or download algorithms
- Adding download progress caching
- Example: `perf(downloaders/video): optimize thread allocation` (faster, but same results)

**Breaking Change Examples for Codigo Facilito Downloader:**

```
feat(api)!: change AsyncFacilito context manager behavior

BREAKING CHANGE: AsyncFacilito now requires explicit browser initialization.
The previous auto-initialization has been removed for better resource control.

Before:
async with AsyncFacilito() as client:
    await client.download(url)

After:
async with AsyncFacilito() as client:
    await client.initialize_browser()
    await client.download(url)

Users must update their code to call initialize_browser() explicitly.
```

```
refactor!: rename Quality enum values

BREAKING CHANGE: Quality enum values have been renamed for consistency.
All references must be updated:

- Quality.MAX → Quality.HIGHEST
- Quality.MIN → Quality.LOWEST
- Quality.P1080 → Quality.FHD
- Quality.P720 → Quality.HD

CLI arguments remain unchanged (--quality max still works).
```

```
build!: upgrade to Python 3.12

BREAKING CHANGE: Project now requires Python 3.12+. Users must:
- Install Python 3.12 or higher
- Update Poetry environment: poetry env use python3.12
- Reinstall dependencies: poetry install

This change enables use of new type hint syntax and performance improvements.
```

```
feat(cli)!: remove deprecated set-cookies command

BREAKING CHANGE: Removed the set-cookies command. Use login command instead.

Migration path:
- Replace `facilito set-cookies cookies.json`
- With `facilito login` (browser-based authentication)
- Or use environment variables for cookie-based auth
```

```
fix(downloaders/video)!: correct VSD binary quality parameter format

BREAKING CHANGE: VSD binary quality parameter format has changed.
Previously accepted values like "1080" now require "1080p" suffix.

This fixes video quality selection but may affect custom scripts
that directly call the VSD binary with old format parameters.
```

```
feat(models)!: change Pydantic model field names

BREAKING CHANGE: Renamed fields in Course and Unit models for consistency:
- Course.course_name → Course.title
- Unit.unit_type → Unit.content_type
- Video.video_id → Video.id

API consumers must update field references when parsing models.
```

```
fix(auth)!: correct cookie normalization for sameSite attribute

BREAKING CHANGE: Cookie sameSite values are now strictly validated.
Invalid values will raise ValidationError instead of being silently ignored.

Users with malformed cookies must re-authenticate using `facilito login`.
```

**III. Commit Message Examples:**

**Documentation Changes (Always use `docs` type - NEVER `feat(docs)`, `refactor(docs)`, `fix(docs)`, or `chore(docs)`):**

```
docs: add installation guide
```

```
docs(readme): update Poetry installation steps
```

```
docs: create API usage examples
```

```
docs(contributing): add commit message guidelines
```

```
docs(changelog): add version 0.4.0 release notes
```

```
docs: fix typos in multiple files
```

```
docs(git-commit): update commit message instructions
```

**CRITICAL RULE**: NEVER use `feat(docs)`, `refactor(docs)`, `fix(docs)`, or `chore(docs)`. The correct pattern is:

- ✅ `docs: ...` or `docs(scope): ...` where scope is optional filename reference
- ❌ `feat(docs): ...` ← ABSOLUTELY FORBIDDEN
- ❌ `refactor(docs): ...` ← ABSOLUTELY FORBIDDEN
- ❌ `fix(docs): ...` ← ABSOLUTELY FORBIDDEN
- ❌ `chore(docs): ...` ← ABSOLUTELY FORBIDDEN

**Mixed Commits (Code + Documentation):**

```
feat(cli): add export command with documentation

Implemented new export command for saving course metadata to JSON.
Added command line options for format selection and output path.

Modified files (3):
- src/facilito/cli.py: Added export command
- src/facilito/models.py: Added export models
- README.md: Updated CLI documentation with export examples

Note: README changes are mentioned in body, not in type.
The primary change is code (feat), not documentation.
```

```
refactor(collectors): simplify selector logic

Extracted common Playwright selectors into shared utilities.
Improved code maintainability by reducing duplication.

Modified files (4):
- src/facilito/collectors/video.py: Use shared selectors
- src/facilito/collectors/course.py: Use shared selectors
- src/facilito/utils.py: Added selector helpers
- CONTRIBUTING.md: Updated development guidelines

Note: CONTRIBUTING.md changes are mentioned in body.
The primary change is refactoring code, not documentation.
```

**Mixed Commits (Documentation + Configuration):**

```
docs: update project documentation and tooling

Updated README with new installation steps and usage examples.
Also configured VSCode settings for consistent formatting.

Modified files (3):
- README.md: Updated installation and usage sections
- CONTRIBUTING.md: Added commit message examples
- .vscode/settings.json: Added Python formatting settings

Note: When mixing docs + config, docs takes priority (docs > config).
```

**SPECIFIC EXAMPLE: Commit message instructions + VSCode settings:**

❌ **INCORRECT (too simple, no body, wrong structure):**

```
Add GitHub Copilot chat commit message generation instructions to VSCode settings
```

✅ **CORRECT (follows all rules):**

```
docs: configure commit message generation for Copilot

Added reference to git-commit-messages-instructions.md in VSCode
settings to enable automatic commit message generation following
Conventional Commits specification for this project.

Modified files (2):
- .vscode/settings.json: Added Copilot instructions reference
- .github/git-commit-messages-instructions.md: Updated rules

This ensures GitHub Copilot generates consistent commit messages
that follow project conventions for Python/Playwright codebase.
```

**WHY THE FIRST IS WRONG:**

- ❌ No type or scope (violates Conventional Commits)
- ❌ No body (required for 2+ files)
- ❌ Too vague (doesn't explain WHY or impact)
- ❌ Past tense in title (should be imperative present)
- ❌ Doesn't list modified files

**WHY THE SECOND IS CORRECT:**

- ✅ Correct type: `docs` (documentation is primary over config)
- ✅ Optional scope added for clarity
- ✅ Body explains what was done and why
- ✅ Lists both modified files
- ✅ Imperative present tense in title
- ✅ Past tense in body
- ✅ Explains impact/benefit

**Configuration/Tooling Changes (Always use `chore` type):**

```
chore: update VSCode settings
```

```
chore: add .editorconfig
```

```
chore: update .gitignore to exclude .venv
```

```
chore: configure Ruff linter settings
```

```
chore: update pre-commit hooks configuration
```

**NOTE**: NEVER use `feat(settings)`, `refactor(config)`, `fix(vscode)` for configuration files. Always use `chore` for tooling/editor configurations.

**Simple Changes (No Body):**

```
feat(cli): add --format option to download command
```

```
fix(collectors/course): handle empty chapter lists
```

```
style: format code with ruff
```

**Complex Changes (With Body):**

```
feat(downloaders/bootcamp): add support for bootcamp downloads

Implemented bootcamp-specific collector and downloader to handle
multi-course bootcamp structures. Bootcamps are now downloaded with
nested directory structure: bootcamp/course/chapter/unit.

Modified files (4):
- src/facilito/collectors/bootcamp.py: Created new collector
- src/facilito/downloaders/bootcamp.py: Created new downloader
- src/facilito/utils.py: Added bootcamp URL detection
- src/facilito/cli.py: Added bootcamp command option
```

```
fix(auth): resolve session persistence across browser restarts

Fixed issue where authentication state was not properly saved between
CLI invocations. The problem was caused by incomplete Playwright
storage state serialization.

Changed session persistence to use explicit storage_state parameter
instead of relying on automatic session storage. This ensures cookies
and local storage are properly persisted to state.json.

Fixes #42
```

```
refactor(collectors): extract common selector logic

Extracted repeated Playwright selector patterns into shared utility
functions. This improves code maintainability and reduces duplication
across video, unit, and course collectors.

Modified files (5):
- src/facilito/collectors/video.py: Use shared selectors
- src/facilito/collectors/unit.py: Use shared selectors
- src/facilito/collectors/course.py: Use shared selectors
- src/facilito/utils.py: Added extract_element_text helper
- tests/test_collectors.py: Added selector utility tests
```

```
perf(downloaders/video): optimize concurrent download handling

Improved download performance by implementing adaptive thread pooling
based on available bandwidth. Downloads now start with fewer threads
and scale up if network capacity allows.

Performance impact:
- Average download time reduced by 35% on high-bandwidth connections
- Memory usage reduced by 20% through better chunk management
- No performance degradation on low-bandwidth connections
```

**IV. Python-Specific Guidelines:**

- **Docstrings and Comments in .py Files:**

  - **IMPORTANT**: Docstrings and inline comments are NOT `docs` type
  - Use the appropriate type based on what the CODE does, not the documentation change
  - **Adding docstrings to existing code without logic changes** → `refactor`
  - **Adding docstrings as part of new feature** → `feat`
  - **Fixing incorrect docstrings** → `fix` (only if the docstring was wrong about what code does)
  - **Improving/clarifying existing docstrings** → `refactor`
  - **Examples:**
    - ✅ `refactor(collectors): add docstrings to video collector methods`
    - ✅ `feat(api): add download_course method with comprehensive docstrings`
    - ✅ `refactor(utils): improve inline comments for clarity`
    - ❌ `docs(collectors): add docstrings` ← INCORRECT (not a standalone doc file)
    - ❌ `docs: update comments in utils.py` ← INCORRECT (not a standalone doc file)

- **Import Changes:**

  - Use `style` type for import reordering or formatting changes
  - Use `refactor` if imports change due to code restructuring
  - Example: `style: reorder imports per ruff configuration`

- **Type Hints:**

  - Use `refactor` when adding or improving type hints without logic changes
  - Use `feat` when adding type hints enables new runtime validation
  - Example: `refactor(models): improve type hints for Course model`

- **Pydantic Models:**

  - Use `feat` when adding new model fields or validators
  - Use `fix` when correcting validation logic
  - Use `refactor` when restructuring models without changing validation
  - Example: `fix(models): correct validator for video URL format`

- **Async/Await:**

  - Use `refactor` when converting sync to async without adding features
  - Use `perf` when async conversion specifically improves performance
  - Example: `refactor(downloaders): convert to async/await pattern`

- **Playwright Selectors:**

  - Use `fix` when updating selectors that broke due to site changes
  - Use `refactor` when improving selector reliability without external cause
  - Example: `fix(collectors/video): update selector for video URL extraction`

- **CLI Commands (Typer):**

  - Use `feat` when adding new commands or command options
  - Use `fix` when correcting command behavior or parameter handling
  - Example: `feat(cli): add --resume flag to download command`

- **Poetry Dependencies:**

  - Use `build` when adding, removing, or updating dependencies
  - Example: `build: add playwright-stealth dependency`
  - Example: `build: update aiohttp to 3.11.7`

- **Configuration Files (Editor/Tooling):**

  - **IMPORTANT**: Configuration files should use `chore`, NOT `feat` or `refactor`
  - Applies to: `.vscode/`, `.editorconfig`, `.gitignore`, IDE settings
  - **NOT `feat(settings)`** or **NOT `refactor(config)`** - use `chore`
  - Examples:
    - ✅ `chore: update VSCode settings for Python`
    - ✅ `chore: add .editorconfig for consistent formatting`
    - ✅ `chore: update .gitignore to exclude __pycache__`
    - ❌ `feat(vscode): add settings` ← INCORRECT
    - ❌ `refactor(config): update editor config` ← INCORRECT
  - **Exception**: Build tool configs like `pyproject.toml`, `ruff.toml` use `build`

- **Ruff/Mypy:**
  - Use `style` for formatting-only changes
  - Use `build` for configuration file changes (ruff.toml, mypy.ini)
  - Example: `style: format with ruff`
  - Example: `build: enable stricter mypy checks`

**V. Common Patterns:**

**When to Use `refactor` vs `feat`:**

- ❌ `feat(collectors): extract base collector class` → Use `refactor` (no new functionality)
- ✅ `refactor(collectors): extract base collector class` → Correct
- ❌ `refactor(cli): add new export command` → Use `feat` (new functionality)
- ✅ `feat(cli): add export command` → Correct

**When to Use `fix` vs `refactor`:**

- ✅ `fix(downloaders): handle network timeout errors` → Correct (fixing broken behavior)
- ✅ `refactor(downloaders): improve error handling structure` → Correct (improving code quality)

**When to Include Body:**

- ✅ Single file, obvious change → No body needed
- ✅ Multiple files (2-10) → List files with descriptions
- ✅ Complex change → Explain motivation and impact
- ✅ Breaking change → Always include migration guide

**Decision Tree for Breaking Changes:**

1. **Does it remove or rename public APIs (AsyncFacilito methods)?** → BREAKING CHANGE
2. **Does it change CLI command structure or arguments?** → BREAKING CHANGE
3. **Does it require users to modify their code or scripts?** → BREAKING CHANGE
4. **Does it change Pydantic model fields or validation?** → BREAKING CHANGE (if affects API consumers)
5. **Does it change configuration requirements (state.json, cookies)?** → BREAKING CHANGE
6. **Does it upgrade major Python version (3.10 → 3.11+)?** → BREAKING CHANGE
7. **Does it change authentication/session handling?** → BREAKING CHANGE (if breaks existing auth)
8. **Is it an internal refactor with no external impact?** → NOT breaking
9. **Does it add optional CLI flags without removing existing ones?** → NOT breaking
10. **Does it fix a bug to restore intended behavior?** → NOT breaking (usually)

**VI. Project-Specific Conventions:**

**File Organization:**

- Changes to `src/facilito/collectors/` → Use `collectors` or specific collector as scope
- Changes to `src/facilito/downloaders/` → Use `downloaders` or specific downloader as scope
- Changes to `src/facilito/cli.py` → Use `cli` as scope
- Changes to `src/facilito/async_api.py` → Use `api` as scope
- Changes to test files → Use `test` type with appropriate scope

**VSD Binary:**

- Use `chore` for VSD binary updates or downloads
- Use `feat` when adding VSD integration features
- Example: `chore: update VSD binary to v0.4.0`

**Playwright Updates:**

- Use `fix` when updating selectors due to site changes
- Use `build` when updating Playwright version
- Example: `fix(collectors/video): update selectors for new page layout`

**Session/State Management:**

- Use `fix` when correcting authentication issues
- Use `feat` when adding new authentication methods
- Example: `fix(auth): correct cookie sameSite normalization`

**Directory Structure:**

- Use `refactor` when changing output directory organization
- Use `feat` when adding new directory customization options
- Example: `refactor(downloaders/course): improve directory naming`

**VII. Quality Checklist:**

Before committing, ensure your commit message:

- ✅ Uses lowercase type (feat, fix, refactor, etc.)
- ✅ Includes scope when applicable (collectors, downloaders, cli, api)
- ✅ Starts description with imperative verb (add, fix, update, remove)
- ✅ Capitalizes first letter of description
- ✅ Limits description to ~50 characters
- ✅ Does not end description with period
- ✅ Includes body for multi-file or complex changes
- ✅ Lists modified files (2-10 files) in body
- ✅ Uses past tense in body ("Added", "Fixed", "Updated")
- ✅ Includes `BREAKING CHANGE:` footer when applicable
- ✅ References issues with `Fixes #N` or `Closes #N`
- ✅ Follows project's async/await, Playwright, and Poetry conventions

**VIII. More Detailed Examples:**

```
feat(collectors/bootcamp): add bootcamp metadata extraction

Implemented collector for bootcamp pages that extracts course lists,
descriptions, and enrollment information. Bootcamps contain multiple
courses with shared access requirements.

Modified files (3):
- src/facilito/collectors/bootcamp.py: Created new collector
- src/facilito/utils.py: Added is_bootcamp_url helper
- src/facilito/models.py: Added Bootcamp Pydantic model

Closes #15
```

```
refactor(downloaders): extract retry logic to decorator

Moved download retry logic from individual downloaders to a
shared @retry_on_failure decorator. This ensures consistent
retry behavior across all download operations.

Affected files (4):
- src/facilito/downloaders/video.py: Applied retry decorator
- src/facilito/downloaders/unit.py: Applied retry decorator
- src/facilito/downloaders/course.py: Applied retry decorator
- src/facilito/helpers.py: Added retry_on_failure decorator

This change maintains the same retry behavior while reducing
code duplication by ~150 lines.
```

```
perf(downloaders/video): optimize VSD binary thread allocation

Implemented adaptive thread pooling that adjusts based on network
performance. Initial tests showed 35% faster downloads on high-bandwidth
connections with no degradation on slower networks.

Modified files (2):
- src/facilito/downloaders/video.py: Added adaptive threading
- src/facilito/constants.py: Added bandwidth detection constants

Performance metrics:
- 1 Gbps: 5min → 3.25min (35% faster)
- 100 Mbps: 12min → 11.5min (4% faster)
- 10 Mbps: 45min → 45min (no change)

Refs: #89
```

```
feat(cli): implement comprehensive download management

Added search, filtering, and progress tracking capabilities for
downloads including pause/resume, speed monitoring, and ETA display.

This change spans multiple modules (10 files modified):
- CLI layer: New commands and options
- Downloaders: Progress callback support
- Models: Download state tracking
- Utils: Speed calculation and formatting

Key changes:
- Created DownloadProgress model with state tracking
- Implemented pause/resume with state persistence
- Added real-time speed monitoring (KB/s, MB/s)
- Created `facilito list` command for active downloads
- Added ETA calculation based on current speed

Performance: Progress updates every 500ms without blocking downloads.

Closes #45, #67, #89
```

```
refactor(collectors): add comprehensive docstrings

Added detailed docstrings to all collector classes and methods
for better code maintainability. Documented expected parameters,
return types, and potential exceptions.

Modified files (3):
- src/facilito/collectors/course.py: Added class and method docstrings
- src/facilito/collectors/video.py: Added class and method docstrings
- src/facilito/collectors/unit.py: Added class and method docstrings

Note: This is a refactor (not docs) because we're improving code
documentation within .py files, not standalone documentation files.
```

```
docs: update installation and usage documentation

Updated project documentation to reflect Poetry installation method
and new CLI commands. Added troubleshooting section with common
authentication and download issues.

Modified files (4):
- README.md: Updated installation instructions
- CONTRIBUTING.md: Added commit message examples
- .github/copilot-instructions.md: Updated project patterns
- .github/git-commit-messages-instructions.md: Python examples

Note: This is docs because we're modifying standalone .md files,
not code comments or docstrings within .py files.
```

```
fix(collectors/video): handle missing video quality options

Fixed crash when video page doesn't provide all quality options.
Now gracefully falls back to available qualities instead of raising
exception when preferred quality is unavailable.

Modified files (2):
- src/facilito/collectors/video.py: Added quality fallback
- src/facilito/errors.py: Added QualityUnavailableError

The collector now tries qualities in descending order:
1080p → 720p → 480p → 360p → lowest available

Fixes #103
```

```
build: update Playwright to 1.40.0 and Python to 3.11

Updated Playwright for improved selector stability and migrated
to Python 3.11 for better async performance. All dependencies
updated to compatible versions.

Modified files (3):
- pyproject.toml: Updated Python and dependencies
- poetry.lock: Regenerated lock file
- README.md: Updated Python version requirement

Breaking changes: None (backward compatible)
Performance: ~10% faster async operations in Python 3.11
```

**IX. Anti-Patterns (What NOT to Do):**

❌ **CRITICAL ERROR: Using feat(docs), refactor(docs), fix(docs), or chore(docs) - ABSOLUTELY FORBIDDEN:**

```
feat(docs): add new documentation file
refactor(docs): update README
fix(docs): correct typo in CONTRIBUTING
chore(docs): update documentation
feat(docs): add API documentation
refactor(docs): reorganize documentation structure
```

✅ **CORRECT: Always use `docs` type for .md files:**

```
docs: add installation guide
docs(readme): update installation instructions
docs(contributing): correct commit message examples
docs: fix typo in usage section
docs: add API documentation
docs: reorganize documentation structure
```

**WHY THIS IS CRITICAL**: `docs` is the TYPE that describes WHAT changed (documentation files), not a scope. The scope (in parentheses) describes WHERE (which file). Using `feat(docs)` is like saying "add new (documentation)" which mixes concepts. The correct pattern is `docs` (type) + optional `(filename)` (scope).

❌ **Wrong pattern for mixed commits (code + docs):**

```
feat(docs): add README and new feature
refactor(docs): update code and documentation
```

✅ **Correct pattern (use code type, mention docs in body):**

```
feat(cli): add export command

Implemented new export command for saving course metadata.
Also updated README with usage examples.

Modified files (2):
- src/facilito/cli.py: Added export command
- README.md: Added export command documentation
```

❌ **Vague descriptions:**

```
fix: fixed bug
feat: added stuff
refactor: code improvements
```

✅ **Specific descriptions:**

```
fix(collectors/video): handle missing quality options
feat(cli): add pause/resume support for downloads
refactor(downloaders): extract retry logic to decorator
```

❌ **Missing scope for specific changes:**

```
fix: update selector
feat: add new command
```

✅ **With proper scope:**

```
fix(collectors/video): update video URL selector
feat(cli): add list command for active downloads
```

❌ **Past tense in description:**

```
feat(cli): added export command
fix(auth): fixed cookie issue
```

✅ **Imperative present tense:**

```
feat(cli): add export command
fix(auth): correct cookie normalization
```

❌ **Wrong type for configuration files:**

```
feat(settings): add VSCode settings
refactor(config): update editor configuration
fix(vscode): correct launch.json
```

✅ **Correct type (use `chore`):**

```
chore: add VSCode settings
chore: update .editorconfig
chore: correct launch.json configuration
```

❌ **Missing body for multi-file changes (CRITICAL ERROR):**

```
refactor: improve download handling
```

```
Add GitHub Copilot instructions to settings
```

```
Update documentation and configuration
```

✅ **With proper structure, type, scope, and body:**

```
refactor(downloaders): extract retry logic to decorator

Moved download retry logic from individual downloaders to a
shared decorator for consistent retry behavior across all
download operations.

Affected files (4):
- src/facilito/downloaders/video.py: Applied decorator
- src/facilito/downloaders/unit.py: Applied decorator
- src/facilito/downloaders/course.py: Applied decorator
- src/facilito/helpers.py: Added retry_on_failure decorator
```

```
docs: configure commit message generation for Copilot

Added reference to git-commit-messages-instructions.md in VSCode
settings to enable automatic commit message generation following
Conventional Commits specification.

Modified files (2):
- .vscode/settings.json: Added Copilot instructions reference
- .github/git-commit-messages-instructions.md: Updated rules
```

**WHY SIMPLE MESSAGES ARE WRONG:**

- They violate Conventional Commits specification (no type)
- They don't provide context (no body with file list)
- They're too vague (what specifically changed?)
- They don't explain WHY (motivation is missing)
- They're not useful for changelog generation
- They fail code review standards
- src/facilito/downloaders/video.py: Applied decorator
- src/facilito/downloaders/unit.py: Applied decorator
- src/facilito/downloaders/course.py: Applied decorator
- src/facilito/helpers.py: Added retry_on_failure decorator

```

**X. Summary:**

This guide ensures all commits follow Conventional Commits specification
adapted for the Codigo Facilito Downloader Python project. Key points:

1. Use correct type (feat, fix, refactor, perf, docs, style, test, build, ci, chore)
2. Include scope when applicable (collectors, downloaders, cli, api, auth, models)
3. Write concise descriptions in imperative present tense
4. Add body for multi-file or complex changes
5. List modified files (2-10 files) with brief descriptions
6. Mark breaking changes with `!` or `BREAKING CHANGE:` footer
7. Reference issues with `Fixes #N` or `Closes #N`
8. Follow Python/Playwright/Poetry project conventions

For questions or clarification, refer to:

- [Conventional Commits](https://www.conventionalcommits.org/)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [copilot-instructions.md](.github/copilot-instructions.md)

```

**Cross-Layer Examples:**

- `feat: add content safety middleware with 4-layer protection`
- `fix: resolve thread management in AI agent service`
- `refactor: standardize error handling across all layers`

**Handling Commits with Multiple Change Types:**

- "Each commit should be as atomic as possible, addressing a single concern. A single commit must only have one type."
- "If a commit includes multiple types of changes (e.g., a new feature and a refactor), choose the type that represents the primary purpose of the commit. The hierarchy is generally `feat` > `fix` > `perf` > `refactor`."
- "**Example**: If you add a new feature and also refactor some old code in the same file, the commit type must be `feat`."
  - `feat(Application.Functions): add update task priority tool` (even if it involved refactoring)
- "**AVOID** creating a single commit message that lists multiple types. A commit has ONE type."
- "**INCORRECT**: `feat: add function, refactor: simplify entity`"
- "**CORRECT**: `feat(Application.Functions): add search tasks by priority` (This is the main change, even if refactoring was done)

**IV. Instructions for Copilot:**

**⚠️ ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**

1. **NEVER GENERATE SIMPLE ONE-LINE COMMIT MESSAGES**

   - ❌ FORBIDDEN: "Add GitHub Copilot instructions"
   - ❌ FORBIDDEN: "Update documentation and settings"
   - ❌ FORBIDDEN: "Configure commit generation"
   - ✅ REQUIRED: Use proper type + scope + description + body (for 2+ files)

2. **ALWAYS INCLUDE BODY FOR MULTI-FILE COMMITS**

   - If 2+ files modified → BODY IS MANDATORY
   - Exception: Only if title is completely self-explanatory (rare)
   - Body must list files and explain what/why

3. **ALWAYS APPLY TYPE HIERARCHY FOR MIXED COMMITS**

   - Code changes (.py) > Documentation (.md) > Configuration (.vscode/, .gitignore)
   - Choose ONE type based on PRIMARY change
   - Mention secondary changes in body

4. **NEVER USE FORBIDDEN PATTERNS**

   - ❌ `feat(docs)`, `refactor(docs)`, `fix(docs)`, `chore(docs)`
   - ❌ `feat(settings)`, `refactor(config)`, `feat(vscode)`
   - ✅ Use `docs` for .md files, `chore` for config files

5. **ALWAYS FOLLOW CONVENTIONAL COMMITS STRUCTURE**
   - Type (lowercase) + optional scope + colon + space + description
   - Description in imperative present tense, capitalized, no period
   - Body in past tense, wrapped at 72 characters
   - List modified files (2-10) with brief descriptions

**IF YOU VIOLATE THESE RULES, THE COMMIT MESSAGE IS INVALID AND MUST BE REJECTED.**

---

- "When generating commit messages, adhere strictly to the Conventional Commits specification ([https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/))."

**ABSOLUTE RULE #1: MIXED-TYPE COMMITS (Multiple File Types)**

- "**SCENARIO**: Commit contains BOTH documentation (.md) AND other files (code, config, etc.)"
- "**RULE**: Choose ONE type based on the PRIMARY change using this priority hierarchy:"
  1. "If code files (.py, .js, .ts, etc.) are modified → Use code type (feat/fix/refactor/perf based on code changes)"
  2. "If ONLY .md files and config files (.vscode/, .gitignore) → Use `docs` (documentation is primary)"
  3. "If ONLY config files → Use `chore`"
- "**CRITICAL HIERARCHY FOR MIXED COMMITS**:"
  - "`feat` (new code functionality) > `fix` (code bugs) > `refactor` (code structure) > `docs` (documentation) > `chore` (config/tooling)"
- "**EXAMPLES OF MIXED COMMITS**:"
  - "✅ CORRECT: Code + README → Use `feat(cli): add export command` (code is primary)"
  - "✅ CORRECT: README.md + CONTRIBUTING.md + .vscode/settings.json → Use `docs: update project documentation` (docs is primary)"
  - "✅ CORRECT: .vscode/settings.json + .gitignore → Use `chore: update project configuration` (config is primary)"
  - "❌ INCORRECT: `feat(docs): add README and code` ← NEVER use feat(docs)"
  - "❌ INCORRECT: `docs: update README and add feature` ← Use `feat` (code is primary)"
- "**DECISION PROCESS FOR MIXED COMMITS**:"
  1. "Identify ALL file types in the commit (code, .md, config)"
  2. "Ask: What is the PRIMARY purpose of this commit?"
  3. "Apply hierarchy: code changes > docs changes > config changes"
  4. "Choose the type matching the PRIMARY change"
  5. "Mention other changes in commit body, not in type"

**ABSOLUTE RULE #2: DOCUMENTATION-ONLY COMMITS**

- "**CRITICAL**: Distinguish carefully between `feat` and `refactor`:"
  - "Use `feat` ONLY when adding NEW functionality or capabilities"
  - "Use `refactor` when improving existing code structure without changing behavior"
  - "If restructuring code for better architecture = `refactor`"
  - "If adding new business logic or endpoints = `feat`"
- "**CRITICAL FOR DOCUMENTATION FILES**: When .md files or documentation are modified OR created, use `docs` type ONLY. NEVER combine with other types. Examples:"
  - "✅ CORRECT: `docs: add installation guide`"
  - "✅ CORRECT: `docs(readme): update setup steps`"
  - "✅ CORRECT: `docs: create contributing guidelines`"
  - "✅ CORRECT: `docs(api): update API documentation`"
  - "❌ INCORRECT: `feat(docs): add new documentation file` ← NEVER EVER use feat(docs)"
  - "❌ INCORRECT: `refactor(docs): update README` ← NEVER EVER use refactor(docs)"
  - "❌ INCORRECT: `fix(docs): correct typo` ← NEVER EVER use fix(docs)"
  - "❌ INCORRECT: `chore(docs): update documentation` ← NEVER EVER use chore(docs)"
  - "**ABSOLUTE RULE**: Documentation changes = `docs` type ALWAYS. NEVER `feat(docs)`, `refactor(docs)`, `fix(docs)`, or `chore(docs)`. Scope is optional (e.g., `docs(readme)` or `docs`)."
  - "**WHY NO feat(docs)?**: Because `docs` IS the type, NOT a scope. The type describes WHAT changed (documentation), not WHERE (that's the scope)."
  - "**CORRECT PATTERN**: `docs` type + optional file scope → `docs(readme): ...` or just `docs: ...`"
  - "**FORBIDDEN PATTERN**: ANY other type + docs scope → `feat(docs)`, `refactor(docs)`, etc. ← NEVER DO THIS"
- "**STRONGLY RECOMMENDED to include a scope** for code changes using the project hierarchy"
- "For Codigo Facilito Downloader project, common scopes include:"
  - "`cli`, `api`, `collectors`, `downloaders`, `auth`, `models`, `utils`, `helpers`, `logger`"
  - "`collectors/video`, `collectors/course`, `downloaders/video`, `downloaders/course`"
  - "`course`, `video`, `unit`, `bootcamp`, `playlist`"
- "For documentation changes, scope can reference the file name (e.g., `docs(readme):`) or be omitted (e.g., `docs:`)"
- "Write descriptions in imperative, present tense with capital first letter"
- "Limit header to 50 characters, body lines to 72 characters"
- "**INCLUDE BODY when:**"
  - "Multiple files are modified (unless title is completely self-explanatory)"
  - "Complex changes that need explanation"
  - "Explaining WHY (motivation) not just WHAT"
  - "**ALWAYS include body when marking BREAKING CHANGE** to explain impact and migration path"
- "**OMIT BODY when:**"
  - "Single file, simple change"
  - "Title is completely self-explanatory"
  - "Trivial updates (e.g., 'docs: fix typo')"
- "**BODY WRITING STYLE - CRITICAL:**"
  - "**Header (title)**: Use IMPERATIVE PRESENT tense (e.g., 'add feature', 'fix bug', 'update config')"
  - "**Body**: Use PAST TENSE (e.g., 'Added feature', 'Fixed bug', 'Updated config')"
  - "Body describes what WAS done, header describes what the commit DOES"
  - "Use `-` (hyphen) for bullet points in body, NEVER `•` or other symbols"
  - "File listings format:"
    - "2-10 files: List each file with hyphen. Example: `- FileName.cs: Added method`"
    - ">10 files: Group by layer/component, don't list all files individually"
  - "Example for many files:"
    - "❌ DON'T: List all 15 files individually (too verbose)"
    - "✅ DO: 'This change spans multiple layers (15 files modified):'"
    - "Then describe by component: 'Application layer: New DTOs and services'"
  - "Wrap lines at 72 characters for readability"
- "**BREAKING CHANGES - Critical Decision Guide:**"
  - "Use `BREAKING CHANGE:` footer or `!` suffix when consumers MUST modify their code"
  - "**Ask yourself**: Would existing code that uses this API/endpoint/interface still work?"
  - "**If NO** (requires consumer changes) → BREAKING CHANGE"
  - "**If YES** (backward compatible) → NOT breaking"
  - "Common breaking changes:"
    - "Removing/renaming public APIs, methods, properties, endpoints"
    - "Changing HTTP response structures (removing/renaming fields)"
    - "Changing method signatures (parameters, return types)"
    - "Major framework upgrades (.NET 9 → .NET 10)"
    - "Removing/renaming configuration keys in appsettings.json"
    - "Changing database schema (removing columns, changing types)"
    - "Changing authentication/authorization requirements"
  - "NOT breaking changes:"
    - "Internal refactoring (private methods, file organization)"
    - "Adding optional parameters with defaults"
    - "Adding new methods/endpoints (keeping existing ones)"
    - "Performance improvements (same behavior/output)"
    - "Bug fixes restoring intended behavior"
    - "Minor dependency updates without API changes"
  - "**Format**: Use `type(scope)!: description` OR add footer `BREAKING CHANGE: explanation`"
  - "**Body REQUIRED**: Explain what breaks, why, and how to migrate"
- "Use footer for breaking changes (`BREAKING CHANGE: ` or `!` in header) and issue references (`Closes #123`)"
- "When in doubt between types, prefer the more specific type (e.g., `perf` over `refactor` for performance improvements)"

**V. TaskAgent Project Specific Guidelines:**

**Common Scenarios and Correct Types:**

1. **Adding new functionality (`feat`):**

   - New AI agent function tools (TaskFunctions methods)
   - New API endpoints or controllers (ChatController, TaskController)
   - New business logic or domain entities (TaskItem methods, new entities)
   - New content safety features or middleware layers
   - New validation rules or business rules in Domain
   - New middleware components (rate limiting, logging)
   - New Entity Framework migrations with new features

2. **Code improvements without new features (`refactor`):**

   - Extracting helper functions or classes for better organization
   - Adding or improving docstrings in Python code (.py files)
   - Adding or improving inline comments in Python code
   - Applying design patterns (Repository, Factory, Strategy)
   - Converting synchronous to asynchronous without adding functionality
   - Simplifying error handling while maintaining same behavior
   - Reorganizing folder structure or file imports
   - Renaming variables/functions for clarity
   - Consolidating duplicate code
   - Improving type hints without changing logic

3. **Performance improvements (`perf`):**

   - Optimizing Playwright selector queries or page navigation
   - Implementing parallel downloads or async batching
   - Adding download progress caching
   - Optimizing VSD binary calls or thread allocation
   - Reducing memory allocations
   - Optimizing thread dictionary management
   - Improving content safety API call efficiency

4. **Bug fixes (`fix`):**
   - Correcting TaskItem business logic (status transitions)
   - Fixing AI agent function tool errors or incorrect responses
   - Resolving content safety false positives
   - Fixing task validation problems (title length, priority values)
   - Correcting DI configuration issues in Program.cs
   - Fixing null reference exceptions in TaskFunctions
   - Resolving Entity Framework enum conversion issues

**Scope Naming Conventions for this Project:**

- **Project Level**: `Domain`, `Application`, `Infrastructure`, `WebApp`
- **Layer/Folder Level**: `Application.Functions`, `Application.DTOs`, `Application.Interfaces`, `Infrastructure.Data`, `Infrastructure.Services`, `WebApp.Middleware`, `WebApp.Controllers`
- **Feature Level**: `ai-agent`, `task-management`, `content-safety`, `database`, `chat`
- **Component Level**: `middleware`, `controllers`, `repositories`, `function-tools`, `entities`

**Decision Tree for Commit Types:**

**STEP 0: MULTIPLE FILE TYPES CHECK (Mixed Commits)**

- "**If commit contains MULTIPLE file types** (code + docs, docs + config, code + config):"
  - "Apply priority hierarchy: code changes > docs changes > config changes"
  - "Choose ONE type based on PRIMARY change"
  - "Examples:"
    - "Code (.py) + README.md → Use code type (feat/fix/refactor), mention docs in body"
    - "README.md + .vscode/settings.json → Use `docs` (docs is primary over config)"
    - ".vscode/ + .gitignore only → Use `chore` (config only)"
  - "**NEVER**: `feat(docs)` or `refactor(docs)` even in mixed commits"
  - "**RULE**: Mention secondary changes in commit body, not in type"

**STEP 1-11: SINGLE FILE TYPE CHECKS**

1. **Does it modify OR create standalone .md/.rst/.txt documentation files ONLY (not .py files)?** → `docs` (NEVER `feat(docs)`, `refactor(docs)`, `fix(docs)`, or `chore(docs)`)
   - ✅ README.md, CONTRIBUTING.md, CHANGELOG.md → `docs`
   - ✅ git-commit-messages-instructions.md → `docs`
   - ✅ Multiple .md files only → `docs`
   - ❌ Docstrings in .py files → NOT `docs` (use refactor/feat/fix based on code)
   - ❌ Comments in .py files → NOT `docs` (use refactor/feat/fix based on code)
   - ❌ NEVER EVER use `feat(docs)`, `refactor(docs)`, `fix(docs)`, or `chore(docs)`
   - **CRITICAL**: `docs` is the TYPE, not a scope. Use `docs` or `docs(filename)`, NEVER `othertype(docs)`
2. **Does it modify editor/tooling config files (.vscode/, .editorconfig, .gitignore)?** → `chore` (NEVER `feat(settings)` or `refactor(config)`)
   - ✅ .vscode/settings.json → `chore`
   - ✅ .editorconfig → `chore`
   - ✅ .gitignore → `chore`
   - ❌ pyproject.toml, ruff.toml → NOT `chore` (use `build`)
3. **Does it add new user-facing functionality?** → `feat`
4. **Does it fix broken functionality?** → `fix`
5. **Does it improve performance measurably?** → `perf`
6. **Does it change code structure without changing behavior (including adding docstrings/comments to .py files)?** → `refactor`
7. **Does it add/modify tests only?** → `test`
8. **Does it change CI/CD configuration?** → `ci`
9. **Does it change build system or dependencies?** → `build`
10. **Does it revert a previous commit?** → `revert`
11. **Everything else** → `chore`

**IMPORTANT NOTES**:

- **STEP 0 (Mixed Commits)**: Check FIRST if commit has multiple file types, apply hierarchy
- **Question #1**: Is the FIRST check for single-type commits and applies ONLY to standalone documentation files (.md, .rst, .txt)
- **Question #2**: Checks for editor/tooling configs - these are ALWAYS `chore`
- Docstrings and comments in .py files are NOT `docs` - they follow the code type (refactor/feat/fix)
- Configuration files like .vscode/ are NOT `feat` or `refactor` - they are `chore`
- **FORBIDDEN PATTERNS**: `feat(docs)`, `refactor(docs)`, `fix(docs)`, `chore(docs)` ← NEVER USE
- **CORRECT PATTERNS**: `docs`, `docs(readme)`, `docs(contributing)` ← ALWAYS USE for .md files
- Examples:
  - ✅ Modifying README.md only → `docs` or `docs(readme)`
  - ✅ Modifying git-commit-messages-instructions.md only → `docs` or `docs(git-commit)`
  - ✅ Adding .vscode/settings.json → `chore`
  - ✅ Code + README → `feat(cli): ...` (mention docs in body)
  - ✅ README + .vscode/ → `docs: ...` (docs primary over config)
  - ✅ Adding docstrings to existing functions → `refactor`
  - ✅ Adding docstrings to new feature → `feat`
  - ❌ Adding docstrings → NOT `docs`
  - ❌ VSCode settings → NOT `feat(settings)`
  - ❌ Modifying README → NOT `feat(docs)` ← ABSOLUTELY FORBIDDEN
  - ❌ Updating docs → NOT `refactor(docs)` ← ABSOLUTELY FORBIDDEN

**Multi-File Changes - Body Guidelines:**

- **Include body if:**
  - 2+ files modified (describe changes and list files if ≤10)
  - Change spans multiple layers or scopes
  - Explanation needed for WHY (not just WHAT)
  - Breaking changes or migrations involved
- **Body can be omitted if:**
  - Single file, straightforward change
  - Title like "docs: fix typo in README" is self-explanatory
  - Trivial formatting or style changes

**File Listing Best Practices:**

- **2-10 files modified:**
  - Include section: "Modified files (X):" or "Affected files (X):"
  - List each file with hyphen and brief description
  - Example: `- TaskService.cs: Added search method`
  - Use past tense for descriptions
- **>10 files modified:**
  - DON'T list all files individually (commit becomes too long)
  - State total count: "This change spans multiple layers (15 files modified):"
  - Group changes by layer/component/category
  - Example: "Application layer: New DTOs, interfaces, and service methods"
  - Example: "Infrastructure layer: Repository implementations and queries"
  - Focus on WHAT changed in each component, not listing every file
- **1 file modified:**
  - Generally omit file listing (obvious from commit diff)
  - Use body to explain WHY and HOW, not WHAT file

**Body Writing Style:**

- Header (title): Imperative present ("add feature", "fix bug")
- Body: Past tense ("Added feature", "Implemented logic", "Fixed validation")
- Bullet points: Use `-` (hyphen), not `•` or other symbols
- Line length: Wrap at 72 characters
- Paragraphs: Separate with blank lines for readability

---

## 🚨 COMMON COPILOT ERRORS TO AVOID

**ERROR #1: Generating Simple Messages for Multi-File Commits**

❌ **WRONG (what Copilot might generate):**

```
Add GitHub Copilot chat commit message generation instructions to VSCode settings
```

```
Update commit message instructions and settings
```

```
Configure Copilot instructions
```

✅ **CORRECT (what Copilot MUST generate):**

```
docs: configure commit message generation for Copilot

Added reference to git-commit-messages-instructions.md in VSCode
settings to enable automatic commit message generation following
Conventional Commits specification for this project.

Modified files (2):
- .vscode/settings.json: Added Copilot instructions reference
- .github/git-commit-messages-instructions.md: Updated rules

This ensures consistent commit messages for Python/Playwright codebase.
```

**WHY ERROR #1 IS CRITICAL:**

- Missing type (violates Conventional Commits)
- Missing body (required for 2+ files)
- Too generic (doesn't explain what or why)
- Not useful for changelog or code review
- **⚠️ Being .md files does NOT exempt from body requirement**

---

**ERROR #1b: Assuming .md Files Can Have Simple Messages**

❌ **WRONG ASSUMPTION:**

"It's just documentation files (.md), so a simple message is OK"

✅ **CORRECT UNDERSTANDING:**

"Even if ALL files are .md, I MUST include body for 2+ files with proper structure"

**EXAMPLE:**

❌ WRONG: `docs: update documentation`
✅ CORRECT:

```
docs: update installation and contribution guides

Updated installation steps to reflect Poetry usage and added
comprehensive commit message examples for contributors.

Modified files (2):
- README.md: Updated installation section
- CONTRIBUTING.md: Added commit message guidelines
```

---

**ERROR #2: Using feat(docs) or Similar Forbidden Patterns**

❌ **WRONG:**

```
feat(docs): update commit message instructions
refactor(docs): improve documentation structure
```

✅ **CORRECT:**

```
docs: update commit message instructions
docs: improve documentation structure
```

---

**ERROR #3: Missing File List in Body**

❌ **WRONG:**

```
docs: update documentation

Updated various documentation files.
```

✅ **CORRECT:**

```
docs: update documentation

Updated installation and contribution guidelines.

Modified files (3):
- README.md: Updated installation steps
- CONTRIBUTING.md: Added commit message examples
- .github/git-commit-messages-instructions.md: Added rules
```

---

**ERROR #4: Wrong Type Priority for Mixed Commits**

❌ **WRONG (using docs when code is primary):**

```
docs: add README and new feature
```

✅ **CORRECT (use code type, mention docs in body):**

```
feat(cli): add export command

Implemented export functionality.
Also updated README with usage examples.

Modified files (2):
- src/facilito/cli.py: Added export command
- README.md: Added export documentation
```

---

**COPILOT SELF-CHECK BEFORE GENERATING:**

1. ✅ Does message have proper type (feat/fix/refactor/docs/chore)?
2. ✅ Does message have scope when applicable?
3. ✅ Is description in imperative present tense?
4. ✅ Is body included for 2+ files?
5. ✅ Are files listed with descriptions?
6. ✅ Did I avoid forbidden patterns (feat(docs), etc.)?
7. ✅ Is the type hierarchy correct for mixed commits?

**IF ANY CHECK FAILS → REGENERATE THE MESSAGE**

---

```

```
