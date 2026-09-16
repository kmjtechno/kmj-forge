import unittest

from kmj_forge.engine import InvalidTransitionError, RunSnapshot, RunState, transition_state


class RunStateTests(unittest.TestCase):
    def test_happy_path_transitions_are_explicit_and_record_history(self) -> None:
        snapshot = RunSnapshot(
            run_id="run-1",
            task_id="task-1",
            state=RunState.RECEIVE,
            history=(RunState.RECEIVE,),
        )
        path = (
            RunState.CLASSIFY,
            RunState.DISCOVER,
            RunState.IMPLEMENT,
            RunState.TEST,
            RunState.REVIEW,
        )
        for state in path:
            snapshot = transition_state(snapshot, state)

        self.assertEqual(snapshot.state, RunState.REVIEW)
        self.assertEqual(snapshot.history, (RunState.RECEIVE, *path))

    def test_illegal_transition_is_rejected(self) -> None:
        snapshot = RunSnapshot("run-1", "task-1", RunState.RECEIVE, (RunState.RECEIVE,))
        with self.assertRaises(InvalidTransitionError):
            transition_state(snapshot, RunState.COMPLETE)

    def test_blocked_is_terminal_and_snapshot_round_trips(self) -> None:
        snapshot = RunSnapshot("run-2", "task-2", RunState.DISCOVER, (RunState.RECEIVE, RunState.CLASSIFY, RunState.DISCOVER))
        blocked = transition_state(snapshot, RunState.BLOCKED)

        self.assertEqual(RunSnapshot.from_dict(blocked.to_dict()), blocked)
        with self.assertRaises(InvalidTransitionError):
            transition_state(blocked, RunState.IMPLEMENT)


if __name__ == "__main__":
    unittest.main()
