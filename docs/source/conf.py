import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

from sphinx_astropy.conf import *

project = 'pyscope'
copyright = '2023, Walter Golay'
author = 'Walter Golay'
release = '0.1.0'

templates_path = ['_templates']
html_static_path = ['_static']

needs_sphinx = '4.2'
extensions += ['sphinx_copybutton']

# For sphinx-copybutton
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "collapse_navigation": True,
    "icon_links": [],
    "navigation_depth": 2,
    "show_nav_level": 2,
    "use_edit_page_button": False
}