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
| `light_scan_interval_ms` | 100 | Dormant while `light_scan_cache = false`. Would control lamp-result cache lifetime. |
| `shared_light_scan` | true | Dormant while `light_scan_cache = false`; not an independently installed component. |
| `diagnostic_timing_targets` | `{}` | No timing wrappers installed. See [diagnostics](DIAGNOSTICS.md). |

Marker semantic-check intervals come from the marker implementation. Party-session polling and party-panel updates use 500 ms in their implementations; they are not config fields in this file.

## Lighting defaults

Keep `visibility_reads`, `vision_light_frame`, and `light_scan_cache` false. Their experimental implementations are retained for inspection, not recommended opt-ins. The [AI audit](AI-REVIEW.md) explains the formula mismatch and cache freshness risks. `lamp_save_buffers = true` is separate: it reuses save input storage while writing current condition values.

## Migrating from older versions

| Old switch | Current switch |
| --- | --- |
| `v2_item_updates` | `item_updates` |
| `v2_artifact_updates` | `artifact_updates` |
| `v2_projection` | `marker_projection` |
| `v2_radiation` | `radiation_display` |
| `v2_task_checks` | `task_checks` |
| `native_read_reduction` | Split into `visibility_reads` and `device_updates`; retain the new disabled visibility default. |

The module migration map is in [`tests/module-migration.json`](../tests/module-migration.json). Do not copy old `gamma_opt_*.script` modules into this package. Some object fields still have a `gamma_opt_` prefix; those are cached state used by the current code, not old files to install.
