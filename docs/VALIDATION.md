# Validation scope

## Current 2.10.2-readable checks

The portable suite passed optional-component and isolation cases, diagnostic lifecycle checks, shared-state tests, 1,000 lamp-save comparisons and 1,000 live lamp-scan comparisons. Altered same-line visibility/lamp functions and unavailable introspection were rejected. World-light frame caching stays disabled.

The upstream visibility audit compared 60,000 calls against the two installed originals. A second 60,000-call audit applied the actual xrRazom rewrite rules and alternated player targets with peer counts 0/1/2. Both variants matched within 1e-12 relative/absolute tolerance and matched compared memory/debug/wrapper state. This tolerance separates floating-point rounding from larger differences; it is not a gameplay-impact threshold. See AI-REVIEW.md and the JSON results under tests.

## Game checks

Initial isolated runs verified the live lamp scan and correctly skipped unrecognized xrRazom visibility instructions. Diagnostic inspection identified the engine's load-time rewrites; the current candidate recognizes those separately. The final 60-second isolated run completed with Atmospherics + xrRazom visibility and live lamp scans ACTIVE, world-light caching DISABLED, and no fatal or startup errors. The ledge component skipped its unsupported implementation. All 26 runtime files match that run. Temporary test files were restored after exit; no peers were connected. See `tests/live-validation.json`.

## Limits

There is no controlled FPS comparison for this release and no exhaustive combat, stealth or connected-client test. The older benchmark charts describe earlier versions. ACTIVE means an installer succeeded, not that all gameplay has been validated. The fixture harness models engine-facing inputs; it does not implement the whole native detection accumulator or networking.
