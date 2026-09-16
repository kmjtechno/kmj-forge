from __future__ import annotations

import re
from dataclasses import dataclass

from kmj_forge.protocol import Task

from .detect import ProjectDetection, detect_project
from .scan import RepoFile, ScanResult


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")
SYMBOL_PATTERNS = (
    re.compile(r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)"),
    re.compile(r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)"),
)


@dataclass(frozen=True, slots=True)
class ContextSnippet:
    path: str
    content: str


@dataclass(frozen=True, slots=True)
class ContextPacket:
    objective: str
    acceptance_criteria: tuple[str, ...]
    constraints: tuple[str, ...]
    permissions: tuple[str, ...]
    detection: ProjectDetection
    relevant_files: tuple[str, ...]
    snippets: tuple[ContextSnippet, ...]
    symbols: tuple[str, ...]
    git_diff: str
    diagnostics: tuple[str, ...]
    total_characters: int
    naive_characters: int


def normalize_instruction(instruction: str) -> str:
    if not isinstance(instruction, str):
        raise TypeError("instruction must be a string")
    return instruction


def _task_tokens(task: Task) -> tuple[str, ...]:
    text = " ".join((task.objective, *task.acceptance_criteria, *task.constraints)).lower()
    return tuple(sorted(set(TOKEN_RE.findall(text))))


def _score(item: RepoFile, tokens: tuple[str, ...]) -> int:
    path = item.path.lower()
    content = item.content.lower()
    score = 0
    for token in tokens:
        if token in path:
            score += 3
        if token in content:
            score += 1
    return score


def _symbols(snippets: tuple[ContextSnippet, ...]) -> tuple[str, ...]:
    result: set[str] = set()
    for snippet in snippets:
        for pattern in SYMBOL_PATTERNS:
            result.update(pattern.findall(snippet.content))
    return tuple(sorted(result))


def _metadata_characters(
    task: Task,
    permissions: tuple[str, ...],
    git_diff: str,
    diagnostics: tuple[str, ...],
) -> int:
    return sum(
        len(value)
        for value in (
            task.objective,
            *task.acceptance_criteria,
            *task.constraints,
            *permissions,
            git_diff,
            *diagnostics,
        )
    )


def compile_context(
    task: Task,
    scan: ScanResult,
    *,
    character_budget: int = 32_000,
    permissions: tuple[str, ...] = (),
    git_diff: str = "",
    diagnostics: tuple[str, ...] = (),
) -> ContextPacket:
    if character_budget < 1:
        raise ValueError("character_budget must be positive")
    if not isinstance(permissions, tuple) or any(not isinstance(value, str) for value in permissions):
        raise TypeError("permissions must be a tuple of strings")
    if not isinstance(diagnostics, tuple) or any(not isinstance(value, str) for value in diagnostics):
        raise TypeError("diagnostics must be a tuple of strings")

    objective = normalize_instruction(task.objective)
    tokens = _task_tokens(task)
    ranked = sorted(scan.files, key=lambda item: (-_score(item, tokens), item.path))
    fixed_chars = _metadata_characters(task, permissions, git_diff, diagnostics)
    if fixed_chars > character_budget:
        raise ValueError(
            f"metadata exceeds context budget: required={fixed_chars} budget={character_budget}"
        )
    remaining = character_budget - fixed_chars
    snippets: list[ContextSnippet] = []

    for item in ranked:
        if remaining <= 0:
            break
        content = item.content[:remaining]
        if not content:
            continue
        snippets.append(ContextSnippet(item.path, content))
        remaining -= len(content)

    snippet_tuple = tuple(snippets)
    total = fixed_chars + sum(len(item.content) for item in snippet_tuple)
    return ContextPacket(
        objective=objective,
        acceptance_criteria=task.acceptance_criteria,
        constraints=task.constraints,
        permissions=permissions,
        detection=detect_project(scan),
        relevant_files=tuple(item.path for item in snippet_tuple),
        snippets=snippet_tuple,
        symbols=_symbols(snippet_tuple),
        git_diff=git_diff,
        diagnostics=diagnostics,
        total_characters=total,
        naive_characters=scan.total_characters,
    )
