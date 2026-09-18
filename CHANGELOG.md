# CHANGELOG

## v0.6.0 (2026-09-18)

### Chore

* chore: ignore .kilo/

.kilo/ holds local Kilo specs and worktree metadata that should not be
tracked.

- .gitignore: Added .kilo/ ([`a4ac5bb`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a4ac5bbd5b123d155a3af61e3652a618de9c5a39))

* chore(video): log the resolved playlist URL

vsd failures said &#34;no playlists were found in website source.&#34; without
showing which URL was used, making it impossible to tell a captured
signed playlist from the broken static fallback.

- src/facilito/collectors/video.py: Log the redacted playlist URL and
  whether it came from the network, page source or the static fallback
- src/facilito/downloaders/video.py: Log the redacted URL passed to vsd
- src/tests/test_ratelimit.py: Added a test asserting the static
  fallback is used and warned about when no playlist is captured ([`698eca5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/698eca5847a08066c74d4b3844b6587cd7034a4b))

* chore(ci): remove ffmpeg and playwright install steps

Remove FFmpeg and Playwright browser installation as they are no longer
required. ([`133cff7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/133cff7365079953427205a599e14f34e3916678))

### Documentation

* docs(state): document resume and failures

Documented the per-course manifest and the resume/failure flags so
users know a completed course is skipped and failures are retried.

- README.md: Added a Reanudar y fallos section with manifest location,
  completed skip, automatic failure retry, --retry-failed, --status and
  --override interplay ([`c4b113f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c4b113f3de632c6702b69c39f1d0c14c7b939941))

* docs(youtube): document embedded video support

Documented automatic detection and the yt-dlp download path so users
know embedded lessons are handled and how quality maps.

- README.md: Added a YouTube subsection covering detection, the yt-dlp
  dependency, quality mapping, limits (no playlists/subtitles) and
  clear failures for private/removed videos ([`87a47cb`](https://github.com/ivansaul/codigo_facilito_downloader/commit/87a47cb7426537cd22e3b68d8e79294cb25d746f))

* docs(ratelimit): add recommended example config file

Added a ready-to-use example config so users can opt into the
recommended pacing without hand-writing JSON, and documented how to
copy or point to it.

- config.example.json: Added the recommended rate-limiting settings
  (0.3/0.3/1.5 pacing, retries and block detection enabled)
- .gitignore: Un-ignored config.example.json so the example ships
- README.md: Documented copying the example to Facilito/config.json or
  passing it via --config ([`9ae8c8a`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9ae8c8adb5c6d126122081a386b940e415f65481))

* docs(ratelimit): add recommended command example

Added a recommended, efficient rate-limiting command with a rationale
table and a conservative fallback for when 429/403 responses appear,
and aligned the sample config with the recommended values.

- README.md: Added the Configuración recomendada subsection with a
  ready-to-use command, a values table, a throttled fallback and an
  opt-out example; aligned Facilito/config.json sample values ([`962de87`](https://github.com/ivansaul/codigo_facilito_downloader/commit/962de87c60cfae06969bfd3350b937f76f93ead1))

* docs(ratelimit): link options from download usage

The download usage list only listed --quality, --override and --threads,
so the new rate-limiting options were easy to miss even though the Rate
limiting section documented them.

- README.md: Added a bullet listing the rate-limiting options and
  linking to the Rate limiting section from the download usage options ([`fbf5379`](https://github.com/ivansaul/codigo_facilito_downloader/commit/fbf5379ca67ccc329ea9ccbe520efb985baa9f6e))

* docs(ratelimit): document options and config file

Documented the new rate-limiting surface and the config file so users
can opt into pacing and understand the abort policy.

- README.md: Added a Rate limiting section with the ten new options and
  their defaults, the Facilito/config.json path and format, CLI &gt; file &gt;
  default precedence, FACILITO_CONFIG override, sample config and polite
  vs opt-out examples; noted the abort-on-exhaustion policy and the
  --threads caveat

This is a minor, non-breaking version bump (0.5.0 -&gt; 0.6.0). ([`f137713`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f137713ee1686fe92199d02089c61375c50279e3))

### Feature

* feat(state): show the last attempt time in --status

A stored failure reason can be stale after a fix, which made --status
look like it was still failing. Include the attempt timestamp so it is
clear the reason is historical.

- src/facilito/async_api.py: --status now prints &#34;(last attempt &lt;time&gt;)&#34;
  for each pending failure ([`8f76ff7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/8f76ff75626578c4e6ad33052db4befcb5e7a72e))

* feat(state): add status and retry-failed flags

Exposed the resume state on the download command so users can inspect
progress and retry only failures.

- src/facilito/cli.py: Added --status and --retry-failed, rejected
  --retry-failed with --override, and forwarded both to the downloader
