## Context

`TwitterScraper` (`app/scraper.py`) has a private `_logged_in` flag that is set on success but never read anywhere else in the codebase. `lifespan()` in `app/main.py` calls `scraper.login()` once at startup and only logs on failure — nothing downstream checks whether login actually succeeded before accounts are added or polls run. `/healthz` (`app/main.py:100-102`) is a static `{"status": "ok"}` with no relation to scraper state. This gap was exposed directly: a recent twikit/X compatibility bug (`Couldn't get KEY_BYTE indices`) made login fail consistently, but the server reported healthy and gave no visible signal that tracking was broken.

## Goals / Non-Goals

**Goals:**
- Make the scraper's login state (logged in / error message) inspectable at runtime.
- Retry login automatically before a poll if not currently logged in, so a transient startup failure self-heals on the next scheduled/manual poll instead of requiring a process restart.
- Surface login failure to the operator through both `/healthz` and the dashboard.

**Non-Goals:**
- Building a full retry/backoff strategy with exponential delays or jitter — a poll already runs on a fixed interval (`POLL_INTERVAL_MINUTES`), which is a sufficient retry cadence.
- Alerting via Telegram on login failure (could be a future addition, out of scope here).
- Fixing the underlying twikit `KEY_BYTE indices` bug itself — that's an upstream library issue, not something this repo controls.

## Decisions

- **Expose login state via a small public property/method on `TwitterScraper`** (e.g. `scraper.is_logged_in` and `scraper.last_login_error`) rather than a separate module-level global, keeping state colocated with the client that owns it.
- **Retry login inside `poll_all_accounts()`**, at the top of the function, guarded by `if not scraper.is_logged_in`. This reuses the existing poll schedule as the retry cadence instead of adding a new APScheduler job. Alternative considered: a dedicated periodic "login watchdog" job — rejected as redundant complexity when polling already runs on the same interval.
- **`/healthz` gains a `twitter_login` field** (e.g. `{"status": "ok", "twitter_login": "ok" | "error"}`) rather than changing its HTTP status code, so container orchestrators' liveness checks (which only care the process is alive) are unaffected; the web dashboard is the primary place an operator would notice the problem.
- **Dashboard banner**: pass `scraper.is_logged_in` / `scraper.last_login_error` into the `index.html` template context and render a simple warning block (plain CSS, consistent with the rest of the dependency-free UI) when not logged in.

## Risks / Trade-offs

- [Risk] Retrying login on every poll when credentials are permanently wrong (e.g. account suspended) adds one extra login attempt per poll cycle indefinitely → Mitigation: this mirrors today's single attempt in cost (one `login()` call), just repeated on the existing schedule rather than continuously; the dashboard/`/healthz` surfacing lets an operator notice and fix credentials rather than let it retry silently forever.
- [Risk] `login()` raising mid-poll could leave `poll_all_accounts()` partially executed → Mitigation: wrap the retry call in its own try/except so a failed re-login just skips this poll cycle (logged, `last_login_error` updated) without aborting account-level polling logic that follows.
