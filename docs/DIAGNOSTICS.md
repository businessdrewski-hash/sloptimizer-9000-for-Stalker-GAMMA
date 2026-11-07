# Diagnostics

## Startup reports

After installation, the active game's appdata log directory receives:

| File | What to read |
| --- | --- |
| `gamma-optimization-status.txt` | One result per component and the reason it installed, skipped or failed. |
| `sloptimizer-patch-report.txt` | Component IDs, target paths and function identities before installation, afterward and at report time. |

`ACTIVE` means the installer succeeded, not that every branch or gameplay case has been tested. `SKIPPED` usually means a missing dependency or unsupported implementation. `DISABLED` means configuration prevented installation. `ERROR` means an initializer raised an error; other components still get their installation attempt. There is no general transaction rollback, so inspect the target if an installer fails after making changes.

The source paths can be MO2's virtual paths. Two different winning files can appear under the same path and line number; the visibility audit demonstrated why those alone do not prove compatibility.

Refresh the ownership report from an existing Lua debug executor:

```lua
sloptimizer_diagnostics.write_report()
```

`CHANGED_SINCE_COMPONENT_INIT` means the current function differs from the recorded post-install function. It may be another mod, a later component, or a timing wrapper. `SAME_AS_AFTER_INSTALL` does not inspect changed upvalues or cached data and does not prove identical behavior.

## Optional timing

Timing is off for normal play. It only starts for an eligible target changed by an active component whose identity still matches. For example, if Lamp save buffers is ACTIVE:

```lua
local ok, reason = sloptimizer_diagnostics.start_timing(
    'bind_light_furniture.placeable_light_wrapper.save_data'
)
printf('Timing: %s, %s', tostring(ok), tostring(reason))
-- Perform the action, then export before stopping.
sloptimizer_diagnostics.write_report()
sloptimizer_diagnostics.stop_timing(
    'bind_light_furniture.placeable_light_wrapper.save_data'
)
```

For startup timing, put that target string in `diagnostic_timing_targets` and restart. A disabled component's target will not become eligible just because it is named there. Export before stopping: stopping discards its totals. Stopping refuses to overwrite a later function replacement.

Elapsed microseconds are **inclusive**: child calls, encountered collection and instrumentation overhead can be included. Nested targets overlap, so their totals must not be added as independent costs. This is neither a frame-presentation recorder nor a measurement of which mod owns GC cleanup time. Allocations and timing answer different questions.

The wrapper adds protected-call overhead. Do not use it on yielding coroutine paths. Leave timing off for gameplay and final FPS comparisons.
