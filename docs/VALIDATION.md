# Validation scope

## Current 2.10.1-readable configuration

The portable runner passed dependency/compatibility scenarios, independent component switches, diagnostic tests, shared-state checks, and 1,000 lamp-save comparisons. The shipping-default check confirms that visibility, the multiplayer wrapper's original-function reference, world lighting and lamp-flicker queries remain untouched by their disabled components.

The [AI audit](AI-REVIEW.md) compared 60,000 calls across two upstream visibility variants. It found a formula mismatch with Atmospherics and controlled cache-freshness differences. These tests use simulated engine inputs; they are not a live combat or network test.

## Earlier readability build

The 2.10.0-readable refactor also underwent local behavior suites covering callback ordering, marker projection, artifact transitions, visibility and device updates. Those suites are not all included in this ZIP.

One 60-second in-game activation/stability check on GAMMA/xrRazom with Anti-Lag completed. Eighteen components activated; ledge optimization skipped an incompatible implementation. No crash or startup diagnostic error was reported. That build still had the three components subsequently disabled in 2.10.1.

## What remains unverified

There is no new FPS comparison for the conservative 2.10.1 defaults, no exhaustive combat/stealth trial, and no claim that connected co-op behavior is fully covered. ACTIVE means installation succeeded, not that all gameplay is validated. Historical performance graphs describe earlier versions.

Documentation-only revisions do not change runtime scripts. Follow [development](DEVELOPMENT.md) to run the included checks or build the ZIP, and [troubleshooting](TROUBLESHOOTING.md) when behavior differs.
