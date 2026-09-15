# KMJ Forge

**KMJ Forge** is an open-source, evidence-driven software engineering framework for understanding, planning, building, testing, debugging, reviewing, and shipping software across languages, IDEs, platforms, and repositories.

> Status: **early development / v0.1.x bootstrap**

KMJ Forge is designed as a reusable engineering foundation for KMJ projects and for the wider open-source community. It is not tied to one product, model provider, programming language, IDE, or operating system.

## Principles

- Universal-first
- Free/open-source-first
- Local-capable
- Provider-agnostic
- Model-agnostic
- Language-agnostic
- IDE-agnostic
- Evidence over claims
- Safe autonomy
- Extensible through skills, tools, adapters, and schemas
- No destructive Git behavior without explicit authorization

## Repository map

| Path | Purpose |
|---|---|
| `src/kmj_forge/` | Minimal executable Python package and CLI bootstrap |
| `core/` | Core orchestration contracts, state-machine design, repository intelligence |
| `agents/` | Specialist agent role definitions and collaboration contracts |
| `skills/` | Reusable engineering procedures and skill specifications |
| `adapters/` | Language, model, tool, IDE, platform, and provider adapters |
| `schemas/` | Versioned JSON schemas and protocol contracts |
| `tools/` | Tool runtime contracts and utilities |
| `examples/` | Small, reproducible usage examples |
| `tests/` | Repository, protocol, and behavior tests |
| `benchmarks/` | Reproducible engineering task benchmarks |
| `docs/` | Architecture, workflows, decisions, plans, and roadmap |
| `.github/` | CI, security workflows, issue templates, and PR policy |

## Quick start

Requirements:

- Python 3.11+
- Git

```bash
git clone https://github.com/kmjtechno/kmj-forge.git
cd kmj-forge

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

python -m pip install -e .
python -m kmj_forge --version
python -m unittest discover -s tests -v
```

## Development workflow

1. Create a focused branch from `main`.
2. Reproduce or specify the requirement.
3. Make the smallest coherent change.
4. Run targeted tests.
5. Run the full relevant suite.
6. Review the diff.
7. Open a pull request with evidence.
8. Merge only after required checks pass.

Direct development on `main` is discouraged.

## Roadmap

The master engineering roadmap is stored at:

`docs/roadmap/KMJ_Forge_Master_Roadmap_v2.yaml`

The roadmap is a strategic architecture document. The implementation version of this repository starts at `0.1.0` and will advance through verified milestones.

## Relationship to KMJ products

KMJ Forge is intentionally a separate project.

Products such as **KMJ Calibration Pro** may consume Forge workflows, skills, tooling, and repository automation without becoming part of the Forge core.

## Security

Do not report security vulnerabilities through public issues.

See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
