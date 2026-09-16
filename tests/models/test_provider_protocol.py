import unittest

from kmj_forge.models.provider import ModelProvider


class ProviderProtocolTests(unittest.TestCase):
    def test_protocol_exposes_required_adapter_operations(self) -> None:
        operations = (
            "list_models",
            "generate",
            "stream",
            "tool_call",
            "cancel",
            "usage",
            "health_check",
        )
        for operation in operations:
            with self.subTest(operation=operation):
                self.assertTrue(callable(getattr(ModelProvider, operation, None)))


if __name__ == "__main__":
    unittest.main()