- src/tests/test_state.py: Added forwarding, mutual-exclusion and help
  tests ([`52988bc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/52988bc99f844cfd76d146d7e4c1a380719d3498))

* feat(state): orchestrate resume and retries

The run entry point now loads the manifest and decides between showing
state, retrying failures only, skipping a completed course, or resuming.

- src/facilito/async_api.py: download accepts status_only/retry_failed,
  skips a completed course with outputs present, resumes with the state,
  retries recorded failures without traversal and reports status
- src/tests/test_state.py: Added completed-skip, retry-only, status and
  no-failures tests
- src/tests/test_ratelimit.py: Async tests now provide a course slug and
  isolate the manifest directory ([`14dd562`](https://github.com/ivansaul/codigo_facilito_downloader/commit/14dd562a00e16cbb8c9d99581e60dc25587c2e1c))

* feat(state): resume and record course progress

Course and bootcamp loops now consult the manifest: units recorded ok
with an existing file are skipped without fetching their page, and every
outcome is persisted as the run advances.

- src/facilito/downloaders/course.py, bootcamp.py: Accept the run state,
  skip ok units, record outcomes and save per unit, and record the
  failure that caused an AbortError before re-raising
- src/tests/test_state.py: Added skip, record and abort tests for course
  and bootcamp ([`48b87cf`](https://github.com/ivansaul/codigo_facilito_downloader/commit/48b87cfbc487c519fe9301fdd8211b505b743088))

* feat(state): return download outcomes

Downloaders now report success or a failure reason so the course loops
can persist failures and resume.

- src/facilito/downloaders/video.py: download_video returns
  UnitOutcome for success, skip and non-abort failures; AbortError still
  propagates
- src/facilito/downloaders/youtube.py: Same for the yt-dlp path
- src/facilito/downloaders/unit.py: download_unit returns the outcome
  (page provider for lectures) and maps a missing ffmpeg
- src/tests/test_state.py: Added outcome tests for both downloaders and
  unit dispatch ([`53cbc12`](https://github.com/ivansaul/codigo_facilito_downloader/commit/53cbc12c585989c9a5eaff5933e8d9cb81714f39))

* feat(state): add run manifest

Added the per-course manifest that records unit outcomes so runs can be
resumed and failures retried without re-walking everything.

- src/facilito/state.py: Added RunState/UnitState, atomic save_state,
  load_state (corruption tolerant), find_state by normalized URL and
  state_path
- src/facilito/constants.py: Added STATE_FILE_NAME and STATE_VERSION
- src/tests/test_state.py: Added record/queries, roundtrip, corruption
  and find_state tests ([`1420845`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1420845888b679b9b66e4436a4706506161400b9))

* feat(state): add unit outcome model

Downloaders need to report whether a unit succeeded and why, so the
resume manifest can record results and failures.

- src/facilito/models.py: Added UnitOutcome(success, error, provider)
- src/tests/test_state.py: Added default and failure outcome tests ([`30b35be`](https://github.com/ivansaul/codigo_facilito_downloader/commit/30b35be153faa2f538e49705c25cf90374f104c1))

* feat(browser): reuse a single page per run

Opening and closing a page per unit made the browser window reappear and
steal focus continuously. Reuse one page (and one probe page) for the
whole run so the window can be ignored once.

- src/facilito/utils.py: Added a weak per-context page registry with
  acquire_page/close_pages; save_page reuses the shared page
- src/facilito/collectors/*.py: Use acquire_page for navigation and stop
  closing the shared page; bootcamp probes reuse a dedicated slot and
  fetch_video removes its request listener
- src/facilito/async_api.py: Close shared pages on context exit
- src/tests/test_ratelimit.py: Updated save_page expectations and added
  page-reuse coverage
- README.md: Noted the single-tab behavior ([`6fc555a`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6fc555af43da0640d53056011b4339ccae219a68))

* feat(browser): run downloads offscreen by default

The headful browser popped in front of everything. It is still required
to pass Cloudflare and to capture the HLS playlist, so keep it headful
but position it off-screen and minimized, with an explicit way back to a
visible window.

- src/facilito/async_api.py: Added a window mode (offscreen, visible,
  headless) honoring FACILITO_WINDOW; offscreen launches Chrome headful
  with --window-position/-start-minimized
- src/facilito/constants.py: Added WINDOW_ENV_VAR, WINDOW_CHOICES and
  OFFSCREEN_ARGS
- src/facilito/cli.py: Added --window with validation on download and
  forced a visible window for login
- src/tests/test_ratelimit.py: Added window resolution, launch args and
  CLI/login tests
- README.md: Documented the window modes and defaults ([`0ebaadb`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0ebaadbfbbf65d9d242528e2c74141f94c74d8cc))

* feat(youtube): route embedded lessons to yt-dlp

The unit downloader now dispatches on the video provider so YouTube
lessons use yt-dlp while HLS keeps using vsd.

- src/facilito/downloaders/unit.py: Route provider == youtube to
  download_youtube and keep download_video for HLS
- src/tests/test_youtube.py: Added dispatch tests for both providers
- src/tests/test_ratelimit.py: Fake video now carries a provider, as
  download_unit reads it ([`a027d1b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a027d1bb83acfecb46bcf81fcadefcc32b3eb1df))

* feat(youtube): detect embedded players

When no HLS playlist is found, the collector now looks for a YouTube
iframe or markup URL and returns a video tagged with the youtube
provider instead of the dead static fallback.

- src/facilito/collectors/video.py: Added _iframe_sources and
  _find_youtube_id and set Video.provider; HLS still wins when a
  playlist is present
- src/tests/test_youtube.py: Added id priority, no-match, detection and
  HLS-precedence tests ([`6968f41`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6968f41e54604e9c6831dd3426e8a01848a3d0c6))

* feat(youtube): download embedded videos with yt-dlp

Added the YouTube downloader so embedded lessons produce an mp4 with
the same quality and skip semantics as HLS videos, reusing the existing
retry/abort policy.

- src/facilito/downloaders/youtube.py: Added quality_to_format and
  download_youtube with lazy yt-dlp import, noplaylist, quiet mode,
  retries=1, partial cleanup and classify_youtube_error
- pyproject.toml: Added the yt-dlp dependency
- src/tests/test_youtube.py: Added quality mapping, success, skip,
  transient retry, fatal, exhaustion and missing-dependency tests ([`7a941c8`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7a941c88a2895e49dd14f89fa5845dfc1adf30d7))

* feat(youtube): classify youtube download errors

The YouTube path must reuse the existing retry/abort policy, so yt-dlp
messages need the same Detection classification as vsd errors.

- src/facilito/ratelimit.py: Added classify_youtube_error with throttle,
  auth, fatal and transient tables
