# Model provider adapters

External model providers implement the provider-neutral `kmj_forge.models.ModelProvider` protocol.

Core routing never hard-codes provider names. Adapters discover model capabilities and return `ModelCapability` records to the dynamic registry.

Required adapter operations:

- `list_models`
- `generate`
- `stream`
- `tool_call`
- `cancel`
- `usage`
- `health_check`

Provider adapters must report pricing and availability truthfully. `FREE_ONLY` enforcement is owned by Forge policy, not by providers.
