"""Tests for the main script."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, mock_open, patch

from docker_builder.generate import (
    DockerfileGenerator,
    main,
    parse_args,
)


class TestDockerfileGenerator(unittest.TestCase):
    """Main tests."""

    def setUp(self) -> None:
        """Create a temporary base directory."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.tmp_dir.name

        self.generator = DockerfileGenerator(
            base_dir=self.base_dir,
            use_root=True,
            include_latex=False,
        )

    def tearDown(self) -> None:
        """Cleanup temp directory."""
        self.tmp_dir.cleanup()

    def test_paths_initialization(self) -> None:
        """Test correct path construction."""
        self.assertTrue(self.generator.template_dir.endswith("templates"))
        self.assertTrue(self.generator.output_dir.endswith("generated"))

    @patch("docker_builder.generate.yaml.safe_load")
    def test_load_config(self, mock_yaml: MagicMock) -> None:
        """Test YAML config loading."""
        mock_yaml.return_value = {"key": "value"}

        with patch("builtins.open", mock_open(read_data="dummy")):
            cfg = self.generator.load_config()

        self.assertEqual(cfg, {"key": "value"})
        mock_yaml.assert_called_once()

    def test_ensure_output_dir(self) -> None:
        """Test output directory creation."""
        out_dir = self.generator.output_dir
        # self.assertFalse(os.path.exists(out_dir))

        self.generator.ensure_output_dir()

        self.assertTrue(os.path.exists(out_dir))

    def test_build_context(self) -> None:
        """Test context construction."""
        cfg = {
            "cuda": {"version": "12.0", "ubuntu": "22.04"},
            "pytorch": {"cpu_index": "cpu"},
        }

        ctx = self.generator._build_context(cfg, "3.10")

        self.assertEqual(ctx["python_version"], "3.10")
        self.assertEqual(ctx["cuda_version"], "12.0")
        self.assertEqual(ctx["ubuntu"], "22.04")
        self.assertTrue(ctx["use_root"])
        self.assertFalse(ctx["include_latex"])

    @patch("docker_builder.generate.Environment")
    def test_generate(self, mock_env_cls: MagicMock) -> None:
        """Test full generation flow with mocked templates."""
        # Mock config
        cfg = {
            "python_versions": ["3.10", "3.11"],
            "cuda": {"version": "12.0", "ubuntu": "22.04"},
            "pytorch": {"cpu_index": "cpu"},
        }

        # Mock templates
        mock_template = MagicMock()
        mock_template.render.return_value = "DOCKERFILE_CONTENT"

        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template
        mock_env_cls.return_value = mock_env

        self.generator.env = mock_env

        with (
            patch.object(self.generator, "load_config", return_value=cfg),
            patch("builtins.open", mock_open()) as m_open,
            patch("builtins.print") as mock_print,
        ):
            self.generator.generate()

        # Expect 4 files (2 versions × cpu/gpu)
        self.assertEqual(m_open.call_count, 4)

        # Ensure template rendering called
        self.assertTrue(mock_template.render.called)

        # Ensure logging happened
        self.assertEqual(mock_print.call_count, 2)


class TestCLI(unittest.TestCase):
    """Tests for the CLI."""

    def test_parse_args_defaults(self) -> None:
        """Test CLI default arguments."""
        with patch("sys.argv", ["prog"]):
            args = parse_args()

        self.assertFalse(args.root)
        self.assertFalse(args.latex)
        self.assertIsInstance(args.base_dir, str)

    def test_parse_args_flags(self) -> None:
        """Test CLI flags."""
        with patch("sys.argv", ["prog", "--root", "--latex", "--base-dir", "/tmp"]):
            args = parse_args()

        self.assertTrue(args.root)
        self.assertTrue(args.latex)
        self.assertEqual(args.base_dir, "/tmp")

    @patch("docker_builder.generate.DockerfileGenerator")
    def test_main(self, mock_gen_cls: MagicMock) -> None:
        """Test CLI entrypoint."""
        mock_instance = MagicMock()
        mock_gen_cls.return_value = mock_instance

        with patch("sys.argv", ["prog", "--root"]):
            main()

        mock_gen_cls.assert_called_once()
        mock_instance.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
