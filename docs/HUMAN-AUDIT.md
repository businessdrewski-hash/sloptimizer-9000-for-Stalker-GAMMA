# Maintainer audit

**Version: 2.10.3-readable, based on v2.10.2-readable.**
This audit records implementation contracts, compatibility changes and remaining
risks. Baseline release records do not validate subsequent candidate changes.

**Latest follow-up:** [Compatibility hardening pass](COMPATIBILITY-PASS.md) records subsequent fixes and tests.

## Start here

1. Find the subsystem in the module map below.
2. Read its public `install` function: it identifies the original function and
   the conditions under which the patch is applied.
3. Read its `make_*` helper or replacement body: that is the runtime algorithm.
4. Check the exact targets in [the registry](../gamedata/scripts/sloptimizer_registry.script).
5. Review the relevant tests before editing. Tests with mocked engine objects
   establish Lua behavior, not native pointer validity or connected-game safety.

The source of truth for whether a patch activated is the generated game status
report. An enabled checkbox alone does not prove activation. Unknown versions
should remain on their original implementation.

## Categories used in this audit

| Category | Meaning | Action |
|---|---|---|
| Simplify | Code protects against an unsupported/impossible condition, or carries unused work | Remove locally and compare supported behavior |
| Retain | Complexity protects a specific contract | Keep it and explain that contract |
| Harden | A reproducible assumption failure or weak compatibility boundary | Add focused protection and regression tests |
| Retire | Disconnected or disabled experimental code/configuration | Keep disabled; remove from a future release after documenting migration |
| Investigate | Plausible risk without sufficient evidence | Record assumptions; do not label it a confirmed crash cause |

## Rules for future edits

### Engine APIs versus optional dependencies

On the supported engine, `device()` and vector constructors are engine APIs.
Do not add repeated existence/type probes or silent fallback clocks around them.
The inspected public source exports the device, its clock method and frame field.
That source is evidence for the supported API contract, not a complete audit of
the closed multiplayer engine.

Optional Lua modules, multiplayer-only APIs, modded function bodies, actor state,
UI widgets and live entity lifetimes are different. Their checks are meaningful.
Do not remove them just to reduce line count. A Lua userdata being non-nil does
not mean the underlying C++ object is still valid.

### Ownership and caching

| Value | Reasonable lifetime | Constraint |
|---|---|---|
| Engine device wrapper | Supported engine session | Read clock/camera/state live; singleton lifetime is an engine assumption |
| Binder object | Current update | Read `self.object` again next update; do not keep an old object/ID/section |
| Scratch vector | One owner or synchronous non-reentrant operation | Never hand shared scratch to a consumer that retains or mutates it later |
| Returned position/result | Caller-owned contract | Keep independent results when callers may retain them |
| UI widget | Its owning UI lifetime | Check current slot/widget; native destruction is not detectable with a simple nil check |
| Config metadata | Until documented invalidation | Include relevant defaults in keys and reset on applicable changes |
| Task/entity state | Current evaluation | Do not cache decisions across gameplay or network mutations |

`vector()` creates mutable vector data, not merely another reference to an engine
singleton. Its reuse therefore requires a stronger ownership argument than a
cached device wrapper.

### Wrappers and patch scope

- Prefer local optimizations in the owning upstream mod when possible.
- Use an external wrapper when preserving an upstream function or its mutable
  state requires it. A short wrapper with a documented purpose is not inherently wasteful.
- Do not replace a global helper to fix one caller unless its broader scope is
  intentional, documented, independently switchable and tested.
- The global clock patch still exists in this working copy. Simplifying its
  setup does not resolve the broader compatibility question about replacing it.
- Do not remove the DotMarks patches until the actual upstream utility update
  is available and its behavior/coverage have been checked.

### Compatibility checks

A source filename and line range identify a likely version, not its executable
behavior. Another mod can change that body without changing its starting line.
Prefer a comparison of the reviewed body/constants/upvalue layout before a
replacement that bypasses the original. Use the shared binding helper where
needed; do not build a second generic patch framework.

