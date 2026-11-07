# Lighting and visibility compatibility

## What 2.10.2 changes

Visibility and lamp optimization are enabled again with different safeguards. The world-light frame cache remains disabled. This is not a blanket restoration of the old lighting changes.

### Visibility: preserve the winning formula

The earlier replacement assumed Stealth Crash Fix's divisor 3.02 and standard-night multiplier 2. Atmospherics uses 2.35 and 4. Both functions had the same source path and line numbers, so that guard could accept a function whose detection tuning differed.

The repaired installer compiles reference bodies and compares LuaJIT instructions, constants, function shape, and upvalue names. It selects the replacement containing the matching formulas only after recognition. Unsupported code or unavailable introspection skips installation. The instruction check excludes the mutable function-entry opcode; nested callback prototypes, where present, are compared recursively. The original function's environment and private state cells remain shared. Recognition supports plain and xrRazom-rewritten versions of both formula variants. The reviewed xrRazom outer wrapper is preserved.

The compatibility reference is not executed for gameplay. It should be updated only after reviewing upstream changes, not to bypass a skipped component.

### Lamps: reuse storage, not decisions

The revised lamp path retains its visit and scan closures. It still calls the original-radius nearby-object scan on every request, reads current class membership and alive state, and reads the current flicker switch. It does not cache scan outcomes or object classifications. Re-entry falls back to the original; scan failures reset its busy state before propagating the error. Its installer also verifies the original body and nested callback.

This preserves the original transition timing instead of accepting the old 100 ms delay. The legacy `light_scan_cache` name enables this live path; interval/shared-cache settings are ignored. The old shared spatial scan helper is not installed.

Lamp-save buffer reuse remains enabled separately. It writes the current fuel condition on every original save call and falls back if the data manager changes.

### World lighting: original helper retained

The old once-per-frame cache can reuse a stale value if weather colors change during the frame. We have not established a useful replacement that both avoids those reads and guarantees freshness on this engine. `vision_light_frame` stays false.

## Evidence

The revised visibility installer was tested against both actual installed upstream files in 60,000 simulated calls, with the xrRazom wrapper and simulated avatar support. It exercised light states, day/night boundaries, crouching/movement, firing, visibility memory, marking and missing NPCs. Both variants had zero output differences beyond 1e-12 relative/absolute tolerance, with matching compared memory/debug/wrapper state. Tiny exact floating-point differences remain; the tolerance is a numerical comparison tool, not a guarantee about a native threshold at a boundary. Input hashes and counts are in `tests/ai-review-results.json`.

1,000 live lamp comparisons matched decisions and getter/scan order. Further checks cover class-table replacement, errors, re-entry, altered same-line functions, and unavailable introspection. Lamp saves have a separate 1,000-write comparison.

These fixtures model native-facing inputs, not whole combat encounters, engine scheduling or connected-peer replication. No new FPS claim is made. See VALIDATION.md for any game startup check.

## Reproduce

Install `tests/requirements.txt`, then run `python tests/run_checks.py`. For the separate upstream visibility audit, run `python tools/audit_visibility.py --mods-root "path/to/MO2/mods" --output ai-audit-results.json`. The tool reads the named installed originals and records hashes; it does not launch or change the game.

## xrRazom load-time rewrites

The multiplayer engine applies `xrr_gamma_ai.ltx` before compilation. Its visibility rules retain memory of multiple targets, key marking by observer/target when peers are present, and clear stale marking on skipped target branches. Keeping the outer avatar wrapper alone does not preserve these inner changes. The first strict in-game check rejected this rewritten body (774 versus 744 instructions); the guard was not relaxed. A separate recognized body was added with those exact rewrite rules retained. Unsupported future rewrites still skip.

An additional 60,000 calls used the actual installed rewrite rules, peer counts 0/1/2, alternating actor/avatar targets, and the reviewed wrapper. Both variants matched within numerical tolerance with matching compared state. The combined audits cover 120,000 calls; these are fixture counts, not live encounters. `tests/peer-visibility-results.json` contains the second result set. Add `--peer-rewrites` to the audit command to reproduce that mode. Connected-client combat still needs broader testing.
