"""Configuration files for building the documentation."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath("../src"))

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------

project = "docker-builder"
copyright = "2026, Balázs Paszkál Halmos"
author = "Balázs Paszkál Halmos"

try:
    # git describe --tags --long always yields: {tag}-{distance}-g{hash}
    raw = subprocess.check_output(
        ["git", "describe", "--tags", "--long"],
        stderr=subprocess.DEVNULL,
        text=True,
    ).strip()
    tag, distance, hash_ = raw.rsplit("-", 2)
    tag = tag.lstrip("v")
    release = tag if distance == "0" else f"{tag}+{hash_}"
except Exception:
    release = "unknown"

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "numpydoc",
]

# ---------------------------------------------------------------------------
# Autodoc / autosummary
# ---------------------------------------------------------------------------

autosummary_generate = True
add_module_names = False
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# ---------------------------------------------------------------------------
# numpydoc
# ---------------------------------------------------------------------------

numpydoc_show_class_members = True
numpydoc_class_members_toctree = False
numpydoc_attributes_as_param_list = True
numpydoc_xref_param_type = True

# ---------------------------------------------------------------------------
# Theme — pydata-sphinx-theme (same as NumPy)
# ---------------------------------------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/halmosb/docker-builder",
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "header_links_before_dropdown": 4,
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
