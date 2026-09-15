# Git Workflow

## Protected main

`main` is the stable integration branch.

Recommended repository rules:

- pull request required before merge;
- required status checks;
- branch must be up to date before merge;
- conversations resolved;
- force-push disabled;
- branch deletion disabled;
- linear history preferred;
- administrator bypass minimized.

## Branches

- `feat/*`
- `fix/*`
- `docs/*`
- `test/*`
- `refactor/*`
- `chore/*`

## Merge

Default recommendation: squash merge for focused PRs.

Every merge should preserve:

- issue/goal;
- verification evidence;
- tests;
- known risks;
- rollback notes when relevant.
