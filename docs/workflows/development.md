# Development Workflow

## Standard change

`RECEIVE → DISCOVER → SPECIFY → PLAN → IMPLEMENT → TEST → REVIEW → REGRESSION → COMPLETE`

## Bug fix

1. collect exact failure;
2. reproduce;
3. minimize reproduction;
4. inspect logs/control flow;
5. form hypotheses;
6. run discriminating tests;
7. identify root cause;
8. implement minimal correct fix;
9. add regression coverage;
10. rerun original reproduction;
11. run relevant suite;
12. record evidence.

Random patch loops, deleting tests, hiding failures, and disabling checks are prohibited.
