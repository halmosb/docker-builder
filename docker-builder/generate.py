"""
Script for generating custom docker images.

It features include:
- root and non root image
- optional latex packages
- git with custom commands
- vim with custom .vimrc file
"""

import os
import argparse
from typing import Dict, Any

import yaml
from jinja2 import Environment, FileSystemLoader


class DockerfileGenerator:
    """
    Generator for CPU and GPU Dockerfiles based on Jinja2 templates and YAML configuration.

    This class loads version configuration, prepares template contexts, and generates
    Dockerfiles for multiple Python versions with configurable features such as root
    user support and LaTeX package installation.

    Parameters
    ----------
    base_dir : str
        Root directory of the project.
    use_root : bool
        Whether to generate Dockerfiles that run as root user.
    include_latex : bool
        Whether to include LaTeX-related system dependencies.
    """

    def __init__(self, base_dir: str, use_root: bool, include_latex: bool) -> None:
        self.base_dir: str = base_dir
        self.template_dir: str = os.path.join(base_dir, "templates")
        self.output_dir: str = os.path.join(base_dir, "generated")

        self.use_root: bool = use_root
        self.include_latex: bool = include_latex

        self.env: Environment = Environment(
            loader=FileSystemLoader(self.template_dir)
        )

    def load_config(self) -> Dict[str, Any]:
        """
        Load YAML configuration file.

        Returns
        -------
        Dict[str, Any]
            Parsed configuration dictionary.
        """
        config_path = os.path.join(self.base_dir, "config", "versions.yaml")
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def ensure_output_dir(self) -> None:
        """
        Ensure that the output directory exists.
        """
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_context(self, cfg: Dict[str, Any], python_version: str) -> Dict[str, Any]:
        """
        Construct template context for a given Python version.

        Parameters
        ----------
        cfg : Dict[str, Any]
            Loaded configuration dictionary.
        python_version : str
            Python version string.

        Returns
        -------
        Dict[str, Any]
            Context dictionary passed to Jinja templates.
        """
        return {
            "python_version": python_version,
            "cuda_version": cfg["cuda"]["version"],
            "ubuntu": cfg["cuda"]["ubuntu"],
            "pytorch_cpu_index": cfg["pytorch"]["cpu_index"],
            "use_root": self.use_root,
            "include_latex": self.include_latex,
        }

    def generate(self) -> None:
        """
        Generate Dockerfiles for all configured Python versions.

        This method renders both CPU and GPU templates for each Python version
        and writes them into the output directory.
        """
        cfg = self.load_config()
        self.ensure_output_dir()

        cpu_template = self.env.get_template("Dockerfile.cpu.j2")
        gpu_template = self.env.get_template("Dockerfile.gpu.j2")

        for py in cfg["python_versions"]:
            ctx = self._build_context(cfg, py)

            cpu_out = os.path.join(self.output_dir, f"Dockerfile.{py}.cpu")
            gpu_out = os.path.join(self.output_dir, f"Dockerfile.{py}.gpu")

            with open(cpu_out, "w") as f:
                f.write(cpu_template.render(**ctx))

            with open(gpu_out, "w") as f:
                f.write(gpu_template.render(**ctx))

            print(
                f"Generated Python {py} | root={self.use_root} | latex={self.include_latex}"
            )


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments.

    Returns
    -------
    argparse.Namespace
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Generate Dockerfiles for CPU and GPU environments."
    )

    parser.add_argument(
        "--root",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Generate Dockerfiles running as root user.",
    )

    parser.add_argument(
        "--latex",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Include LaTeX packages.",
    )

    parser.add_argument(
        "--base-dir",
        type=str,
        default=os.path.dirname(os.path.dirname(__file__)),
        help="Project root directory.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Entry point for CLI execution.
    """
    args = parse_args()

    generator = DockerfileGenerator(
        base_dir=args.base_dir,
        use_root=args.root,
        include_latex=args.latex,
    )

    generator.generate()


if __name__ == "__main__":
    main()