Mutable upvalues must remain shared cells when upstream code can replace their
values. Copying their current values is not always equivalent.

## Module map: all 26 runtime scripts

Names below omit the `sloptimizer_` prefix and `.script` suffix. All files are
in [gamedata/scripts](../gamedata/scripts).

| Subsystem / module | Purpose and ownership | Audit disposition |
|---|---|---|
| Startup: `bootstrap` | Installs components once; records activation | Retain fault isolation. Installer errors are **not transactions**: partial writes are not rolled back. Avoid modifying functions before all validation passes. |
| Startup: `registry` | Lists dependencies, switches, targets and order | Retain one explicit registry. Removed unused interval argument to live light scanner. Ordering is part of compatibility. |
| Startup: `config` | User switches | Annotated misleading legacy light-cache/interval settings. Do not rename public keys without migration notes. |
| Review: `diagnostics` | Patch provenance and opt-in inclusive timings | Retain. Timer API checks handle real engine differences; nested timers and return/error preservation are purposeful. No default timing instrumentation. |
| Binding: `function_binding` | Shares mutable upvalues; compares reviewed executable bodies | Retain. Dynamic compilation/reference bodies support private state and compatibility. Do not remove because the file is long. |
| Clock: `device_clock` | Local live-clock closure | Simplified to one device request and live method calls; removed nonexistent-engine fallbacks. |
| Clock: `live_clock` | Replaces global `time_global` | Simplified redundant engine checks and impossible post-assignment identity test. Retained upstream-ownership check. Global replacement scope remains a review item. |
| Markers: `marker_updates` | Schedules full checks and smooth visual positioning | Removed redundant device checks and unreachable no-device branch. Kept frame capability fallback, pickup/custom-marker paths and rollback handling. Frame-clock deduplication is not a universal guarantee of one call per rendered frame. |
| Markers: `marker_projection` | Reuses synchronous projection/hover scratch | Retain ownership distinction between inputs and returned outputs. Upstream matching is still line-based. Verify upstream coverage before removing overlapping patches. |
| HUD: `body_health_display` | Limits only captured HUD refresh helper | Retain wrapper and clock rollback behavior. Upstream-body compatibility could be stronger. Health logic must remain outside the limiter. |
| HUD: `radiation_display` | Avoids unchanged text writes | Hardened absent label/icon handling. Missing-widget assumption was also upstream. Pass/slot state is copied at install; external writers would need further examination. |
| Multiplayer HUD: `party_session` | Suspends offline panel rendering | Removed unused `last_hud` reference. Retain real multiplayer/API checks. Absent renderer now defers work; native UI lifetime still requires live testing. |
| Multiplayer HUD: `party_fields` | Skips unchanged field writes and hidden-distance work | Hardened widget identity tracking with weak references. Portrait-key coverage and four-slot assumption still need matching upstream version. |
| Items: `item_updates` | Skips unused bookkeeping; tracks uses/condition | Hardened current-object access and exact reviewed-body check. Retain fallback when private tracked state cannot be shared. |
| Artifacts: `artifact_updates` | Removes duplicate reads within original update flow | Removed persistent object/ID/section retention and unused local. Keep physics/radiation frequency. Missing physics-bone result is an inherited unchecked assumption; not silently altered. |
| Artifacts: `artifact_metadata` | Caches static kind metadata | Retain default-sensitive cache keys and invalidation. Runtime config edits outside known invalidation remain a compatibility assumption. |
| Devices: `device_updates` | Optimized device power/PDA/NVG body | Removed persistent object identity. Retain shared upvalues and gameplay branches. Exact-body compatibility added in the follow-up pass. |
| Lamps: `lamp_save_buffers` | Reuses per-lamp synchronous input table | Retain independent lamp ownership and manager-replacement fallback. Same-lamp re-entry/native retention is not proven safe by nil checks; body identification is still line-based. |
| Lamps: `light_flicker` | Reuses visit closure, scans live every call | Retain strict body match, live mutable state and re-entry fallback. This is not a TTL cache. |
| Lamps: `shared_light_scan` | Old spatial negative-result cache experiment | Retire from future production package. No startup installer uses it now; standalone code is not approved for gameplay. Left disconnected. |
| Lighting: `world_lighting` | Disabled per-frame world-light cache | Keep disabled. Do not simplify into an active behavior change. |
| Visibility: `visibility` | Recognized visibility variants with fewer unused reads | Retain reference bodies, constants, multiplayer wrapper and shared state. Large file size serves exact compatibility. Native accumulator/network behavior still needs live validation. |
| Dispatch: `callback_dispatch` | Initial heap cache and traversal buffers | Retain depth-local buffers, error cleanup and ambiguous-order fallback. Generic simplification can change callback execution ordering. Exact dispatcher/sort-body checks and fallback on later public sort replacement added in the follow-up pass. |
| Tasks: `task_checks` | Live task results with retained device wrapper | Removed engine-wrapper existence check. Retain actor/loading gates and source ownership checks. |
| Geometry: `ray_queries` | Avoids copied ray inputs | Retain independent endpoint/results and visual-query fallback. Depends on native setters copying input values. Line-based body check remains a review item. |
| Movement: `ledge_rays` | Reuses rays within synchronous ledge evaluation | Retain nesting/error cleanup and unknown-option fallback. Wrapper drops return values; reviewed caller does not use them, but an extended caller might. Minimal result fields depend on the reviewed consumer. |

