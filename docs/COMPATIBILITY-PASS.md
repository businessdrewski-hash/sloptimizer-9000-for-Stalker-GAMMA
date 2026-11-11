# Compatibility hardening pass

**Version: 2.10.3-readable.**

## Changes

| Area | Protection added | Runtime effect |
|---|---|---|
| Artifact update | Compare reviewed body/constants/upvalues before replacing | Unknown variants keep their original update |
| Device update | Same reviewed-body validation | Unknown variants keep their original power/NVG/PDA logic |
| Callback dispatch | Validate dispatcher, sorting entry point, comparator, heap, comparator wrapper, ordered sift and captured floor function | Unknown sort implementations are not bypassed |
| Callback dispatch after installation | Check public sorting function identities | If another mod replaces them, use the original dispatcher |
| Party HUD fields | Include current widget identity in cached writes | Rebuilt widgets receive their initial value even if unchanged |
| Party HUD references | Weak-value widget cache | Cache does not keep removed UI wrappers alive |
| Offline party renderer | Check availability of the current HUD renderer | Defer panel work while renderer is absent; retry on a later poll |

The preceding crash pass remains included: live binder-object reads, absent
radiation-widget checks, and stronger item-update matching. No arbitrary engine
calls are hidden behind error-swallowing wrappers.

## Maintainer map

- `sloptimizer_function_binding.matches_body`: shared installation-time check.
  Compilation/comparison failures return false; they do not replace the target.
- `sloptimizer_device_updates` and `sloptimizer_artifact_updates`: reviewed
  upstream source bodies live next to the replacement/installer for inspection.
- `sloptimizer_callback_dispatch.reviewed`: references for each covered sorting
  component. Validation occurs before assigning the dispatcher replacement.
- `sloptimizer_party_fields.set_field`: widget identity is tracked separately
  from cached values. Failed widget writes do not commit the new cache values.
- `sloptimizer_party_session.make_peer_poller`: obtains a live renderer before
  changing the panel's rendering registration.

These changes do not make every installer transactional. Earlier installations
can still have partial side effects if a later operation fails. Other line-only
guards also remain; broader compatibility is not claimed.

## Validation

All passed:

- Six compatibility test methods: known/changed binder bodies; known/changed
  sorting helpers; later public sorting replacement; unavailable comparison
  support; rebuilt widgets and weak ownership; absent/recreated HUD renderer.
- Eight crash-audit test methods, including reproduction of baseline failures.
- Two simplification methods, including 500 marker-update comparisons.
- Existing portable suite: optional dependencies, component switches, diagnostics,
  split module/upvalue handling, lamp saves and live lamp scans.

Run `python tests/test_compatibility_hardening.py` in the existing Lupa/LuaJIT
test environment. Set `GAMMA_SCRIPTS` to the reviewed GAMMA `gamedata/scripts` directory.
This test requires upstream sorting source files; they are not bundled.

## Remaining uncertainty

An initial informal gameplay walkthrough reported normal behavior. Connected
multiplayer behavior and native object lifetimes remain unverified. Mock tests
cannot reproduce every native destruction or pointer-lifetime condition. Crash
attribution requires matching logs, versions and reproduction steps. No measured
FPS improvement or general crash-elimination claim is made.

The inherited artifact fixed-bone assumptions remain unchanged: silently skipping
physics work without a matching failure report could alter gameplay. This pass
does not disable or weaken the native engine's own error checks.
