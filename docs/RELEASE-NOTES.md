# v2.10.3-readable: compatibility and safety

* Reads current binder objects on each update instead of retaining object identities across updates.
* Validates reviewed item, artifact, device and callback implementations before replacement.
* Falls back to the original callback dispatcher if public sorting helpers change later.
* Handles missing radiation widgets and party HUD renderers; tracks replacement party widgets without retaining removed wrappers.
* Simplifies redundant checks around guaranteed engine APIs.

See [Compatibility hardening](COMPATIBILITY-PASS.md) and [Validation](VALIDATION.md).
Validation: 16 audit test methods and the existing portable suite passed. An initial gameplay walkthrough reported normal behavior. No additional FPS gain or exhaustive connected multiplayer validation is claimed.

## Published baseline: v2.10.2-readable


* Restores guarded visibility optimization for reviewed Atmospherics and Stealth Crash Fix variants, preserving each original formula.
* Preserves xrRazom's inner load-time per-player memory/marking rewrites as well as its outer avatar wrapper. Checks instructions, constants and private-state names; unknown implementations skip.
* Replaces the old lamp-result cache with a live scan on every call. Reuses callback storage without delaying lamp decisions or caching object classifications. Lamp-save buffer reuse remains enabled.
* Keeps world-light frame caching disabled. The legacy lamp interval/shared-cache settings no longer affect the live scan.

Validation: 120,000 simulated visibility calls across plain and xrRazom-rewritten variants, 1,000 live lamp-scan comparisons, lamp-save tests, and portable compatibility/diagnostic checks. See VALIDATION.md for the final in-game activation check. Tiny JIT rounding differences remain; no new FPS improvement or exhaustive live combat/co-op equivalence is claimed.

Install as a new MO2 mod and disable the older Sloptimizer version. Do not merge old startup files into it. Keep original target mods enabled. Anti-Lag by Jack_Harris is optional; place Sloptimizer below it if used. No engine binaries or GC-setting changes.
