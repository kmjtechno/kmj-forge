import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_run_record_schema_is_valid_json_and_has_required_keys(self) -> None:
        path = ROOT / "schemas" / "run-record.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "KMJ Forge Run Record")
        self.assertEqual(schema["type"], "object")
        self.assertEqual(
            schema["required"],
            ["run_id", "task_id", "final_status"],
        )


if __name__ == "__main__":
    unittest.main()
