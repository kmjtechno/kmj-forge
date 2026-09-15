import io
import unittest
from contextlib import redirect_stdout

from kmj_forge.cli import main


class CliTests(unittest.TestCase):
    def test_version(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().strip(), "KMJ Forge 0.1.0")

    def test_bootstrap_message(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([])
        self.assertEqual(code, 0)
        self.assertIn("KMJ Forge bootstrap is ready.", out.getvalue())


if __name__ == "__main__":
    unittest.main()
