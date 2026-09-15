# Core

The `core/` area defines implementation-independent contracts for KMJ Forge.

Planned responsibilities:

- orchestration state machine;
- repository intelligence;
- context assembly;
- planning and verification contracts;
- policy and approval gates;
- resumable execution state.

Core interfaces should remain small. Provider-, language-, IDE-, and platform-specific behavior belongs in adapters.