## Candidate changes

The earlier crash pass changes are preserved: current binder-object reads,
missing radiation-widget checks, and strict item-body matching.

This readability pass additionally:

- Removes redundant engine existence/method checks in clock, marker and task setup.
- Removes an unreachable marker no-device path after successful installation.
- Removes the impossible global-clock "assignment did not change identity" check.
- Removes unused artifact and party-panel locals.
- Labels inert legacy configuration and removes its unused argument forwarding.
- Identifies the build version in its startup report.

No global optimization was silently disabled, no multiplayer protocol changed,
and no experimental lighting cache was enabled. This cleanup is primarily about
readability and correct contracts, not a promised FPS increase.

## Tests and limitations

Run the existing portable suite, the crash regression suite and the new cleanup
comparison suite with LuaJIT 2.0/Lupa available:

```text
python tests/run_checks.py
python tests/test_crash_audit.py
python tests/test_simplification.py
python tests/test_compatibility_hardening.py
```

The two audit-specific suites currently need the neighboring baseline folder
`Sloptimizer-9000-2.10.2-readable`; this is a local audit workspace, not yet a
self-contained release/test kit.

Results: all passed. The cleanup suite compares 500 marker-update steps against
the baseline, including repeated calls, clock rollback, hidden HUD/PDA, pickup
exceptions and offscreen transitions. It also checks one device acquisition and
live clock values. Crash tests reproduce prior failures and check the candidate fixes.
Existing tests cover optional components, diagnostics, shared state, lamp saving
and live light-scan behavior.

An initial informal gameplay walkthrough reported normal behavior. This is not
a controlled performance test, connected multiplayer validation or proof of
native pointer safety. Existing live-validation JSONs describe the baseline,
not the candidate changes.

## Priority for the next maintainer pass

1. For crash diagnosis, collect a matching log/dump, exact versions and
   reproduction steps. Fixture failures alone do not identify a live crash.
2. Add reviewed-body matching to remaining high-impact replacement installers,
   beyond the now-hardened device/artifact updates and shared callback dispatch.
3. Test binder destruction/recreation and inventory/UI replacement in game;
   inspect party-field invalidation if UI widgets are replaced.
4. When the upstream utility update is available, remove verified overlapping
   marker patches and reassess whether the global clock override is still needed.
5. Remove retired experiment files/inert settings from a future clean package,
   update diagnostics/config migration and make audit tests self-contained.

Do not combine these into an unreviewable wholesale rewrite. Keep changes grouped
by subsystem, with exact targets, assumptions and tests visible beside each patch.
