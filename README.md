# Sloptimizer 9000 - readable source build

**[Download the MO2-installable ZIP](https://github.com/businessdrewski-hash/sloptimizer-9000-for-Stalker-GAMMA/releases/download/v2.10.1-readable/Sloptimizer-9000-2.10.1-readable.zip)**
**2.10.1-readable** is a maintainable source layout of the existing optimization pack. This readable release disables the visibility replacement, world-light frame cache and lamp-flicker cache following a compatibility audit. Other optimization defaults are retained. See [AI review](docs/AI-REVIEW.md). Each component has a descriptive filename and the same `install()` entry point.

## Read or edit the code

1. Start with [the module layout](docs/STRUCTURE.md).
2. Find the function you want in [the patch map](docs/PATCHES.md).
3. Edit its component under `gamedata/scripts`. Each file explains its purpose and the lifetime of its cached state.
4. Change switches in `sloptimizer_config.script`, then restart the game.

[Developer tools and checks](docs/DEVELOPMENT.md) are optional.

## Install

Close the game. Install this ZIP as a **new mod** in MO2 and disable any older Sloptimizer/optimization-pack version. Do not merge it into the old mod: runtime modules have been renamed and some split into separate files.

Enable it below the mods it optimizes. Anti-Lag is optional; if used, place this pack below it. Keep the original target mods enabled. This does not replace engine binaries or alter GC settings.

To carry over custom settings, use the switch names in the patch map rather than copying an older configuration file. To remove the pack, disable it and restart.

## Credits

Credit to the original authors of the GAMMA and xrRazom mods whose functions are optimized here. Anti-Lag is by Jack_Harris. The underlying mod logic retains its original authorship; this package does not grant new rights over it.

## Release notes and validation

See [release notes](docs/RELEASE-NOTES.md) and the [AI audit](docs/AI-REVIEW.md). Historical benchmark assets retained in the repository describe earlier versions, not this release’s conservative defaults.
