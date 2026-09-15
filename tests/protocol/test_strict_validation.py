import unittest

from kmj_forge.protocol import EvidenceRecord, ModelCapability


class StrictProtocolValidationTests(unittest.TestCase):
    def test_model_capability_rejects_string_booleans_and_numbers(self) -> None:
        base = {
            "schema_version": "1.0",
            "provider": "provider",
            "model_id": "model",
            "capabilities": ["coding"],
            "context_window": 8192,
            "input_price_per_million": 0.0,
            "output_price_per_million": 0.0,
            "available": True,
            "local": False,
        }
        for field, invalid in (
            ("available", "false"),
            ("local", "true"),
            ("context_window", "8192"),
            ("input_price_per_million", "0"),
        ):
            with self.subTest(field=field):
                payload = dict(base)
                payload[field] = invalid
                with self.assertRaises((TypeError, ValueError)):
                    ModelCapability.from_dict(payload)