- src/tests/test_youtube.py: Added a classification table incl. unknown
  and empty messages ([`9274499`](https://github.com/ivansaul/codigo_facilito_downloader/commit/92744993196948630fb67d0952e76536d9aa8ffe))

* feat(youtube): extract youtube video ids

Detection needs to pull the 11-character id from the several URL shapes
YouTube uses, tolerating extra query parameters.

- src/facilito/helpers.py: Added YOUTUBE_ID_PATTERN and
  extract_youtube_id covering embed, nocookie, youtu.be and watch URLs
- src/tests/test_youtube.py: Added variants and invalid-input tests ([`ee41e77`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ee41e771d8c97cf2340e4873727a5a1c420d066f))

* feat(youtube): add video provider field

Embedded YouTube lessons need a different downloader than the HLS path,
so the model must carry which provider a video uses.

- src/facilito/models.py: Added VideoProvider (hls, youtube) and
  Video.provider defaulting to hls to keep existing sites valid
- src/tests/test_youtube.py: Added default and explicit provider tests ([`10a1724`](https://github.com/ivansaul/codigo_facilito_downloader/commit/10a17243a33a98158796586c5fe8aa7a63868974))

* feat(ratelimit): pace consecutive video downloads

Inserted the inter-download delay between consecutive real downloads
in course and bootcamp runs, leaving skipped units unpaced.

- src/facilito/downloaders/course.py, bootcamp.py: Create one Pacer
  per run, wait before each non-skipped unit and pass settings/stats to
  save_page
- src/tests/test_ratelimit.py: Added course/bootcamp loop tests
  asserting a skipped video consumes no pacing ([`c1d5808`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c1d580813d346c82e9f0f39e810a00571241e13a))

* feat(ratelimit): retry and classify vsd downloads

Wrapped the vsd subprocess in the retry adapter so video downloads
classify failures, clean partial output and abort on exhaustion.

- src/facilito/downloaders/video.py: Run vsd via asyncio.to_thread with
  stderr captured, classify with classify_vsd_error, remove partial
  output before retrying and re-raise AbortError; _download_vsd and the
  ffmpeg guard are untouched
- src/tests/test_ratelimit.py: Added success, transient retry with
  cleanup, exhaustion, auth and existing-file tests ([`87e5c18`](https://github.com/ivansaul/codigo_facilito_downloader/commit/87e5c184a3defc03002f9c4369a9b46638d6abb7))

* feat(ratelimit): thread settings through downloaders

Connected the resolved settings from the run entry point down to the
collectors and downloaders, and emitted a single end-of-run summary.

- src/facilito/async_api.py: download builds a run-level ThrottleStats,
  forwards settings/stats to fetch_* and download_* and logs the
  summary only when events occurred
- src/facilito/downloaders/unit.py: forwards settings/stats to
  fetch_video, download_video and save_page
- src/tests/test_ratelimit.py: Added forwarding and summary tests ([`7155f71`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7155f71b203639931b56c5837fa9a479cf1a4b82))

* feat(ratelimit): apply pacing and detection to collectors

Routed every site-facing collector navigation through throttled_goto,
including the high-frequency bootcamp redirect probes, and let aborts
propagate instead of being converted to domain errors.

- src/facilito/collectors/unit.py, course.py, video.py, bootcamp.py:
  Added settings/stats parameters, replaced page.goto with
  throttled_goto and re-raise AbortError before each broad handler
- src/tests/test_ratelimit.py: Added parametrized tests asserting
  collectors re-raise AbortError unchanged ([`98b772d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/98b772d502791b5981b20cec30b6639beff1d349))

* feat(ratelimit): abort propagation and paced page saves

Stopped the swallow boundary from hiding aborts and routed MHTML page
saves through throttled navigation.

- src/facilito/utils.py: try_except_request re-raises AbortError before
  its broad handler; save_page navigates via throttled_goto and
  re-raises AbortError without converting it
- src/tests/test_ratelimit.py: Added abort propagation, plain-exception
  swallow and save_page wiring tests ([`8f2c958`](https://github.com/ivansaul/codigo_facilito_downloader/commit/8f2c9587a44749cac92cc0bd3da20641d01b6557))

* feat(ratelimit): add throttled navigation and download pacer

Composed pacing, detection and retry into the two entry points used by
every call site, and added URL redaction for safe logging.

- src/facilito/ratelimit.py: Added throttled_goto, Pacer, redact_url
  and a bounded page.content fallback for 401/403 disambiguation
- src/tests/test_ratelimit.py: Added fake-page tests for pacing,
  transient retry, Retry-After cap, challenge retry, login failure,
  exhaustion, unknown 403 and Pacer first-operation rule ([`a866437`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a866437a8f7409ec86ebb2e0fa8e5480d7ec88f4))

* feat(ratelimit): detect 429 and Cloudflare challenges

Added pure, table-testable classifiers so the retry loop can tell
throttling, transient failures, auth failures and hard blocks apart.

- src/facilito/ratelimit.py: Added classify_playwright_response using
  status, headers, body and final URL markers, and classify_vsd_error
  using exit code plus table-driven stderr regexes
- src/tests/test_ratelimit.py: Added 429/5xx/403-challenge/403-auth,
  detection-disabled and vsd stderr classification tables ([`20a92cb`](https://github.com/ivansaul/codigo_facilito_downloader/commit/20a92cb9ce77d4f8bcfb2de9e21fc01b310d1bd8))

* feat(ratelimit): add retry/backoff with Retry-After support

Implemented the deterministic, injectable retry engine reused by every
call site, with full jitter, exponential backoff and Retry-After
handling.

- src/facilito/ratelimit.py: Added Detection, RetrySignal,
  ThrottleStats, RetryPolicy, parse_retry_after, sleep_with_jitter and
  run_with_retry with a configurable Retry-After cap and warning
- src/tests/test_ratelimit.py: Added seeded wait-sequence, cap,
  Retry-After table, single-attempt, auth, cancellation and stats tests ([`2bb2de4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2bb2de496d5aa38699af62e841332e2221d00efe))

* feat(ratelimit): add download CLI options and config resolution

Exposed the rate-limiting surface on the download command and made an
aborted run exit non-zero with an actionable message.

- src/facilito/cli.py: Added the pacing, retry, detection and --config
  options as tri-state sentinels, resolved them via
  config.resolve_settings, and converted AbortError into typer.Exit(1)
  with an ERROR log
- src/tests/test_ratelimit.py: Added help, option parsing, invalid
  value, missing config and abort-exit tests via CliRunner ([`80043f2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/80043f2d595677e95eaf239e2cde4733b60113b1))

* feat(ratelimit): add config loader with CLI precedence

Implemented resolve_settings so rate-limit options resolve with strict
CLI &gt; config file &gt; default precedence and actionable validation
errors.

- src/facilito/config.py: Added config path resolution (explicit
  --config &gt; FACILITO_CONFIG &gt; Facilito/config.json) and settings
  merging with BadParameter on missing explicit or invalid files
- src/tests/test_ratelimit.py: Added precedence, env var, unknown key,
  bounds and missing-file tests ([`871325a`](https://github.com/ivansaul/codigo_facilito_downloader/commit/871325a088defc47457ca047082db1dbce5de8a4))

* feat(ratelimit): add config path constants

Established the single source of truth for the rate-limiting config
file location and its environment override.

- src/facilito/constants.py: Added APP_DIR, CONFIG_FILE and
  CONFIG_ENV_VAR without touching existing session/URL constants
- src/tests/test_ratelimit.py: Added config constant assertions ([`dd182af`](https://github.com/ivansaul/codigo_facilito_downloader/commit/dd182af59f9c4f1ae280d43435029195dd02004d))

* feat(ratelimit): add RateLimitSettings model

Added the validated settings contract that every rate-limiting layer
will consume, with conservative retry defaults and pacing disabled by
default to preserve current behavior.

- src/facilito/ratelimit.py: Added RateLimitSettings with field
  bounds, extra=&#34;forbid&#34;, and a retry_max_delay &gt;= retry_base_delay
  validator
- src/tests/test_ratelimit.py: Added default, out-of-range,
  cross-field and unknown-key tests ([`ac00a23`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ac00a234aa0ca5908e4736301e460a0340e76a49))

* feat(ratelimit): add abort and rate-limit error types

Added the AbortError marker family so later rate-limiting work has a
single, unambiguous way to bypass the swallow boundary without
changing LoginError or the existing domain errors.

- src/facilito/errors.py: Added AbortError(BaseError),
  RateLimitError(AbortError) and RetryExhaustedError(RateLimitError),
  the latter carrying label, attempts and reason
- src/tests/test_ratelimit.py: Added hierarchy, LoginError-not-abort
  and RetryExhaustedError field tests ([`9a73339`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9a73339d0abd784b1d4e8c2db138f9b11e7736a2))

### Fix

* fix(video): mux streams ourselves instead of using vsd --output

vsd 0.4.1 builds an invalid ffmpeg command for single-stream playlists
(no -i), so those downloads always failed with ffmpeg exit 234
(-EINVAL). Reproduced locally with a video-only HLS playlist.

- src/facilito/downloaders/video.py: Download streams with vsd into a
  per-download directory (no --output) and mux them with ffmpeg (video
  first), cleaning the directory afterwards; partial output is removed on
  failure
- src/tests/test_ratelimit.py: Updated vsd fakes for the extra ffmpeg
  step and added a mux-failure test

Verified end-to-end against local HLS masters: a single-stream media
playlist now succeeds and a video+audio master still muxes correctly. ([`6854ffd`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6854ffd792137732f3462f674b1b9171d216a2ca))

* fix(state): use keyword args for UnitOutcome in tests

The pydantic model does not accept positional arguments.

- src/tests/test_state.py: Build the failure outcome with keyword arguments ([`3ac3207`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3ac32072e4ace5f376b97a6133d3a758578b7db5))

* fix(video): surface the real vsd error instead of progress noise

vsd wrote its progress bar to stderr, so the reported reason was the
first 200 characters of the progress bar and the actual error (and its
classification) was hidden.

- src/facilito/ratelimit.py: Added clean_process_output to strip ANSI
  codes and progress-bar lines
- src/facilito/downloaders/video.py: Classify and log the cleaned output,
  keep the tail of the message as the reason and pass --color never
- src/tests/test_ratelimit.py: Added cleaning and reason tests ([`ce5376b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ce5376bdecb0c0b04194a713b768a8e2ad875731))

* fix(video): extract the playlist URL from page markup

For some lessons the player neither requested the manifest during the
wait nor exposed currentSrc, so capture fell back to the dead static
URL. Scan the page markup (unescaping JSON) for the absolute signed
playlist URL, and log what the page contained when nothing is found.

- src/facilito/collectors/video.py: Added _find_playlist_in_html and a
  markup branch before the static fallback; log bcdn_token/m3u8 presence
  and the final URL, and log the player trigger outcome
- src/tests/test_ratelimit.py: Added HTML unescaping, no-match and
  fetch_video markup-branch tests ([`3836d26`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3836d26b523958b056c3352e845fae3a2e1b25bb))

* fix(video): trigger playback to capture lazy-loaded playlists

Some players only request the HLS manifest once playback starts, so the
network capture timed out and fell back to the broken static URL.

- src/facilito/collectors/video.py: When no .m3u8 request is observed,
  start playback (muted) and click a play button, then wait again; also
  read the playlist from the video element&#39;s currentSrc/src before the
  static fallback
- src/tests/test_ratelimit.py: Added trigger, player-source and
  fetch_video player-source tests

Verified locally with a page that only fetches the manifest on play(). ([`f4eb8bd`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f4eb8bdbc0d389e19e0b2700876bb4ac252c62f9))

* fix(video): send Referer header to the CDN

The captured playlist lives on a BunnyCDN host with referer-based
hotlink protection: without a Referer it returns 403 HTML, so vsd said
&#34;no playlists were found in website source.&#34;

- src/facilito/downloaders/video.py: Pass --header Referer &lt;BASE_URL&gt;/
  to vsd (supported since vsd 0.4.1)
- src/tests/test_ratelimit.py: Added a test asserting the Referer
  header is part of the vsd command

Verified manually: with the Referer header vsd parses the playlist and
muxes the video successfully. ([`a377426`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a3774260b9a4492189016c2d50a75a856db24585))

* fix(playwright): prefer Chrome for media codecs

The bundled Chromium ships without proprietary codecs, so the player
showed &#34;No compatible source was found for this media.&#34; and some
players never requested the HLS playlist, breaking playlist capture.

- src/facilito/async_api.py: _launch_browser prefers an installed
  Chrome/Edge channel and falls back to bundled Chromium; the browser
  can be forced via the browser argument
- src/facilito/constants.py: Added BROWSER_ENV_VAR, BROWSER_CHANNELS and
  BROWSER_CHOICES
- src/facilito/cli.py: Added --browser with validation and forwarded it
  to AsyncFacilito
- src/tests/test_ratelimit.py: Added channel selection, fallback, env
  var and CLI tests
- README.md: Documented --browser, FACILITO_BROWSER and the codec reason ([`7b21e7a`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7b21e7ac3e29bef593703bb34cbebc0e649a1dde))

* fix(video): repair VSD download and playlist URL

Fixed video downloads, which failed because the VSD binary was never
installed and the m3u8 URL was built from a hardcoded pattern that
the site no longer serves.

Fixed the VSD binary handling in the downloader:
- Corrected the GitHub release tag path to `vsd-{version}` and pinned
  version 0.4.1, a published release compatible with the `--quality`
  flag and the JSON cookie file.
- Made `_download_vsd` return the resolved binary path or None, log
  the real exception, remove partial archives on failure, and fall
  back to a system-installed `vsd`.
- Aborted `download_video` with a clear error when no binary is
  available, removed the non-existent `--skip-prompts` flag, and
  logged vsd stderr so failures are visible in facilito.log.

Updated the video collector to capture the actual `.m3u8` request
made by the player while the page loads, instead of relying on HTML
scraping and the static URL, so signed playlist URLs are supported.
Falls back to the previous strategies when no request is observed.

Modified files (2):
- src/facilito/downloaders/video.py: Fixed the VSD binary download
  and command flags, and added failure handling and stderr logging
- src/facilito/collectors/video.py: Captured the real playlist URL
  from page network requests, keeping the existing fallbacks

Validated with ruff, mypy and a local Playwright test server. The
live site could not be tested because Cloudflare blocks headless
browsers in this environment. ([`cf5b0b1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/cf5b0b177c330716b2542bb5babf79482fc01047))

### Style

* style: use quoted strings in test workflow ([`0e82cfa`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0e82cfa0c79b4d3f0da0ef6e05ba39285de61e54))

### Test

* test(log): keep the test suite out of facilito.log

Running the tests appended pytest noise (fake downloads, tracebacks) to
the user&#39;s facilito.log, which was confusing when reading real runs.

- src/facilito/logger.py: FACILITO_LOG_FILE overrides the log path and an
  empty value disables file logging
- src/tests/conftest.py: Disable file logging for the test suite ([`50712e3`](https://github.com/ivansaul/codigo_facilito_downloader/commit/50712e3bf4cd9ad0eed8a79b999cc2d79b93d885))

* test(ratelimit): cover abort chain, redaction and defaults

Closed the cross-cutting testing gaps that span multiple modules.

- src/tests/test_ratelimit.py: Added an end-to-end abort propagation
  test through try_except_request, a signed-URL redaction assertion and
  a defaults-add-no-waits test for throttled_goto and Pacer ([`f1ce66b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f1ce66b9d392009bb2fecb50a72964fc03a22711))

### Unknown

* Merge pull request #65 from fakel/master ([`a559eed`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a559eed563dff87de90d0dbffa6afe6a41f854f3))

* Merge pull request #62 from ivansaul/chore/test-workflow

chore: remove ffmpeg and playwright install steps ([`6af0d55`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6af0d552428d43cb4c30f09f4f48800d1e7f9988))

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci ([`414309e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/414309e6f0cae6713c3ac9384f82eb4228606244))

## v0.5.0 (2025-11-10)

### Chore

* chore: add /Facilito/ to .gitignore to exclude project-specific files ([`dd114dd`](https://github.com/ivansaul/codigo_facilito_downloader/commit/dd114dd38f8835bd9820ceeda0019de2a71aca08))

### Documentation

* docs: refactor Copilot instructions for clarity and structure

- Updated project overview to include bootcamps in the description.
- Enhanced the architecture section by clearly separating collectors and downloaders.
- Improved descriptions of collectors and downloaders with specific file structures.
- Revised key conventions and patterns for better organization and clarity.
- Added details about entity model hierarchy and updated authentication state management.
- Clarified error handling strategy and file naming conventions.
- Specified the location of the VSD binary cache directory.
- Added a note on bootcamp redirects in the testing strategy. ([`10dd4fa`](https://github.com/ivansaul/codigo_facilito_downloader/commit/10dd4faf7a77592a439b62e0686a8e798268caa6))

* docs: update git commit message instructions for .md files

Enhanced the guidelines for generating commit messages related to .md files.
Clarified that even for multi-file changes involving only documentation, a detailed body is required.
Updated examples to emphasize the necessity of including file lists and explanations for changes made to multiple .md files. ([`5604a91`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5604a91d93c1aeb2d60b53ec10a856fc6660b789))

* docs: configure commit message generation for Copilot

Added reference to git-commit-messages-instructions.md in VSCode settings to enable automatic commit message generation following Conventional Commits specification for this project.

Modified files (2):
- .vscode/settings.json: Added Copilot instructions reference
- .github/git-commit-messages-instructions.md: Created rules ([`3c3e42d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3c3e42d2cbdcebea7e7e5c4e985e0264e8e1530e))

* docs: Add comprehensive AI agent instructions for Codigo Facilito Downloader, detailing project overview, architecture, workflows, conventions, and testing strategy. ([`0a0fe02`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0a0fe02c4724dba3daa9cab8246bd0fda51f1ce2))

* docs: add contributing guidelines and update README ([`6884ecc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6884ecc6919fa344df78ca71b4692da97f317b00))

### Feature

* feat(bootcamp): add bootcamp support to downloader

- Implemented bootcamp fetching and downloading functionality.
- Added `fetch_bootcamp` method in `AsyncFacilito` class.
- Created `bootcamp.py` in collectors for bootcamp module fetching.
- Added `download_bootcamp` function in downloaders for saving bootcamp data.
- Updated CLI to accept bootcamp URLs for downloading.
- Enhanced models to include Bootcamp and Module structures.
- Introduced utility function `is_bootcamp` to identify bootcamp URLs. ([`410ae34`](https://github.com/ivansaul/codigo_facilito_downloader/commit/410ae34d9b64e695a950c23f76dad560522c7ad3))

### Refactor

* refactor: error message formatting and improve comments in bootcamp module fetching

- Split long error message into multiple lines for better readability in AsyncFacilito class.
- Enhance comments in _fetch_bootcamp_modules function to clarify the purpose of following redirects and waiting for navigation. ([`fbff624`](https://github.com/ivansaul/codigo_facilito_downloader/commit/fbff624959790375372e95a81492e566bf76b123))

### Unknown

* Merge pull request #61 from cristofima/feature/bootcamps

feat(downloaders): add bootcamp download support ([`eedf032`](https://github.com/ivansaul/codigo_facilito_downloader/commit/eedf0321e9cff5cfb7398e8b6bb2d2442bfc03cf))

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci ([`a7fdbd5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a7fdbd522dd2e910c5375445530bf83f9edd5bbc))

* Merge pull request #59 from ivansaul/docs/contributing

docs: add contributing guidelines and update README ([`2496667`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2496667a1d20030527b225daf5666de4ec7a4e46))

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci ([`7fbf3bc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7fbf3bccf797176688f4ac851b28edd8243dba10))

## v0.4.0 (2024-12-16)

### Documentation

* docs: remove redundant poetry installation steps. ([`e23c8e7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e23c8e77c626855cee9486b263f02b2ccd51b7c3))

* docs: improve installation instructions

Add recommended `poetry` installation instructions, provide detailed installation and upgrade steps using `poetry` and `pip` ([`e15d25c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e15d25c4f53c6ff7b6838e53996507b0c1d0d59f))

### Feature

* feat: add support for Windows AMD64 architecture

- Add the &#34;windows, amd64&#34; mapping to the binary URLs, pointing to the 
x86_64-pc-windows-msvc.zip binary. This expands the supported Windows architectures.
- This change resolves the error: [ERROR] Unsupported platform: windows amd64.

Thanks to @Isaac-opz for the contribution! ([`5dba1a3`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5dba1a3f8d934805ab07777588324da177d21b93))

### Unknown

* Merge pull request #51 from ivansaul/refactor

docs: remove redundant poetry installation steps. ([`ead5a08`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ead5a0846a1aed37d68bbefa4a33073cb26c5014))

* Merge pull request #50 from ivansaul/refactor

docs: improve installation instructions ([`365c75c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/365c75ca499ff2be25c467823a0181299669f411))

## v0.3.0 (2024-11-24)

### Documentation

* docs: add a link to previous stable version ([`258e8ea`](https://github.com/ivansaul/codigo_facilito_downloader/commit/258e8eab6c0d7ba5c08c0f6d7f5b918c29e073ce))

* docs: update README TODO ([`2ca31ce`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2ca31ce4b9f36285a980e3ad12db8bced90260e6))

### Feature

* feat: add cookie-based login

- Implement a new `set-cookies` command for CLI login using cookies
- Provide instructions for exporting cookies
- Add a helper function to normalize cookie format ([`41228fe`](https://github.com/ivansaul/codigo_facilito_downloader/commit/41228fe8fb11c404366bd6b239ea6e25371f1cac))

### Unknown

* Merge pull request #48 from ivansaul/refactor

docs: update README TODO ([`933890e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/933890eef3824e8b4c15f337acb2680697cdb595))

## v0.2.1 (2024-11-23)

### Fix

* fix: video m3u8 URL retrieval ([`af9470f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/af9470f683e3bc3aa2c5bd2fba7ec9505ff6ee80))

### Unknown

* Merge pull request #47 from ivansaul/refactor

fix: video m3u8 URL retrieval ([`83a4f54`](https://github.com/ivansaul/codigo_facilito_downloader/commit/83a4f54ae3b11fea0fabe95bb38560b1539421c6))

## v0.2.0 (2024-11-23)

### Chore

* chore: removes redundant PyPI publishing step

Removes the redundant `pypa/gh-action-pypi-publish` step from the release workflow. ([`2c63fba`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2c63fbaa4ec9f6b4f91194e1dbd73838536ddf33))

### Documentation

* docs: add important stability notice callout ([`75f7c25`](https://github.com/ivansaul/codigo_facilito_downloader/commit/75f7c25022abb1c3e87896411a7a1f86fbff2a78))

### Feature

* feat: add support for quiz downloads ([`28a0284`](https://github.com/ivansaul/codigo_facilito_downloader/commit/28a02842c58ab945764f56ce985422034200dbc7))

* feat: add support for dynamic CSS selectors in course extraction

Refine selectors to handle dynamic HTML structures for chapters and units. ([`4670197`](https://github.com/ivansaul/codigo_facilito_downloader/commit/46701973af47cfd782d267f5f4e36354b69387eb))

### Fix

* fix: unit download logic ([`91d8d21`](https://github.com/ivansaul/codigo_facilito_downloader/commit/91d8d21e795f4195808e541972c2e0737c943ab2))

### Unknown

* Merge pull request #46 from ivansaul/refactor

feat: refine selectors to handle dynamic HTML structures ([`82dd297`](https://github.com/ivansaul/codigo_facilito_downloader/commit/82dd2973cd6299e215124f8c3471d49ce39821bd))

* Merge pull request #45 from ivansaul/refactor

docs: add important stability notice callout ([`19093b0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/19093b0571718d53d4916a449f85e0c409b473e7))

## v0.1.0 (2024-11-23)

### Chore

* chore: disable upload to PyPI by setting `upload_to_pypi` to false ([`2d93def`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2d93def8b110228cb0f81d37de0e827ac551002d))

* chore: update version to 0.5 to reflect the current release state ([`a93e140`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a93e1404d18c89f682515676529285b2f1d376c5))

* chore: updates dependencies and settings ([`0798799`](https://github.com/ivansaul/codigo_facilito_downloader/commit/07987993949c044d11078ed1ea0cc49ca4ebe7f5))

* chore: move unit type detection logic to utils.py ([`0504482`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0504482384aadd6a214e48ea1e9c27f3a59b1d1a))

* chore: updates dependencies

Update various dependencies to newer versions, add  tools for code quality, testing, debugging and introduces colorlog, unidecode, and playwright-stealth ([`50cbd5b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/50cbd5b9dfe9a2b769b845a53bc88bc83bd1d79a))

* chore: improve unit tests helper functions

Adds tests for `clean_string`, `hashify`, and `slugify` functions. ([`1793045`](https://github.com/ivansaul/codigo_facilito_downloader/commit/17930457a3d530e59ea2607f2ebb17b47266f3a4))

* chore: improve collectors functions

Implements asynchronous functions for fetching course, unit, and video data from the Facilito platform. ([`97dd66c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/97dd66cf393e06405fc6b7d0c79abd1879a11855))

* chore: improve configuration constants for Facilito app

Add necessary constants for the Facilito application, including URLs for different endpoints and the session directory. ([`56ce594`](https://github.com/ivansaul/codigo_facilito_downloader/commit/56ce594133b814cb28e2d4a2e24a7cc9f7acae4f))

* chore: improve utility functions

Add functions for handling login, asynchronous requests, saving and loading browser state, progressive scrolling, and saving web pages as mhtml. ([`f6808f0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f6808f0fd4097d46341ace6f8f932047f750ffaf))

* chore: improve custom error classes for facilito

Introduces a hierarchy of custom error classes (BaseError, LoginError, VideoError, UnitError, CourseError) for improved error handling and clarity. ([`c1ca651`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c1ca6512b613ebc994e23d1463da8fc5a5f79095))

* chore: improve resource models for facilito

Add models for `Resource`, `Video`, `Lecture`, `Unit`, `Chapter`, and `Course` to represent facilito resources.
Includes `Quality` and `TypeUnit` enums for better data organization. ([`f79a16f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f79a16fb09e7a9abd78d4d4bbbd5bfb260dec770))

* chore: improves helper functions

Improves helper functions for better readability and maintainability, replaces legacy functions with cleaner alternatives and removes redundant comments and unused code. ([`5c89b1b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5c89b1bab506cb234eaeda9e22e5d8dba8e00b4c))

* chore: improve logging functionality with color formatting ([`1c198d3`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1c198d399e968890fb42865f6ce1744527bd7963))

* chore: delete all previous files and reset project structure ([`a65cbd4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a65cbd490e1648eaf93a1339bab1a9241fe9ce5b))

* chore: add bug-report and request-feature markdown templates ([`4aab76f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/4aab76fae25441e047d08a6ab4138cc241e9f40b))

* chore(vscode): add spanish spell checker ([`506d894`](https://github.com/ivansaul/codigo_facilito_downloader/commit/506d894fab6fcc9f4407865ec3c249d02ce670af))

* chore(vscode): add extension.json

added recomendations extensions ([`53011c5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/53011c5a05f73371b055cd3e2a5afa56a3af1ffc))

* chore: add pre-commit config file ([`af58b89`](https://github.com/ivansaul/codigo_facilito_downloader/commit/af58b899e2f20db39b3e7136f49bf112d7789650))

* chore: remove requirements.txt ([`a7e97ba`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a7e97ba524e7da2e9c139815dcb965ab8bc934d8))

* chore: change version in pyproject.toml

-  change from 0.1.0 to 0.5.0 ([`abb2fd9`](https://github.com/ivansaul/codigo_facilito_downloader/commit/abb2fd94d4c30b4fdf3c1f1c0b4deae2993c254a))

* chore: add .vscode  to git tracking ([`5b6a0b1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5b6a0b192c255b77595e82437c49f486f7b774e1))

* chore: integrate Poetry for dependency management ([`a65dca2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a65dca2937da14bd95b132facb7cf4d5c8899d65))

* chore(git): stop tracking cookies.txt ([`399d181`](https://github.com/ivansaul/codigo_facilito_downloader/commit/399d181f69964daa300b6f473d9eadcc3afa2f67))

### Documentation

* docs: update installation instructions to use GitHub instead of PyPI ([`08711c1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/08711c11843323264cda951bd889f9b341687977))

* docs(readme): remove cheat-sheets testing banner ([`e39524c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e39524cf4a925fb036c903b5d82306f9e2088ca6))

* docs(readme): add cheat-sheets testing banner ([`8dd68c5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/8dd68c5001019005d3a37a9fb4dc67d1177b85e2))

* docs(readme): fix scoop python installation command ([`0cc8f63`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0cc8f63047305cbf37780299f60c4749a679c5ac))

* docs(readme): update instructions and fix typo

- add instructions to install git
- add important quote for update repo ([`554511d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/554511dc2a2996e928d17afc574b88c209127c5d))

* docs(readme): update windows important quote

- added scoop youtube tutorial link ([`69671c7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/69671c72909750007ad43fd4b953a95115ee2cc5))

* docs(readme): update header readme

- change repo banner image
- add demo.gif ([`432c26b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/432c26b9a0401399b80d7983307a3fe88ebfbfa4))

* docs(readme): update readme

- add playwright deps install instructions
- add output download command example ([`771b62e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/771b62e2909c0d39874599f3b3293e4695104221))

* docs(readme): improve code block formatting

Updated code block from &#39;```bash&#39; to &#39;```console&#39; for better rendering. ([`96b7473`](https://github.com/ivansaul/codigo_facilito_downloader/commit/96b7473360140838d050f2fba63394fd15fbf80a))

* docs(readme): fix formatting in [!IMPORTANT] ([`2d24522`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2d24522a8941b3068d8406b8aefee712e04f9c9d))

* docs: update README

- add important blockquote ([`140b28f`](https://github.com/ivansaul/codigo_facilito_downloader/commit/140b28f8b7768b68b18bedee6359e5e812632a6b))

* docs: update README with new github blockquotes ([`0a7040e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0a7040ed209baaf75e267f7b78b9602b46eb6317))

* docs: fix Discord channel link ([`636c7a0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/636c7a071131826c3af836a65c4e2a55255cd567))

* docs: update README with maintenance notice ([`5227962`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5227962547795dd22b74de9b0045e2ad3a61829c))

### Feature

* feat: add thread control to downloaders

Improve download performance by introducing a configurable number of threads. Allows users to control the number of concurrent downloads from 1 to 16. ([`37d4fb1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/37d4fb17e522179ee7bd015ae0b70166f15f0442))

* feat: add source.mhtml file downloading for courses ([`6624bb2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/6624bb2b3c7ee5254756c6920b7e932e8d5b9f11))

* feat: adds CI/CD pipeline for automated releases

Adds GitHub Actions workflows for testing and releasing packages, Integrates semantic-release for automated versioning and PyPI uploads. ([`2931277`](https://github.com/ivansaul/codigo_facilito_downloader/commit/293127753759b965292e9ea37d88e3143a185c00))

* feat: add CLI commands for facilito

Implements `login`, `logout`, and `download` commands for interacting with the facilito API.
These commands provide a command-line interface for common tasks. ([`86c9a21`](https://github.com/ivansaul/codigo_facilito_downloader/commit/86c9a21ab7a11a388bae55d1da4042c226be1fac))

* feat: add video downloader and course downloader functionality ([`a39ef49`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a39ef491716ba528c6bcb4073564a9d714400ece))

* feat: Add AsyncFacilito API class

Implements an asynchronous API class for interacting with the Facilito platform, using Playwright for browser automation. Includes methods for login, fetching units and courses, and handling authentication. ([`30af9ba`](https://github.com/ivansaul/codigo_facilito_downloader/commit/30af9baf4a40aeb5e94196eb9f9bc73282bda85c))

* feat: add default prefix to sections title ([`bd76d0c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/bd76d0c4f6876d784f4f9737ca5d00cc65e74507))

* feat: add prefix_name argument to video.download() method ([`9964c65`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9964c65099e7c5642ea52542f81335871e6611c8))

* feat(cli): updete download command

- implement download course by url
- add headless mode option ([`99122cf`](https://github.com/ivansaul/codigo_facilito_downloader/commit/99122cfb6fb6e35dd83499891e668c8743b9da07))

* feat: add new logger(cli_logger) ([`64ae708`](https://github.com/ivansaul/codigo_facilito_downloader/commit/64ae708cad4467534a1cae60ebed6d5aa4ddcfac))

### Fix

* fix: course fetching

Add handling to expand all course chapters ([`b13c639`](https://github.com/ivansaul/codigo_facilito_downloader/commit/b13c639d2fd7141a90fc1f9d2aeb91c3fa4bd04f))

* fix: helper is_ffmpeg_installed()

- was caching wrong exception ([`f98b041`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f98b041ae38c6d00dc2a150937aded162a0e09e3))

### Refactor

* refactor: remove unnecessary file ([`0de0d07`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0de0d073f6a65d0834e9a926d2c5ac2e106da6a9))

* refactor: WIP update multiple files ([`c0d99f5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c0d99f537c84c5327c1a83b6b35f35d8c9c491fa))

* refactor: remove unnecessary files ([`d946bb4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d946bb4de0b665f833cc20f41acfada203c9b496))

* refactor: WIP add test ([`5d8f7a6`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5d8f7a6f2c6d7cbd7d7228e14a52559a5afa972d))

* refactor: WIP rewrite code ([`e555880`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e555880e60f592944df0ab41daf403d89e0cdf2d))

* refactor: migrate to Playwright(WIP) ([`2985a44`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2985a44caa9c1cd173ec87859a19d6060f36d58f))

* refactor: migrate to Playwright(WIP) ([`14f3b7a`](https://github.com/ivansaul/codigo_facilito_downloader/commit/14f3b7a0d22f09a507c6c7281db8f56721d11468))

### Style

* style(format): apply style formatting with Black.

- run all pre-commits. ([`cefaa66`](https://github.com/ivansaul/codigo_facilito_downloader/commit/cefaa66a80430ee616c7cd00b3664531ba908463))

### Unknown

* Merge pull request #44 from ivansaul/refactor

refactor: add asynchronous api ([`d6d7d91`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d6d7d91a3dc6a8c4242574b2a86f7d52aad31cb3))

* update README with updated installation and usage instructions. ([`2627e64`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2627e64a2a0581bd062799bf8ec36064764e996f))

* Merge pull request #33 from ivansaul/pre-commit-ci-update-config

[pre-commit.ci] pre-commit autoupdate ([`9062ca9`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9062ca92c1a45b8e4a89de63f85cfb47280efa59))

* [pre-commit.ci] pre-commit autoupdate

updates:
- [github.com/pre-commit/pre-commit-hooks: v2.3.0 → v4.5.0](https://github.com/pre-commit/pre-commit-hooks/compare/v2.3.0...v4.5.0)
- [github.com/pycqa/isort: 5.12.0 → 5.13.2](https://github.com/pycqa/isort/compare/5.12.0...5.13.2)
- [github.com/hadialqattan/pycln: v2.3.0 → v2.4.0](https://github.com/hadialqattan/pycln/compare/v2.3.0...v2.4.0) ([`9722812`](https://github.com/ivansaul/codigo_facilito_downloader/commit/972281260cc9d22bfec61eb7f476186d1be4918f))

* Merge pull request #32 from Ronald3217/fix/multi-input

fix(collectors):   locator find multiple elements with course_id name ([`597648e`](https://github.com/ivansaul/codigo_facilito_downloader/commit/597648e56c7c54e206c5c632c047b75669bae0ff))

* FIX: Error finding multiple elements

Error when finding multiple elements with the id &#34;course_id&#34; is fixed ([`f9a84a5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f9a84a505c35eed4996a9e34a2b59fcd6f8d68e7))

* Merge branch &#39;rewrite&#39; v.0.5.0 ([`7a39af0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7a39af01b91f92b6dc5333a37be3bf6ce4412479))

* doc: update readme ([`acbe5ad`](https://github.com/ivansaul/codigo_facilito_downloader/commit/acbe5ad7094b2e01e0d9da99c3598e3b092773d5))

* rename src files ([`1673af5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1673af50a703cd2dead355cf82cced2ad64b6f37))

* WIP: add docstrings ([`4c45da7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/4c45da7678d809844d2364eb3a4a7282135ecc2c))

* Merge pull request #29 from Ronald3217/master

FEAT: Descargar en lote ([`8766800`](https://github.com/ivansaul/codigo_facilito_downloader/commit/87668000275c6e3efcd3e299b5a4df5af7e00ceb))

* FEAT: Descargar en lote

Se agrega la funcion para descargar en lote, Leer README.md ([`c7071ad`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c7071adf5e92d37db1c172e91ba13189269a75eb))

* Merge branch &#39;master&#39; of github.com:ivansaul/codigo_facilito_downloader ([`3f0265b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3f0265b6e02a33345fa30f14d7f0a14c3e396c1e))

* set number of threads for yt-dlp ([`874878c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/874878c982f60372e3fd135591d42bd09fc5f706))

* Merge pull request #19 from Ronald3217/master

FEAT:  Obtener info del bootcamp ([`ed29079`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ed290792ca3ea607905f2fc5d1d9069d9d3c6b5d))

* FEAT:  Obtener info del bootcamp

Obtener la información del bootcamp, y almacenarla en &#34;bootcamp.json&#34; ([`0f373c1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/0f373c141d806d8f906f59e9a8b5cdb7a2f268c2))

* remove demo ([`df7d6c8`](https://github.com/ivansaul/codigo_facilito_downloader/commit/df7d6c8f357f1cd2d912010254ca5afe7cac5437))

* implement FacilitoCookies ([`19daacf`](https://github.com/ivansaul/codigo_facilito_downloader/commit/19daacf879074581e22f170577edb5f8551c6a72))

* implement FacilitoCookies ([`809df90`](https://github.com/ivansaul/codigo_facilito_downloader/commit/809df903f4d07240579b8d8fb6872bc59b4d32e0))

* update readme ([`5fc09e5`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5fc09e5b61435e8a685f973e2583674a0edad055))

* update readme ([`d8eb634`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d8eb63486634d05174deff2db396fccc0b0c6f1e))

* implement quality, external_dowloader selections options ([`2892d43`](https://github.com/ivansaul/codigo_facilito_downloader/commit/2892d435b89c9e818b5271c2cbc4ab2f2d0540f8))

* add click package ([`ffe14dc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ffe14dc4656135d9c110e9261a1f2cc5f2cd423d))

* fix -&gt; remove all empty videos and articles ([`1821c7c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/1821c7cef68c4ff9ecfee5bdf60b0d79641086d0))

* move check aria2 and geckodriver to utils ([`82498d0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/82498d076aa596fd307c816e03978b4b17ef05f3))

* add &#39;articulos&#39; conditional checker ([`a887ab0`](https://github.com/ivansaul/codigo_facilito_downloader/commit/a887ab0214e5adff54e5252267de772da3608ba7))

* add encoding utf-8 ([`4c88d77`](https://github.com/ivansaul/codigo_facilito_downloader/commit/4c88d7738630e3a483d7a18708c8e178f698121a))

* implement input_credentials utils ([`86c9def`](https://github.com/ivansaul/codigo_facilito_downloader/commit/86c9def3b621854d07b2ebe330487aa9b389cf2d))

* Update README.md ([`49ba1f9`](https://github.com/ivansaul/codigo_facilito_downloader/commit/49ba1f960c315d393b89455922c402874f3b9a93))

* fix local_driver_path in check_aria2 method ([`b52c721`](https://github.com/ivansaul/codigo_facilito_downloader/commit/b52c721fab0ad70c79f9d055eb773557e4906bc9))

* implement check_aria2() method ([`f0bfcd6`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f0bfcd6b9ce7dd2779b99470483c82dae9cdb85d))

* extract release version to variable &#34;release&#34; ([`3e25bc1`](https://github.com/ivansaul/codigo_facilito_downloader/commit/3e25bc1672694dfb24b7a1c5c5e9969ff416c7a3))

* update readme ([`ad379a2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ad379a2ba0bc4ca4c05e96ea6923763a01862ce3))

* set headless to True ([`f137b0c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f137b0c6afae0de9cb6192285a4149b7540f0628))

* add support for win and mac ([`5049167`](https://github.com/ivansaul/codigo_facilito_downloader/commit/5049167c5eaacf0405aadb4d2c0dee81703dc3a3))

* Update README.md ([`f24910d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f24910dd2572bcb3cbcb24bcc56fcc5afb80a59b))

* Update README.md ([`d426bb2`](https://github.com/ivansaul/codigo_facilito_downloader/commit/d426bb28ba53b3ded043611710cf2e344052e18a))

* fix -&gt; remove pop up promo banner ([`06c3fea`](https://github.com/ivansaul/codigo_facilito_downloader/commit/06c3feacdd52d70ab41ee983b55b490a213490f2))

* fix -&gt; remove pop up promo banner ([`ff9722d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/ff9722dbd843f9a685072279bc5e0a6f01b5bfa6))

* Update README.md ([`9b85dbd`](https://github.com/ivansaul/codigo_facilito_downloader/commit/9b85dbd472558b8b0c05d3966f85d8fef8cdbdbc))

* Update README.md ([`e45b23c`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e45b23cb2a464ee5e49567e27b700e1f32a5c995))

* fix counter video name ([`c516d64`](https://github.com/ivansaul/codigo_facilito_downloader/commit/c516d64ef7930270880cce1863c8b7775e1d6b1b))

* add counter [1-&gt;n] ([`936c91d`](https://github.com/ivansaul/codigo_facilito_downloader/commit/936c91daa5c3d4735fec5f83c4bbcd2daf2d91c4))

* Update README.md ([`efbdfab`](https://github.com/ivansaul/codigo_facilito_downloader/commit/efbdfabb255efc3793dbab5e945bf3e807038871))

* Update README.md ([`88e69cc`](https://github.com/ivansaul/codigo_facilito_downloader/commit/88e69cc6a436f44a714803273dcbfaac9ad74575))

* update readme ([`f64d6f4`](https://github.com/ivansaul/codigo_facilito_downloader/commit/f64d6f442cd390f92bc58f6dad1a0c8bbe644cbc))

* initial commit ([`14b3554`](https://github.com/ivansaul/codigo_facilito_downloader/commit/14b3554276cec4d005ff65c94bbdbc78e90075a7))

* initial commit ([`7c1a441`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7c1a441ce1759410d8a6b98c670b44719a45a053))

* initial commit ([`bf3f9e3`](https://github.com/ivansaul/codigo_facilito_downloader/commit/bf3f9e378ec19869a34181cc938dd5bf563515fb))

* initial commit ([`602c18b`](https://github.com/ivansaul/codigo_facilito_downloader/commit/602c18b29a9bb369a62787628a6f30022f37e446))

* initial commit ([`acdd065`](https://github.com/ivansaul/codigo_facilito_downloader/commit/acdd0659ee916396fd8b530f4986d9fe8baea4e6))

* initial commit ([`e85e2a7`](https://github.com/ivansaul/codigo_facilito_downloader/commit/e85e2a725d5dae9de844c3636f9a6c843fd8c04c))

* Initial commit ([`7920136`](https://github.com/ivansaul/codigo_facilito_downloader/commit/7920136ff5809f1b4039ae56c755d5b5820eabdd))
