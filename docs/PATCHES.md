# Patch map

This is the lookup table for code ownership. **Enabled** means the configuration permits installation; a missing dependency or failed guard can still make the component skip. Check the startup report to see what actually installed.

`module.function::name` identifies a private Lua upvalue inside that function, not a public field. The listed targets are the diagnostic observation points. Some components also register callbacks, replace an object environment, or recreate UI objects; those effects are described in the entries.

| Component | Default | Switch | Implementation |
| --- | --- | --- | --- |
| [Shared clock](#shared-clock) | Enabled | `shared_clock` | [live_clock](../gamedata/scripts/sloptimizer_live_clock.script) |
| [Markers](#markers) | Enabled | `markers` | [marker_updates](../gamedata/scripts/sloptimizer_marker_updates.script) |
| [Injury display](#injury-display) | Enabled | `injury_display` | [body_health_display](../gamedata/scripts/sloptimizer_body_health_display.script) |
| [Ledge rays](#ledge-rays) | Enabled | `ledge_ray_reuse` | [ledge_rays](../gamedata/scripts/sloptimizer_ledge_rays.script) |
| [Callback cache](#callback-cache) | Enabled | `callback_cache` | [callback_dispatch](../gamedata/scripts/sloptimizer_callback_dispatch.script) |
| [Ray query inputs](#ray-query-inputs) | Enabled | `ray_query_inputs` | [ray_queries](../gamedata/scripts/sloptimizer_ray_queries.script) |
| [Light scans](#light-scans) | Disabled | `light_scan_cache` | [light_flicker](../gamedata/scripts/sloptimizer_light_flicker.script) |
| [Offline peer panel](#offline-peer-panel) | Enabled | `offline_peer_panel` | [party_session](../gamedata/scripts/sloptimizer_party_session.script) |
| [Peer field cache](#peer-field-cache) | Enabled | `peer_field_cache` | [party_fields](../gamedata/scripts/sloptimizer_party_fields.script) |
| [Artifact metadata](#artifact-metadata) | Enabled | `artifact_kind_cache` | [artifact_metadata](../gamedata/scripts/sloptimizer_artifact_metadata.script) |
| [Item update](#item-update) | Enabled | `item_updates` | [item_updates](../gamedata/scripts/sloptimizer_item_updates.script) |
| [Artifact update](#artifact-update) | Enabled | `artifact_updates` | [artifact_updates](../gamedata/scripts/sloptimizer_artifact_updates.script) |
| [Projection](#projection) | Enabled | `marker_projection` | [marker_projection](../gamedata/scripts/sloptimizer_marker_projection.script) |
| [Radiation](#radiation) | Enabled | `radiation_display` | [radiation_display](../gamedata/scripts/sloptimizer_radiation_display.script) |
| [Task checks](#task-checks) | Enabled | `task_checks` | [task_checks](../gamedata/scripts/sloptimizer_task_checks.script) |
| [Vision world light](#vision-world-light) | Disabled | `vision_light_frame` | [world_lighting](../gamedata/scripts/sloptimizer_world_lighting.script) |
| [Visibility read reduction](#visibility-read-reduction) | Disabled | `visibility_reads` | [visibility](../gamedata/scripts/sloptimizer_visibility.script) |
| [Device read reduction](#device-read-reduction) | Enabled | `device_updates` | [device_updates](../gamedata/scripts/sloptimizer_device_updates.script) |
| [Lamp save buffers](#lamp-save-buffers) | Enabled | `lamp_save_buffers` | [lamp_save_buffers](../gamedata/scripts/sloptimizer_lamp_save_buffers.script) |

## Shared clock

Source: [`sloptimizer_live_clock.script`](../gamedata/scripts/sloptimizer_live_clock.script)  
Switch: `shared_clock`  
Component ID: `shared_clock`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: No optional script modules listed; see installer for engine/API requirements.

* `_G.time_global`

Replace the reviewed global wrapper; retain one device handle and read its clock live on every call. Avoid repeatedly constructing/requesting the device wrapper.

State/behavior: Global scope. Device lifetime assumptions matter; time values are not cached here. Anti-Lag anomaly upvalues are untouched.

## Markers

Source: [`sloptimizer_marker_updates.script`](../gamedata/scripts/sloptimizer_marker_updates.script)  
Switch: `markers`  
Component ID: `markers`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `utils_catspaw_hudmarks`, `ui_hud_dotmarks`

* `utils_catspaw_hudmarks.marker_is_offscreen`
* `utils_catspaw_hudmarks.dotproduct_for_pos`

Wrap the marker precheck; replace hover-direction calculation when a retained device is available. Suppress duplicate checks and move simple visible dots between full semantic checks, reusing vectors.

State/behavior: Full checks follow marker intervals. World positions can be stale between them; rich labels, pickup animations and custom end callbacks use the original pipeline. Check moving objects, hover, pickups, camera turns and PDA transitions.

## Injury display

Source: [`sloptimizer_body_health_display.script`](../gamedata/scripts/sloptimizer_body_health_display.script)  
Switch: `injury_display`  
Component ID: `injury_display`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `zzz_player_injuries`

* `zzz_player_injuries.actor_on_update::HUDUpdate`

Replace the private HUDUpdate upvalue with a throttling wrapper. Avoid redrawing the limb display on every actor update.

State/behavior: Display can lag by the configured interval (33 ms default). Health logic in actor_on_update still runs. Check healing previews and limb display transitions.

## Ledge rays

Source: [`sloptimizer_ledge_rays.script`](../gamedata/scripts/sloptimizer_ledge_rays.script)  
Switch: `ledge_ray_reuse`  
Component ID: `ledge_rays`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `demonized_ledge_grabbing`, `demonized_geometry_ray`, `axr_main`

* `demonized_ledge_grabbing.checkLedgeGrabbing`
* `demonized_ledge_grabbing.checkLedgeGrabbing::dgr`

Wrap the ledge callback, replace its dgr upvalue with a constructor proxy, and swap its actor callback registry entry at the original priority. Reuse sequential rays within one synchronous ledge check; produce only the result fields that the reviewed consumer reads.

State/behavior: Ledge movement is gameplay-sensitive. Scope must not escape or survive a check. Unknown arguments fall back to the original constructor. Common Anti-Lag variants fail the source guard and skip this component.

## Callback cache

Source: [`sloptimizer_callback_dispatch.script`](../gamedata/scripts/sloptimizer_callback_dispatch.script)  
Switch: `callback_cache`  
Component ID: `callback_cache`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `axr_main`

* `axr_main.make_callback`

Replace the dispatcher with a cached initial heap and reusable per-recursion traversal arrays. Avoid rebuilding ordering and temporary buffers for unchanged callback registries.

State/behavior: Priorities remain live during traversal; equal/non-numeric priorities and metatables fall back. Callback mutation, re-entry and errors are important regression cases. This is shared execution infrastructure.

## Ray query inputs

Source: [`sloptimizer_ray_queries.script`](../gamedata/scripts/sloptimizer_ray_queries.script)  
Switch: `ray_query_inputs`  
Component ID: `ray_query_inputs`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `demonized_geometry_ray`

* `demonized_geometry_ray.geometry_ray.get`

Wrap the public getter; retain the original visualization path. Remove copied input vectors while retaining an independently allocated endpoint and result table.

State/behavior: Assumes native setters copy their inputs. Queries still run. Check old results are not mutated by later queries, contact offsets and visualized rays.

## Light scans

Source: [`sloptimizer_light_flicker.script`](../gamedata/scripts/sloptimizer_light_flicker.script)  
Switch: `light_scan_cache`  
Component ID: `light_scans`  
Default: **Disabled - see [AI audit](AI-REVIEW.md)**  
Required modules: `bind_light_furniture`

* `bind_light_furniture.need_flicker`

Wrap need_flicker with a per-lamp cache and an optional shared negative spatial scan. Reduce repeated nearby-object searches and classification work across lamps.

State/behavior: Results can be stale for up to 100 ms by default. Emission bypasses the outer cache; not every switch transition does. Positive broad scans fall back to exact checks. Only the first 64 shared negative results are shadow-checked; a detected mismatch disables that shortcut, not the outer cache.

## Offline peer panel

Source: [`sloptimizer_party_session.script`](../gamedata/scripts/sloptimizer_party_session.script)  
Switch: `offline_peer_panel`  
Component ID: `offline_peer_panel`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `xrr_peer_hud`

* `xrr_peer_hud.UIPeerList.Update`

Add an actor_on_update poller; do not replace the Update method in this component. Remove the offline party HUD from render updates, restoring it when a session appears.

State/behavior: Session changes are polled every 500 ms. Calls AddDialogToRender/RemoveDialogToRender and forced Update; this is not just a numeric cache. Test connect/disconnect and HUD recreation. No multiplayer engine: skip.

## Peer field cache

Source: [`sloptimizer_party_fields.script`](../gamedata/scripts/sloptimizer_party_fields.script)  
Switch: `peer_field_cache`  
Component ID: `peer_field_cache`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `xrr_peer_hud`

* `xrr_peer_hud.UIPeerList.Update`

Replace the party-panel Update method; recreate an existing HUD; register an option-change cache reset. Skip unchanged widget writes, cache portraits and avoid hidden distance calculations.

State/behavior: Keeps the original 500 ms interval. Portrait cache keys are faction/outfit. Other addons modifying widgets or portrait dependencies may invalidate assumptions. Test connect/disconnect and changing peer state when editing this path.

## Artifact metadata

Source: [`sloptimizer_artifact_metadata.script`](../gamedata/scripts/sloptimizer_artifact_metadata.script)  
Switch: `artifact_kind_cache`  
Component ID: `artifact_metadata`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `item_artefact`

* `zz_item_artefact.SYS_GetParam`

Wrap SYS_GetParam in the artifact function environment only; register load/option-change cache resets. Cache static artifact kind metadata by section and nil/empty default separately.

State/behavior: Other parameter queries fall through. Runtime metadata edits outside the reset callbacks can be stale; global SYS_GetParam is not replaced.

## Item update

Source: [`sloptimizer_item_updates.script`](../gamedata/scripts/sloptimizer_item_updates.script)  
Switch: `item_updates`  
Component ID: `item_update`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `bind_item`

* `bind_item.item_binder.update`

Replace the binder update with a reviewed shortcut; keep first-update behavior on the original. Retain object identity and reduce unused bookkeeping. Share tracked state cells where supported.

State/behavior: Native binder update still runs every call. Uses/condition remain live. If tracked state cannot be shared, tracked items use the original path. Check reloads, multiuse items, condition changes and object lifetime assumptions.

## Artifact update

Source: [`sloptimizer_artifact_updates.script`](../gamedata/scripts/sloptimizer_artifact_updates.script)  
Switch: `artifact_updates`  
Component ID: `artifact_update`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `item_artefact`

* `item_artefact.artefact_binder.update`

Replace the reviewed zz_item_artefact update body in its original environment. Retain identity, reuse condition reads, skip unnecessary radiation casts and distance work for parented artifacts.

State/behavior: The replacement retains randomization, save restoration, physics and radiation branches. Check transitions, changing condition, fixed bones and radiation. No_rad keeps the original permanent-exclusion assumption.

## Projection

Source: [`sloptimizer_marker_projection.script`](../gamedata/scripts/sloptimizer_marker_projection.script)  
Switch: `marker_projection`  
Component ID: `projection`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `utils_catspaw_hudmarks`, `ui_hud_dotmarks`

* `utils_catspaw_hudmarks.world_to_ui`
* `ui_hud_dotmarks.dot_eye`

Replace projection and eye-direction helpers with private input scratch vectors. Avoid fresh input vectors for synchronous projection and direction calculations.

State/behavior: Projection output is still engine-owned; camera values remain live. Assumes synchronous calls and no retained scratch reference. Test nested/custom consumers before extending this reuse.

## Radiation

Source: [`sloptimizer_radiation_display.script`](../gamedata/scripts/sloptimizer_radiation_display.script)  
Switch: `radiation_display`  
Component ID: `radiation`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `actor_status`

* `actor_status.UIIndicators.Update`

Replace the radiation addon wrapper while continuing to call its saved base HUD Update. Skip identical fast-refresh text conversions/writes.

State/behavior: Normal refresh and radiation calculations remain. Private pass/slot state is initialized from the reviewed wrapper. Check gasmask slot changes, geiger requirements and competing text writers.

## Task checks

Source: [`sloptimizer_task_checks.script`](../gamedata/scripts/sloptimizer_task_checks.script)  
Switch: `task_checks`  
Component ID: `task_checks`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `task_manager`

* `task_manager.CRandomTask.task_complete`
* `task_manager.CRandomTask.task_fail`

Replace both reviewed task status methods with versions retaining a device wrapper. Avoid repeated device wrapper requests.

State/behavior: Actor, precache_frame, forced status and last status are read live. Task decisions are intended to match the original. Check forced complete/fail and missing tasks.

## Vision world light

Source: [`sloptimizer_world_lighting.script`](../gamedata/scripts/sloptimizer_world_lighting.script)  
Switch: `vision_light_frame`  
Component ID: `vision_world_light`  
Default: **Disabled - see [AI audit](AI-REVIEW.md)**  
Required modules: `visual_memory_manager`

* `visual_memory_manager.lights_lum`

Wrap the shared world-light helper with an engine-frame cache. Avoid recalculating the same shared lighting value for each visibility query.

State/behavior: A second lighting change within the same engine frame is not observed until the next frame. NPC-specific get_visible_value still executes. When editing this cache, check detection during lighting transitions.

## Visibility read reduction

Source: [`sloptimizer_visibility.script`](../gamedata/scripts/sloptimizer_visibility.script)  
Switch: `visibility_reads`  
Component ID: `visibility_read_reduction`  
Default: **Disabled - see [AI audit](AI-REVIEW.md)**  
Required modules: `visual_memory_manager`, `stealth_mcm`, `camp_lum`, `level_weathers`

* `visual_memory_manager.get_visible_value`
* `visual_memory_manager.get_visible_value::orig`

Replace the reviewed visibility body, or replace only the orig upvalue inside the reviewed xrRazom wrapper. Skip flashlight lookups whose results cannot be used by the current branch.

State/behavior: The body contains the Stealth Crash Fix formulas, which do not match the installed Atmospherics variant. Its old filename/line guard accepts both. Do not enable this component without fixing version matching and preserving the winning upstream formula. The multiplayer wrapper is retained, but that alone does not establish compatible detection behavior.

## Device read reduction

Source: [`sloptimizer_device_updates.script`](../gamedata/scripts/sloptimizer_device_updates.script)  
Switch: `device_updates`  
Component ID: `device_read_reduction`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `item_device`

* `item_device.device_binder.update`

Replace the reviewed device update body with shared original upvalue cells. Retain device identity and section while reading power/condition and parent live.

State/behavior: Power, NVG, emission and PDA branches remain. Object identity lifetime and compatibility with other binder overrides still require review.

## Lamp save buffers

Source: [`sloptimizer_lamp_save_buffers.script`](../gamedata/scripts/sloptimizer_lamp_save_buffers.script)  
Switch: `lamp_save_buffers`  
Component ID: `lamp_save_buffers`  
Default: **Enabled, subject to dependency and source checks**  
Required modules: `bind_light_furniture`, `hf_obj_manager`

* `bind_light_furniture.placeable_light_wrapper.save_data`

Wrap save_data; reuse one input table per lamp; call original if the manager function changes. Avoid one temporary condition table per lamp save.

State/behavior: Every condition write still happens. The reviewed manager copies fields synchronously. A manager that retains the table would invalidate reuse; the signature guard and runtime function check are important.

## Defaults and isolation

Active defaults: marker full-check intervals come from the original marker; the limb display interval is 33 ms; party polling and field refresh are 500 ms. Dormant settings: lamp caching would use 100 ms and world lighting would cache one frame if their disabled components were enabled. See [configuration](CONFIGURATION.md).

Use the named switch to disable a component, or add its component ID to `disabled_components` in the configuration file. Restart after changing it. Visibility lookups and world-light caching have independent switches (`visibility_reads` and `vision_light_frame`), as do device updates.

Source/version guards are in each installer. Update them only after reviewing the corresponding upstream function and its private state, not just its line numbers.
