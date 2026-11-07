# Troubleshooting a patch or conflict

## Find the code responsible

1. Read the current startup status. Confirm which components actually installed, rather than assuming an enabled MO2 mod installed every patch.
2. Find the affected function or symptom in the [patch map](PATCHES.md). Each entry links its installer, switch, dependencies and assumptions.
3. Read `install()` first to see the source guard and actual replacement assignment. Follow the `make_*` factory or embedded replacement body for runtime behavior.
4. If the target contains `::`, inspect that private upvalue. The public wrapper can keep the same identity while its inner function changes.

## Isolate a behavior change

Disable only the suspected component, restart, and repeat the same action in the same save/location. Record whether the symptom changes. Restart again when restoring it: editing configuration or reloading a script mid-session is not an uninstall.

| Symptom | First components to inspect |
| --- | --- |
| Dot position, hover or pickup prompts | Markers and Projection |
| Limb or radiation display | Injury display and Radiation |
| Party panel missing/stale | Offline peer panel and Peer field cache |
| Item condition, artifact radiation or device power | Item update, Artifact update, Artifact metadata and Device read reduction |
| Climbing or geometry queries | Ledge rays and Ray query inputs |
| Task completion or broad callback issues | Task checks and Callback cache |
| NPC detection or lamp transitions | Confirm world-light caching is disabled; inspect which visibility variant activated and isolate Visibility read reduction or Light scans with a restart. |

## A component skipped

Check its reason before changing anything. Source guards may reject an upstream update or another mod's replacement. Inspect MO2's winning file, the upstream body, private state and relevant API behavior. Do not change a line number just to force a match. Missing optional mods should skip their components without blocking the pack.

## An initializer failed

Read the error and ownership report, then inspect assignments made before the failing line. Installation is isolated per component but not automatically rolled back. Restart with the component disabled before testing a fix.

## Useful bug report details

Include the pack version, engine/build, affected original-mod versions, relevant MO2 conflicts, startup status and patch report, exact reproduction steps, and whether a component-off restart changes the result. For performance reports, state resolution, FPS cap, save/location, movement versus standing still and whether profiling was active. Remove personal paths or unrelated log content before sharing.
