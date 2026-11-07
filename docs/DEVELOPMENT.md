# Development workflow

## Make a focused edit

1. Use an isolated MO2 profile and a separate copy of this mod. Keep the original target mods enabled and disable older Sloptimizer versions.
2. Use the [patch map](PATCHES.md) to find the component. Read its installer and the actual winning upstream implementation.
3. Identify its contract: return values, side effects, mutable private state, callback order, ownership of reused objects, and when cached results expire or reset.
4. Edit the component itself. For an embedded body, edit the source string in that module. Keep upstream upvalue names intact unless also reviewing the binding helper.
5. Add a regression check that compares observable behavior with the original. Exercise mutation, missing objects, transitions, re-entry and fallback where relevant.
6. Run checks, build, install the new ZIP as a separate mod, restart, and verify its startup report before testing the changed behavior.

## Portable checks and packaging

From the extracted package root, with Python and a compatible Lupa wheel available:

```text
python -m pip install -r tests/requirements.txt
python tests/run_checks.py
python tools/build_zip.py
```

The default ZIP is written beside the extracted package folder. An explicit destination is supported:

```text
python tools/build_zip.py --output path/to/test-build.zip
```

The builder includes source, docs, tests and tools, excludes Python bytecode caches, and verifies archived file contents. It does not run the tests, install the mod, launch the game or publish to GitHub. The ZIP name is fixed in the tool; update it deliberately when preparing a new version.

| Included check | Main coverage |
| --- | --- |
| `test_optional_mods.py` | Missing/unsupported modules, initializer fault isolation, individual switches, and preservation of disabled world lighting and unsupported visibility/lamp targets. Its broad activation scenarios deliberately enable switches in fixtures; the shipping-default test is separate. |
| `test_diagnostics.py` | Return/error behavior, timing lifecycle, target ownership and unsupported timing cases. |
| `test_split_modules.py` | Module loading, live clock fallback and mutable upvalue sharing. |
| `test_lighting_contracts.py` | Live lamp decisions and read order, replaced state, re-entry, error recovery, and unknown-body rejection. |
| `test_lamp_saves.py` | Original versus optimized writes, per-lamp state, saved snapshots and manager replacement. |

The broader historical callback, artifact, marker and device suites used during development are not all bundled here. Do not interpret the portable runner as complete coverage of every optimization. See [validation](VALIDATION.md).

The separate `tools/audit_visibility.py` requires the named upstream mods in a supplied mods directory. It compares Lua behavior under simulated engine inputs and records input hashes; it does not simulate a whole combat encounter. Usage is in the [AI audit](AI-REVIEW.md).

## Add or change a component

Keep these aligned:

* Runtime: component `install()`, `sloptimizer_registry.script`, and `sloptimizer_config.script`.
* Fixtures: `tests/optional_components.json` and `tests/components.json`; update hardcoded component counts in tests when changing the registry size.
* Documentation: [patch map](PATCHES.md), [configuration](CONFIGURATION.md), source comments and validation scope.

The registry is authoritative for runtime order and target observation paths. JSON fixtures are not used by the game and must not be treated as a second live registry. Upstream filenames and line numbers are only partial guards: different bodies can share them.

## Measure after checking behavior

Use [diagnostics](DIAGNOSTICS.md) to locate expensive calls. Compare frame times with instrumentation disabled for performance claims. A lower allocation count or passing functional test does not by itself establish smoother frames. Do not combine nested inclusive timings into a total.
