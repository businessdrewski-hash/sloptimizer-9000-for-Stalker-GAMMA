# Module layout

Runtime modules are flat because X-Ray loads scripts by their module names. Logical separation is by responsibility, not development history.

## Entry points

* `sloptimizer_bootstrap.script` starts after the actor is available, checks optional dependencies and installs components independently.
* `sloptimizer_registry.script` lists components in installation order: module, switch, dependencies, argument and target functions.
* `sloptimizer_config.script` contains user-editable switches and intervals.

Each component exports `install()`, returning a boolean and a reason. Missing or unsupported targets skip without preventing other components from installing. Source guards belong to the component, alongside the assignment that applies its patch.

## Components

| Responsibility | Modules |
| --- | --- |
| Interaction markers | `sloptimizer_marker_updates`, `sloptimizer_marker_projection` |
| Lighting | `sloptimizer_light_flicker`, `sloptimizer_shared_light_scan`, `sloptimizer_world_lighting` |
| NPC visibility | `sloptimizer_visibility` |
| HUD displays | `sloptimizer_body_health_display`, `sloptimizer_radiation_display` |
| Multiplayer panel | `sloptimizer_party_session`, `sloptimizer_party_fields` |
| Items and devices | `sloptimizer_item_updates`, `sloptimizer_artifact_updates`, `sloptimizer_artifact_metadata`, `sloptimizer_device_updates` |
| Script infrastructure | `sloptimizer_callback_dispatch`, `sloptimizer_live_clock`, `sloptimizer_task_checks` |
| Geometry and persistence | `sloptimizer_ledge_rays`, `sloptimizer_ray_queries`, `sloptimizer_lamp_save_buffers` |

## Shared helpers

`sloptimizer_device_clock` makes a live clock accessor with a retained engine-device handle. It is shared by the lamp and party-session timers.

`sloptimizer_function_binding` binds a replacement to an original function's environment and **mutable upvalue cells**. Visibility and device updates use it. Their function bodies remain in their respective component files as readable Lua source strings, compiled once at installation. This lets them share private state with the original implementation. Copying the values instead would break later reassignment of state tables.

Edit those bodies in their component file. Preserve names that refer to upstream private state: the binder matches upvalues by name. There is no separate generated copy to edit or keep synchronized.

## Code conventions

* Pure `make_*` factories build wrappers or replacement functions; `install()` performs source checks and changes the target.
* Comments describe cache ownership, invalidation and assumptions next to the relevant logic.
* Engine/module names and upstream formula variable names are retained where they identify an external contract.
* Existing `gamma_opt_*` fields on individual UI/binder objects are private cached state, not old modules that must remain installed.
* Helpers that were not called during gameplay, such as the old anomaly-clock alias rewrite helper, have been removed.

## Installation order

Keep the registry order unless reviewing the dependency: ledge installation inspects the original callback registry before callback replacement; artifact metadata installs before artifact updates; party-session polling installs before party-field HUD recreation.

The refactor changes organization and names, not those ordering relationships. Restart after editing; there is no general-purpose hot-uninstall mechanism.
