"""Tests for the main script."""

import os
import runpy
import shutil
import tempfile
import unittest
import warnings
from unittest.mock import MagicMock, mock_open, patch

from docker_builder.generate import (
    DockerfileGenerator,
    main,
    parse_args,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_CONFIG = """\
python_versions:
  - "3.12"
  - "3.13"

cuda:
  version: "13.2.1"
  ubuntu: "24.04"

pytorch:
  cpu_index: "https://download.pytorch.org/whl/cpu"
  gpu_index: "https://download.pytorch.org/whl/cu132"
"""


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
            "pytorch": {"cpu_index": "cpu", "gpu_index": "cu132"},
        }

        ctx = self.generator._build_context(cfg, "3.10")

        self.assertEqual(ctx["python_version"], "3.10")
        self.assertEqual(ctx["cuda_version"], "12.0")
        self.assertEqual(ctx["ubuntu"], "22.04")
        self.assertEqual(ctx["pytorch_gpu_index"], "cu132")
        self.assertTrue(ctx["use_root"])
        self.assertFalse(ctx["include_latex"])

    @patch("docker_builder.generate.Environment")
    def test_generate(self, mock_env_cls: MagicMock) -> None:
        """Test full generation flow with mocked templates."""
        # Mock config
        cfg = {
            "python_versions": ["3.10", "3.11"],
            "cuda": {"version": "12.0", "ubuntu": "22.04"},
            "pytorch": {"cpu_index": "cpu", "gpu_index": "cu132"},
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


class TestRealTemplates(unittest.TestCase):
    """Render the real templates into a temporary project tree."""

    def setUp(self) -> None:
        """Create a temporary project with config, templates and a src dir."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        root = self.tmp_dir.name

        shutil.copytree(
            os.path.join(REPO_ROOT, "templates"), os.path.join(root, "templates")
        )
        os.makedirs(os.path.join(root, "config"))
        with open(os.path.join(root, "config", "versions.yaml"), "w") as f:
            f.write(TEST_CONFIG)

        self.base_dir = os.path.join(root, "src")
        os.makedirs(self.base_dir)
        self.output_dir = os.path.join(root, "generated")

    def tearDown(self) -> None:
        """Cleanup temp directory."""
        self.tmp_dir.cleanup()

    def _read(self, name: str) -> str:
        with open(os.path.join(self.output_dir, name)) as f:
            return f.read()

    def _generate(self, use_root: bool, include_latex: bool) -> None:
        generator = DockerfileGenerator(
            base_dir=self.base_dir,
            use_root=use_root,
            include_latex=include_latex,
        )
        with patch("builtins.print"):
            generator.generate()

    def test_generates_all_files(self) -> None:
        """Test that a CPU and GPU Dockerfile is written per Python version."""
        self._generate(use_root=False, include_latex=False)

        self.assertEqual(
            sorted(os.listdir(self.output_dir)),
            [
                "Dockerfile.3.12.cpu",
                "Dockerfile.3.12.gpu",
                "Dockerfile.3.13.cpu",
                "Dockerfile.3.13.gpu",
            ],
        )
        self.assertIn("FROM python:3.12-slim", self._read("Dockerfile.3.12.cpu"))
        self.assertIn(
            "FROM docker.io/nvidia/cuda:13.2.1-cudnn-runtime-ubuntu24.04",
            self._read("Dockerfile.3.13.gpu"),
        )

    def test_non_root_without_latex(self) -> None:
        """Test the non-root variant without LaTeX packages."""
        self._generate(use_root=False, include_latex=False)

        for name in ("Dockerfile.3.12.cpu", "Dockerfile.3.12.gpu"):
            content = self._read(name)
            self.assertIn("ENV PRE_COMMIT_HOME=/opt/pre-commit-cache", content)
            self.assertIn("pre-commit install-hooks", content)
            self.assertIn("chown -R non_root:non_root ${PRE_COMMIT_HOME}", content)
            self.assertNotIn("ENV HOME=/root", content)

        self.assertNotIn("texlive-latex-base", self._read("Dockerfile.3.12.cpu"))

    def test_root_with_latex(self) -> None:
        """Test the root variant with LaTeX packages."""
        self._generate(use_root=True, include_latex=True)

        for name in ("Dockerfile.3.12.cpu", "Dockerfile.3.12.gpu"):
            content = self._read(name)
            self.assertIn("ENV HOME=/root", content)
            self.assertIn("pre-commit install-hooks", content)
            self.assertNotIn("chown -R non_root:non_root ${PRE_COMMIT_HOME}", content)

        self.assertIn("texlive-latex-base", self._read("Dockerfile.3.12.cpu"))

    def test_module_entrypoint(self) -> None:
        """Test running the module as ``__main__`` in-process."""
        argv = ["prog", "--no-root", "--base-dir", self.base_dir]
        with (
            patch("sys.argv", argv),
            patch("builtins.print"),
            warnings.catch_warnings(),
        ):
            # The module is already imported by this test file.
            warnings.simplefilter("ignore", RuntimeWarning)
            runpy.run_module("docker_builder.generate", run_name="__main__")

        self.assertEqual(len(os.listdir(self.output_dir)), 4)


if __name__ == "__main__":
    unittest.main()
