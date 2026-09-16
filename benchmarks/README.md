# Benchmarks

KMJ Forge benchmarks measure real engineering performance rather than optimizing for one benchmark suite.

Target task categories include:

- simple and complex bugs;
- new features;
- refactors;
- migrations;
- build-system failures;
- dependency conflicts;
- security fixes;
- performance optimization;
- long-horizon project work.

Primary metrics:

- verified success rate;
- human acceptance rate.

Secondary metrics:

- time;
- cost;
- token/context usage;
- regression rate;
- human intervention;
- retries and escalations.

## Alpha acceptance fixtures

`benchmarks/fixtures/` contains persistent Python, TypeScript, Rust, and mixed-project repositories used by `tests/acceptance/test_persistent_fixtures.py`.

With a 400-character context budget, CI run `35071970683` recorded:

| Fixture | Naive chars | Selected chars | Reduction |
| --- | ---: | ---: | ---: |
| Python | 1,368 | 400 | 70.76% |
| TypeScript | 1,062 | 400 | 62.34% |
| Rust | 1,016 | 400 | 60.63% |
| Mixed | 1,204 | 400 | 66.78% |

These fixtures are intentionally small and deterministic. They prove bounded context selection and language/build detection; they are not a claim about production-scale token savings. Larger benchmark suites should report the same measurements without weakening the character budget or relevance assertions.

Local benchmark outputs belong in `benchmarks/results/` and are ignored by Git.
