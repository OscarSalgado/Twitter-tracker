## Why

The Twitter/X login (via twikit) is only attempted once, at app startup, inside `lifespan()`. If it fails — due to bad credentials, a twikit/X compatibility issue, or a transient network problem — the exception is only logged to stdout and the app keeps running with a scraper that was never logged in. Operators only discover the failure by tailing server logs; `/healthz` reports `200 ok` regardless, and the dashboard gives no indication that adding accounts or polling will fail. There is also no retry: a transient failure at startup permanently disables tracking until the process is restarted.

## What Changes

- Track the scraper's login state (logged in / not logged in / last error) so it can be inspected at runtime, not just inferred from logs.
- Retry the login automatically before each scheduled poll (and on-demand "check now") if the scraper isn't currently logged in, instead of only trying once at startup.
- Surface login status on the dashboard (e.g. a banner when not logged in) so the operator doesn't need to read logs to notice tracking is broken.
- Extend `/healthz` (or add a distinct status field) to reflect the real Twitter login state rather than always reporting healthy.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `web-dashboard`: the health check requirement is extended to report Twitter login status, and the dashboard overview surfaces a not-logged-in warning.
- `tweet-polling`: add a requirement that a poll (scheduled or manual) retries login first if the scraper is not currently logged in, before attempting to fetch tweets.

## Impact

- `app/scraper.py`: expose login state and last login error; `login()` becomes safely re-callable.
- `app/tracker_service.py`: attempt re-login before `poll_all_accounts()` if not logged in.
- `app/main.py`: `/healthz` reports login status; dashboard route passes login state to the template.
- `app/templates/index.html`: render a warning banner when not logged in.
- No new external dependency or additional requests to X beyond the existing login/poll calls — retries only occur on the same schedule as regular polling, so this does not increase request volume or risk of rate-limiting/ToS issues beyond what already happens today.
