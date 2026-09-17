from kmj_forge.engine.failure_classifier import classify_failure
from kmj_forge.engine.hypothesis import HypothesisEngine
from kmj_forge.engine.reproduction import ReproductionAttempt, ReproductionManager


def test_hypotheses_require_a_reproduced_known_failure() -> None:
    expected = classify_failure("TimeoutError: request timed out")
    reproduction = ReproductionManager().evaluate(
        expected,
        [ReproductionAttempt("pytest tests/test_api.py", "ConnectionError: refused", 1)],
    )

    assert HypothesisEngine().generate(expected, reproduction) == ()


def test_hypotheses_are_deterministic_and_ranked() -> None:
    expected = classify_failure("AssertionError: test failed")
    reproduction = ReproductionManager().evaluate(
        expected,
        [ReproductionAttempt("pytest tests/test_a.py", "AssertionError: test failed", 1)],
    )

    hypotheses = HypothesisEngine().generate(expected, reproduction)

    assert [item.rank for item in hypotheses] == [1, 2]
    assert hypotheses[0].category is expected.category
    assert hypotheses[0].statement == "implementation behavior disagrees with the verified test expectation"
    assert hypotheses[1].statement == "test fixture or setup does not represent the intended behavior"


def test_unknown_failure_cannot_produce_hypotheses() -> None:
    expected = classify_failure("something unprecedented happened")
    reproduction = ReproductionManager().evaluate(
        expected,
        [ReproductionAttempt("python repro.py", "something unprecedented happened", 1)],
    )

    assert HypothesisEngine().generate(expected, reproduction) == ()
