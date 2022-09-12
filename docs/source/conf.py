#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import subprocess
import sphinx_rtd_theme
import sys

sys.path.insert(0, os.path.abspath("../../"))

project = "freebandlib"
copyright = "2022, Reinis Cirpons and James D. Mitchell"
author = "Reinis Cirpons and James D. Mitchell"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinxcontrib.bibtex",
]

bibtex_bibfiles = []  # ["freebandlib.bib"]

autosummary_generate = True
add_module_names = False

templates_path = ["_templates"]
html_static_path = ["_static"]
source_suffix = ".rst"
master_doc = "index"
project = "freebandlib"
copyright = "2022, Reinis Cirpons + J. D. Mitchell"
author = "Reinis Cirpons + J. D. Mitchell"
version = "0.0.0"
release = "0.0.0"
language = None
exclude_patterns = ["_build"]
pygments_style = "sphinx"
highlight_language = "python"
todo_include_todos = False

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["_static"]
htmlhelp_basename = "freebandlib"

man_pages = [
    (
        master_doc,
        "freebandlib",
        "freebandlib Documentation",
        [author],
        1,
    )
]

intersphinx_mapping = {"https://docs.python.org/": None}

autoclass_content = "both"
