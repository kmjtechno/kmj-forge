# Contributing to KMJ Forge

Thank you for contributing.

## Development principles

KMJ Forge accepts changes that are:

- evidence-driven;
- scoped and reviewable;
- covered by appropriate tests;
- non-destructive to user work;
- compatible with the project's provider-, model-, language-, IDE-, and platform-agnostic direction.

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

python -m pip install -e .
python -m unittest discover -s tests -v
```

## Branch naming

Use focused branches:

- `feat/<short-name>`
- `fix/<short-name>`
- `docs/<short-name>`
- `refactor/<short-name>`
- `test/<short-name>`
- `chore/<short-name>`

Do not develop directly on `main`.

## Pull requests

Every PR should include:

1. problem or goal;
2. scope;
3. files changed;
4. verification commands;
5. exact test results;
6. risk and rollback notes where relevant.

A passing test is evidence only when it actually exercises the requirement.

## Commit guidance

Prefer small, coherent commits using conventional prefixes where practical:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `chore:`

## Security

Do not put secrets, credentials, private keys, customer data, or production tokens in issues, commits, tests, fixtures, or examples.

Security vulnerabilities should follow `SECURITY.md`.
