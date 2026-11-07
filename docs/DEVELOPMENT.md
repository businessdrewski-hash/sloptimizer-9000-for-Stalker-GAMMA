# Developer tools

These tools are secondary to the source. Normal play does not require Python, a profiler, or a benchmark tool.

## Validate and build

From the extracted package root:

```text
python -m pip install -r tests/requirements.txt
python tests/run_checks.py
python tools/build_zip.py
```

The portable tests cover dependency handling, independent switches, diagnostic call semantics, split-module loading and shared mutable state. Local regression fixtures also exercise callback ordering, marker projection, artifacts, visibility, devices, lamp caching and rays. The validation note records this build's check; it is not an FPS comparison.

## Startup reports

The active appdata log directory receives `gamma-optimization-status.txt` and `sloptimizer-patch-report.txt`. These identify active/skipped components, exact target paths and observed function sources. A fresh report can be requested through a Lua debug executor:

```lua
sloptimizer_diagnostics.write_report()
```

Function identity does not observe every state change. A later replacement may be another component in this pack. Use the patch map and a component-off restart to isolate behavior.

## Optional timing

Keep `diagnostic_timing_targets = {}` for normal play. For a short measurement, set a target path in that list before restart, or use an existing Lua debug executor:

```lua
sloptimizer_diagnostics.start_timing('bind_light_furniture.need_flicker')
-- Perform the action you want to inspect.
sloptimizer_diagnostics.write_report()
sloptimizer_diagnostics.stop_timing('bind_light_furniture.need_flicker')
```

Export before stopping, which discards the totals. The wrapper measures inclusive elapsed microseconds using the engine timer: child work, encountered GC and instrumentation overhead are included. Nested totals overlap. This is not a per-mod GC ownership measurement or a frame-present recorder.

Timing is off by default. It changes call overhead and protected-call behavior, so do not use it on yielding coroutine paths or leave it on for a final performance benchmark. Stopping refuses to overwrite a later replacement by another writer.

## Editing safely

Keep the runtime registry, configuration and patch map aligned. Do not change a source guard merely to force installation on an unfamiliar version. Review cache lifetime, mutation and fallback assumptions first. For a gameplay issue, reproduce the same action with the relevant component disabled and restart between configurations.
