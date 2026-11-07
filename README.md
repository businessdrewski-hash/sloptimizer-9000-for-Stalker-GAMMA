# Sloptimizer 9000 for Stalker GAMMA

**[Download v2.10.1-readable for MO2](https://github.com/businessdrewski-hash/sloptimizer-9000-for-Stalker-GAMMA/releases/download/v2.10.1-readable/Sloptimizer-9000-2.10.1-readable.zip)**

Sloptimizer reduces repeated Lua work and temporary allocations in supported GAMMA scripts. This experimental release organizes each optimization into a named module with independent configuration and startup reporting. It does not replace engine files or change GC settings.

The visibility replacement, world-light frame cache and lamp-flicker result cache are **disabled by default** after the lighting audit. Lamp-save buffer reuse remains enabled. See [what the audit found](docs/AI-REVIEW.md).

## For modders

| I want to... | Start here |
| --- | --- |
| Understand how the pack starts and applies patches | [Architecture and code layout](docs/STRUCTURE.md) |
| Find which function a component changes | [Patch map](docs/PATCHES.md) |
| Disable a component or understand a setting | [Configuration](docs/CONFIGURATION.md) |
| Trace a conflict or gameplay regression | [Troubleshooting](docs/TROUBLESHOOTING.md) |
| Edit a component, run checks and build a ZIP | [Development workflow](docs/DEVELOPMENT.md) |
| Inspect ownership reports or time an active patch | [Diagnostics](docs/DIAGNOSTICS.md) |
| See what has and has not been tested | [Validation](docs/VALIDATION.md) |

## Install or update

1. Close the game and install the ZIP as a **new mod** in MO2.
2. Disable older Sloptimizer versions. **Do not merge** with an older installation: module names changed, and old startup scripts must not remain active.
3. Place this mod below the original mods it optimizes in MO2's left pane. Keep those original mods enabled.
4. Anti-Lag by **Jack_Harris** is optional. If used, place Sloptimizer below it. A Sloptimizer component can skip an unsupported Anti-Lag variant rather than replacing it.
5. Launch and allow about ten seconds after loading. Check `appdata/logs/gamma-optimization-status.txt` for the installed components.

No individual optional mod, including Interaction Dots or xrRazom, is required for the whole pack. Components check their own prerequisites. Supported versions still matter; missing or incompatible targets are not automatically optimized.

To remove the pack, disable it in MO2 and restart. To migrate custom settings, consult [configuration](docs/CONFIGURATION.md) rather than copying the old config file wholesale.

## Scope and credits

This build has portable checks and a prior readability-build startup test; the conservative lighting defaults have not had a new FPS benchmark or exhaustive live combat/co-op test. Historical benchmark assets in the repository describe earlier versions. See [validation](docs/VALIDATION.md) and [release notes](docs/RELEASE-NOTES.md).

Credit to the original GAMMA and xrRazom mod authors whose functions this pack adapts. Anti-Lag is by Jack_Harris. Original mod logic retains its original authorship; this package does not grant new rights over it.
