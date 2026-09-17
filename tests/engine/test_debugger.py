from kmj_forge.engine.debugger import DebuggerAgent
from kmj_forge.engine.failure_classifier import classify_failure
from kmj_forge.engine.hypothesis import HypothesisEngine
from kmj_forge.engine.reproduction import ReproductionAttempt, ReproductionManager


def _diagnostic_inputs(message: str):
    failure = classify_failure(message)
    reproduction = ReproductionManager().evaluate(
        failure,
        [ReproductionAttempt("pytest tests/test_a.py", message, 1)],
    )
    hypotheses = HypothesisEngine().generate(failure, reproduction)
    return failure, reproduction, hypotheses


def test_debugger_requires_verified_reproduction_and_hypotheses() -> None:
    failure = classify_failure("TimeoutError: request timed out")
    reproduction = ReproductionManager().evaluate(
        failure,
        [ReproductionAttempt("pytest tests/test_api.py", "ConnectionError: refused", 1)],
    )

    assert DebuggerAgent().diagnose(failure, reproduction, ()) is None


def test_debugger_selects_deterministic_leading_hypothesis() -> None:
    failure, reproduction, hypotheses = _diagnostic_inputs("AssertionError: test failed")

    diagnosis = DebuggerAgent().diagnose(failure, reproduction, hypotheses)

    assert diagnosis is not None
    assert diagnosis.category is failure.category
    assert diagnosis.hypothesis == hypotheses[0]
    assert diagnosis.experiment == "inspect implementation behavior against the failing assertion"
    assert diagnosis.mutation_allowed is False


def test_debugger_rejects_mismatched_or_unranked_hypotheses() -> None:
    failure, reproduction, hypotheses = _diagnostic_inputs("AssertionError: test failed")
    timeout_failure, timeout_reproduction, timeout_hypotheses = _diagnostic_inputs(
        "TimeoutError: request timed out"
    )

    assert DebuggerAgent().diagnose(failure, reproduction, timeout_hypotheses) is None
    assert DebuggerAgent().diagnose(timeout_failure, timeout_reproduction, tuple(reversed(timeout_hypotheses))) is None
