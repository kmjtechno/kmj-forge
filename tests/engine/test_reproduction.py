from kmj_forge.engine.failure_classifier import FailureCategory, classify_failure
from kmj_forge.engine.reproduction import ReproductionAttempt, ReproductionManager


def test_reproduction_requires_matching_failure_category() -> None:
    manager = ReproductionManager()
    expected = classify_failure("TimeoutError: request timed out")

    result = manager.evaluate(
        expected,
        [ReproductionAttempt("pytest tests/test_api.py", "ConnectionError: refused", 1)],
    )

    assert result.reproduced is False
    assert result.matching_attempts == ()


def test_reproduction_is_deterministic_and_keeps_matching_attempts() -> None:
    manager = ReproductionManager()
    expected = classify_failure("AssertionError: test failed")
    attempts = [
        ReproductionAttempt("pytest tests/test_a.py", "AssertionError: test failed", 1),
        ReproductionAttempt("pytest tests/test_b.py", "AssertionError: failed test", 1),
    ]

    result = manager.evaluate(expected, attempts)

    assert result.reproduced is True
    assert result.category is FailureCategory.TEST
    assert result.matching_attempts == tuple(attempts)


def test_successful_command_cannot_count_as_reproduction() -> None:
    manager = ReproductionManager()
    expected = classify_failure("TypeError: bad value")

    result = manager.evaluate(
        expected,
        [ReproductionAttempt("python repro.py", "TypeError: bad value", 0)],
    )

    assert result.reproduced is False
