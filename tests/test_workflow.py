"""Module for integration tests."""

import subprocess
import sys
import unittest


class TestEntrypointSubprocess(unittest.TestCase):
    """Integration test."""

    def test_script_execution(self) -> None:
        """Test running the script via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "docker_builder.generate", "--no-root"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
