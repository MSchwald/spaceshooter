from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Spaceinvaders'
copyright = '2025, Martin Schwald'
author = 'Martin Schwald'
release = '11.10.2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

autoapi_ignore = [str(p) + '/**' for p in project_root.iterdir() if p.is_dir() and p.name != 'docs'] + ['documentation.py','event.py','conf.py']

extensions = [
    'autoapi.extension',
    'sphinx.ext.autodoc',
    "sphinx.ext.autosummary",
    'sphinx.ext.napoleon'
]

autoapi_type = 'python'
autoapi_dirs = [str(project_root)]  # dein Quellcode
autoapi_options = ['members', 'undoc-members', 'show-inheritance']
autoapi_add_toctree_entry = True  # keine extra ToC-Einträge

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = ['_build',
                    'Thumbs.db',
                    '.DS_Store',
]

autodoc_mock_imports = ["pygame"]


# -- LaTeX output configuration ---------------------------------------------

latex_engine = 'pdflatex'  # or 'xelatex' if you need Unicode fonts

latex_elements = {
    # Prevent blank pages between chapters
    'classoptions': 'openany,oneside,nonumchapters',

    # Paper and font setup
    'papersize': 'a4paper',
    'pointsize': '11pt',

    # Margins and overall layout
    'sphinxsetup': 'hmargin=2cm, vmargin=2.5cm',

    # Font (Helvetica-style sans-serif)
    'fontpkg': r'\usepackage{helvet}\renewcommand{\familydefault}{\sfdefault}',

    # Mathematics packages (recommended for any equations)
    'preamble': r'''
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{microtype} % better text spacing
'''

    # Optional: remove title page if you want a clean start
    # 'maketitle': '',
}

# Master document (the main .rst file, usually 'index')
master_doc = 'modules'

# Keep language as English (default)
language = 'en'


latex_documents = [
    (
        'modules',          # normalerweise 'index'
        'spaceinvaders.tex', # Name der LaTeX-Datei
        'Spaceinvaders Documentation',  # Titel
        'Martin Schwald',         # Autor
        'manual'            # Dokumentenklasse: 'manual' oder 'howto'
    )
]
