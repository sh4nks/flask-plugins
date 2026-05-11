from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# General --------------------------------------------------------------

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "sphinx_tabs.tabs",
    "pallets_sphinx_themes",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/sh4nks/flask-plugins/issues/%s", "#%s"),
    "pr": ("https://github.com/sh4nks/flask-plugins/pull/%s", "#%s"),
    "ghsa": (
        "https://github.com/sh4nks/flask-plugins/security/advisories/GHSA-%s",
        "GHSA-%s",
    ),
}

project = "Flask-Plugins"
copyright = "2014, sh4nks"
release, version = release, version = get_version("flask_plugins")

intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("PyPI Releases", "https://pypi.org/project/Flask-Plugins/"),
        ProjectLink("Source Code", "https://github.com/sh4nks/flask-plugins/"),
        ProjectLink("Issue Tracker", "https://github.com/sh4nks/flask-plugins/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_title = f"Flask-Plugins Documentation ({version})"
html_show_sourcelink = False
