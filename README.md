<div align="center">

# KMJ Forge

### Evidence-driven software engineering for humans and AI.

[![GitHub stars](https://img.shields.io/github/stars/kmjtechno/kmj-forge?style=flat&logo=github)](https://github.com/kmjtechno/kmj-forge/stargazers)
[![License](https://img.shields.io/badge/license-Apache--2.0-ED010B)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-111111?logo=python)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-early%20development-ED010B)](#current-status)

**Understand → Plan → Build → Test → Debug → Review → Ship**

[Quick start](#quick-start) · [Architecture](#repository-map) · [Roadmap](#roadmap) · [Contributing](CONTRIBUTING.md) · [KMJ TECHNO](https://kmjtechno.com)

</div>

---

**KMJ Forge** is an open-source, evidence-driven software engineering framework for understanding, planning, building, testing, debugging, reviewing, and shipping software across languages, IDEs, platforms, repositories, and AI model providers.

It is designed as a reusable engineering foundation for KMJ projects and the wider open-source community—not as a wrapper around one model, one editor, or one vendor.

## Why KMJ Forge

Modern AI coding can move fast, but speed without verification creates fragile software. Forge is built around a different rule:

> **Autonomy should increase only when evidence, safety boundaries, and verification increase with it.**

The project aims to make engineering workflows more reproducible and portable by separating core orchestration from models, tools, languages, IDEs, and infrastructure providers.

## Principles

- **Universal-first** — reusable across repositories and product types.
- **Free/open-source-first** — Apache-2.0 core that can be inspected and extended.
- **Local-capable** — workflows should not require a single hosted provider.
- **Provider-agnostic** — avoid lock-in to one cloud or API.
- **Model-agnostic** — compatible architecture for multiple AI systems.
- **Language-agnostic** — engineering contracts should generalize beyond one stack.
- **IDE-agnostic** — workflows should survive editor changes.
- **Evidence over claims** — tests, diffs, logs, schemas, and reproducible checks matter.
- **Safe autonomy** — higher-risk actions require stronger boundaries.
- **Extensible** — skills, tools, adapters, schemas, and agents remain modular.
- **Git safety** — destructive Git behavior requires explicit authorization.

## Current status

KMJ Forge is in **early development / v0.1.x bootstrap**.

The repository currently contains the initial Python package/CLI foundation, orchestration contracts, agent-role definitions, reusable skills, adapter structure, schemas, tests, examples, documentation, and the master engineering roadmap.

Roadmap intent is not presented as already-shipped capability.

## Repository map

| Path | Purpose |
|---|---|
| `src/kmj_forge/` | Executable Python package and CLI bootstrap |
| `core/` | Orchestration contracts, state-machine design, repository intelligence |
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

The roadmap is a strategic architecture document. The implementation version of this repository starts at `0.1.0` and advances through verified milestones.

## KMJ open-source ecosystem

Forge is intentionally independent, but it is part of the wider **KMJ TECHNO** engineering ecosystem.

- **[KMJ CodeBridge](https://github.com/kmjtechno/kmj-codebridge)** — securely connects AI assistants to authorized development projects.
- **[KMJ OmniDesk](https://github.com/kmjtechno/kmj-omnidesk)** — direct-first remote access focused on speed, resilience, and measurable trust.
- **[KMJ Desktop Commander](https://github.com/kmjtechno/kmj-desktop-commander)** — policy-controlled desktop and remote engineering operations.

Products such as **KMJ Calibration Pro** may consume Forge workflows, skills, tooling, and repository automation without becoming part of the Forge core.

## Security

Do not report security vulnerabilities through public issues.

See [SECURITY.md](SECURITY.md).

## Contributing

Useful contributions include reproducible bug reports, focused pull requests, adapters, tests, benchmark cases, and improvements to engineering contracts.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Help the project grow

If Forge's direction is useful to you:

- ⭐ **Star the repository** so more developers can discover it.
- 🐛 Open reproducible issues.
- 🧪 Add test and benchmark cases.
- 🛠️ Contribute focused improvements with evidence.
- 💡 Propose new adapters or workflows with clear acceptance criteria.

## License

Apache License 2.0. See [LICENSE](LICENSE).

---

<div align="center">

### Build fast. Verify everything.

**KMJ TECHNO · Innovate · Build · Scale**

[Website](https://kmjtechno.com) · [Star KMJ Forge](https://github.com/kmjtechno/kmj-forge/stargazers)

</div>
