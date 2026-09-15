# ADR 0001: Open-source KMJ Forge under Apache-2.0

**Status:** Accepted  
**Date:** 2026-09-15

## Decision

KMJ Forge is maintained as a standalone public open-source project under Apache License 2.0.

## Rationale

- reusable across multiple KMJ software products;
- permissive open-source use;
- explicit patent grant;
- compatible with commercial and community adoption;
- separates generic engineering infrastructure from product repositories.

## Consequence

Product-specific source code and secrets must not be copied into KMJ Forge merely because those products use Forge workflows.
