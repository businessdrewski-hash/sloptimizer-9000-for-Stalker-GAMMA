# Lighting and AI visibility audit

## Decision

This readable release defaults `visibility_reads`, `vision_light_frame`, and `light_scan_cache` to false. The bootstrap leaves the original visibility function, its multiplayer wrapper/upvalue, world-light helper, and lamp-flicker query untouched. The experimental modules remain available for developers, but enabling them is not recommended based on these findings. The shared light scan is dormant while its parent light-scan component is disabled.

## Visibility replacement: confirmed compatibility defect

The installed Atmospherics and GAMMA Stealth Crash Fix variants both define `get_visible_value` at line 28. The old filename/line guard accepted either. The replacement was based on the Stealth Crash Fix formula: division by 3.02 and a standard-night multiplier of 2. Atmospherics uses 2.35 and 4. Replacing it can change detection buildup even though the flashlight shortcut itself preserves the reviewed branch logic. The current normal MO2 modlist lists enabled Atmospherics above enabled Stealth Crash Fix in its reverse-priority list. A live module source path alone cannot distinguish them because MO2 virtualizes both to the same path.

The expanded tests compared 30,000 calls against each installed original (60,000 total), including the actual xrRazom wrapper with simulated avatar-call support. They varied day/night boundaries, underground/camp lighting, torches, handheld lights, NPC classes, crouching, motion, firing, memory transitions, marking and missing NPCs. Private state was changed through Lua closures with JIT enabled.

Stealth Crash Fix had no differences outside a 1e-12 numerical tolerance; 45 exact comparisons differed by rounding. Atmospherics had 7,764 differences beyond that tolerance. These are fixture results, not a percentage of live encounters. The test compares output, memory/debug side effects and wrapper calls. It does not model the whole native detection accumulator or network implementation.

## World-light frame cache: conditional behavior difference

The original helper reads current weather sun and hemisphere colors. If those change between two calls in the same frame, the cached helper keeps the earlier value. A controlled input transition reproduced different detection increments, and advancing the frame restored the live value. The public engine source reads CurrentEnv and exposes weather setters; it does not establish the update ordering of the closed multiplayer build. We have not established that this scenario occurs in normal gameplay, so the cache is disabled rather than described as behavior-identical.

## Lamp-flicker cache: bounded transition delay

A controlled psi-influence transition at 50 ms remained cached false until the 100 ms expiry; the emission bypass still responded immediately. The upstream caller starts/stops an actual lamp color animator from this result. That demonstrates different lamp timing, not a measured NPC detection change. The cache is disabled to preserve the original query timing.

## Validation limits

The conservative defaults are checked through the actual bootstrap: all three targets and the multiplayer wrapper's original-function reference remain unchanged. Portable regression checks are included. This review did not run a new in-game combat/stealth trial and does not claim a new FPS result. Other components remain subject to their documented assumptions. The audit did not modify installed game files or engine binaries. This release includes the resulting conservative defaults.

## Reproduce the differential audit

Install `tests/requirements.txt`, then run `python tools/audit_visibility.py --mods-root "path/to/MO2/mods" --output ai-audit-results.json`. This uses the two named installed upstream scripts and xrRazom wrapper as inputs; their hashes are recorded. It does not launch or alter the game. The fixtures exercise native-facing calls through mocks. A future upstream version can change these assumptions, so review failures instead of changing expected values blindly.

## Retained lamp optimization

`lamp_save_buffers` stays enabled. It reuses a per-lamp input table for save-data updates; it does not cache brightness, flicker decisions, fuel values or detection results. Each save still writes the current condition through the original synchronous data manager. If that manager is replaced, the wrapper falls back to the original save function. The focused regression test checks changing fuel, separate lamps, retained save snapshots and manager replacement.
