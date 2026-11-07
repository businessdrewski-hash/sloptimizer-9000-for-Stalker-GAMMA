Readable source release with conservative lighting defaults.

### What changed
* Descriptively named component modules, consistent installation entry points, shared helpers, exact patched-function documentation and separate developer diagnostics.
* Retained lamp-save buffer reuse: every current condition value is still written through the original manager. The original save path is used if that manager changes.
* Disabled the visibility replacement, world-light frame cache and lamp-flicker result cache by default. The audit found that the old visibility guard could accept Atmospherics while replacing its different detection formula. The caches also have freshness tradeoffs. Other optimization defaults remain enabled.
* Independent switches and startup reporting make it easier to trace changes and isolate problems. Profiling stays off by default.

### Install
Download **Sloptimizer-9000-2.10.1-readable.zip** below. Close the game, install it as a **new MO2 mod**, and disable the older Sloptimizer version. **Do not merge into an older installation**: script names changed and old startup files must not remain active. Place it below the original mods it optimizes and Anti-Lag, if used. Anti-Lag by **Jack_Harris** is optional. Keep original mods enabled.

### Validation and limits
Portable compatibility, component isolation, diagnostics, shared-state and lamp-save checks passed. The lighting audit compared 60,000 visibility calls against two installed upstream variants. Tests confirm the disabled components leave original visibility, its multiplayer wrapper, world lighting and lamp queries untouched.

The preceding readable build passed one in-game activation/stability check. The final conservative defaults have not had a new FPS benchmark or exhaustive live combat/co-op test. Historical performance charts are not measurements of this release. This remains an experimental Lua-only pack; no engine replacement or GC-setting changes.

See `docs/STRUCTURE.md`, `docs/PATCHES.md`, and `docs/AI-REVIEW.md` for the source layout, exact function targets and audit findings.
