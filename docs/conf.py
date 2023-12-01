# -*- coding: utf-8 -*-
import pytool

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode", "sphinx.ext.intersphinx"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "pytool"
copyright = "2012, Jacob Alheid"

# The short X.Y version.
version = pytool.__version__
# The full version, including alpha/beta/rc tags.
release = pytool.__version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "simplejson": ("https://simplejson.readthedocs.io/en/latest/", None),
}

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "default"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "pytooldoc"

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "pytool", "pytool Documentation", ["Author"], 1)]

# Options for Epub output
# Bibliographic Dublin Core info.
epub_title = "pytool"
epub_author = "Jacob Alheid"
epub_publisher = "Jacob Alheid"
epub_copyright = "2012, Jacob Alheid"
