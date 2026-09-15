# Tools

Tool contracts and reusable utilities live here.

Every production tool should define:

- typed inputs/outputs;
- permission class;
- timeout;
- cancellation;
- retry policy;
- structured errors;
- audit events;
- evidence output.

High-risk tools must require explicit authorization.
