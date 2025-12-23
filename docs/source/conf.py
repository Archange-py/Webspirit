# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version

project = 'Webspirit'
copyright = '2025, Archange'
author = 'Archange'

release = version("webspirit")
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",        # Google / NumPy style docstrings
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_multiversion",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

autosummary_generate = True
autoclass_content = "both"

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# Configure the versions to include
smv_tag_whitelist = r'^v\d+\.\d+$' # Include tags like v1.0, v2.0, etc
smv_branch_whitelist = r'^main$' # Include the main branch
smv_remote_whitelist = r'^origin$' # Include the origin remote
smv_released_pattern = r'^refs/tags/v\d+\.\d+$' # Pattern for released versions

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "logo": { "text": "webspirit" },
    "github_url": "https://github.com/Archange-py/Webspirit",
    "navbar_end": ["search-field.html", "version-switcher"],
    "icon_links": [
        {"name": "PyPI", "url": "https://pypi.org/project/webspirit/", "icon": "fas fa-box"}
    ],
    # d'autres options : header_links, collapse_navigation, analytics, etc.
}
html_static_path = ["_static"]
# html_logo = "_static/logo-128.png"
