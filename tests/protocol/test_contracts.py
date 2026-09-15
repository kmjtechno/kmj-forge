import json
import unittest
from pathlib import Path

from kmj_forge.protocol import EvidenceRecord, ModelCapability, Task


ROOT = Path(__file__).resolve().parents[2]


class ProtocolContractTests(unittest.TestCase):
    def test_task_round_trip_preserves_contract(self) -> None:
        task = Task(
            task_id="task-001",
            objective="Fix the failing parser test",
            acceptance_criteria=("parser test passes",),
            constraints=("no paid model",),
            requested_capabilities=("coding", "tool_use"),
        )
        self.assertEqual(Task.from_dict(task.to_dict()), task)
        self.assertEqual(task.schema_version, "1.0")

    def test_model_capability_round_trip_preserves_routing_fields(self) -> None:
        model = ModelCapability(
            provider="local",
            model_id="coder-model",
            capabilities=("coding", "tool_use"),
            context_window=32768,
            input_price_per_million=0.0,
            output_price_per_million=0.0,
            available=True,
            local=True,
        )
        self.assertEqual(ModelCapability.from_dict(model.to_dict()), model)
        self.assertTrue(model.is_free)
        self.assertEqual(model.schema_version, "1.0")

    def test_evidence_record_round_trip_preserves_audit_fields(self) -> None:
        evidence = EvidenceRecord(
            evidence_id="ev-001",
            task_id="task-001",
            kind="test",
            status="PASS",
            timestamp="2026-09-15T16:00:00Z",
            command="python -m unittest",
            environment={"python": "3.13"},
            changed_files=("src/kmj_forge/protocol/models.py",),
            artifacts=("test-output.txt",),
        )
        self.assertEqual(EvidenceRecord.from_dict(evidence.to_dict()), evidence)
        self.assertEqual(evidence.schema_version, "1.0")

    def test_json_schemas_match_python_contract_required_fields(self) -> None:
        expected = {
            "task.schema.json": {"schema_version", "task_id", "objective"},
            "model-capability.schema.json": {
                "schema_version", "provider", "model_id", "capabilities",
                "context_window", "available", "local",
            },
            "evidence.schema.json": {
                "schema_version", "evidence_id", "task_id", "kind", "status", "timestamp",
            },
        }
        for filename, required in expected.items():
            schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertTrue(required.issubset(set(schema["required"])), filename)
            self.assertEqual(schema["properties"]["schema_version"]["const"], "1.0")


if __name__ == "__main__":
    unittest.main()
