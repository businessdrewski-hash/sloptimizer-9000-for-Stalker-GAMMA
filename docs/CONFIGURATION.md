# Configuration

Edit [`sloptimizer_config.script`](../gamedata/scripts/sloptimizer_config.script) and restart the game. Installation happens once per session; changing a value afterward does not reliably undo or reconfigure an installed patch.

## Disable one component

Use its switch from the [patch map](PATCHES.md), for example:

```lua
marker_projection = false
```

Or add the component ID to the existing table:

```lua
disabled_components = {
    projection = true,
    injury_display = true,
}
```

These are alternative ways to disable a component. A true `disabled_components` entry takes precedence over an enabled switch. IDs and switches are not always identical: `projection` is the ID; `marker_projection` is its switch. Preserve existing entries when adding another.

## Timing and cache settings

| Setting | Shipped value | Effect |
| --- | --- | --- |
| `injury_display_interval_ms` | 33 | Limb display refresh interval; health calculations continue on the original update path. |
| `light_scan_interval_ms` | 100 | Legacy field; ignored by the repaired live lamp scan. |
| `shared_light_scan` | false | Legacy field; the repaired lamp installer does not use the shared scan helper. |
| `diagnostic_timing_targets` | `{}` | No timing wrappers installed. See [diagnostics](DIAGNOSTICS.md). |

Marker semantic-check intervals come from the marker implementation. Party-session polling and party-panel updates use 500 ms in their implementations; they are not config fields in this file.

## Lighting defaults

Keep `vision_light_frame = false`: shared world brightness is read through the original helper. `visibility_reads = true` now applies only to an instruction/constant-matched original and selects its matching formula variant; unsupported bodies skip. `light_scan_cache = true` is a legacy switch name that now enables callback reuse with a **live scan on every call**, not a cache. The old scan interval and shared-cache fields are unused. `lamp_save_buffers = true` remains separate and writes current condition values.

See the [AI audit and repair](AI-REVIEW.md) for scope and remaining limits.

## Migrating from older versions

| Old switch | Current switch |
| --- | --- |
| `v2_item_updates` | `item_updates` |
| `v2_artifact_updates` | `artifact_updates` |
| `v2_projection` | `marker_projection` |
| `v2_radiation` | `radiation_display` |
| `v2_task_checks` | `task_checks` |
| `native_read_reduction` | Split into `visibility_reads` and `device_updates`; use the current guarded visibility implementation rather than copying an old script. |

The module migration map is in [`tests/module-migration.json`](../tests/module-migration.json). Do not copy old `gamma_opt_*.script` modules into this package. Some object fields still have a `gamma_opt_` prefix; those are cached state used by the current code, not old files to install.
