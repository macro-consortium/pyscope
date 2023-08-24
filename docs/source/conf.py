import pathlib
import sys

sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

from urllib.parse import quote

from sphinx_astropy.conf.v2 import *

project = "pyscope"
copyright = "2023, Walter Golay"
author = "Walter Golay"
version = release = "0.1.0"

graphviz_dot = "/usr/local/bin/dot"

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/WWGolay/pyscope",
            "icon": "fa-brands fa-square-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/pyscope/",
            "icon": "fa-brands fa-python",
        },
        {
            "name": "macro",
            "url": "https://macroconsortium.org",
            "icon": "fa-solid fa-shuttle-space",
        },
    ]
}

extensions = list(map(lambda x: x.replace("viewcode", "linkcode"), extensions))

intersphinx_mapping["click"] = ("https://click.palletsprojects.com/en/8.1.x/", None)
intersphinx_mapping["astroquery"] = (
    "https://astroquery.readthedocs.io/en/latest/",
    None,
)
intersphinx_mapping["astroplan"] = ("https://astroplan.readthedocs.io/en/latest/", None)


def linkcode_resolve(domain, info):
    # print(f"domain={domain}, info={info}")
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = quote(info["module"].replace(".", "/"))
    if not filename.startswith("tests"):
        filename = "src/" + filename
    if "fullname" in info:
        anchor = info["fullname"]
        anchor = "#:~:text=" + quote(anchor.split(".")[-1])
    else:
        anchor = ""

    # github
    result = "https://<github>/<user>/<repo>/blob/master/%s.py%s" % (filename, anchor)
    # print(result)
    return result


extensions.append("sphinx_favicon")

html_logo = "images/pyscope_banner.png"
"""favicons = [
    "images/logo16.png",
    "images/logo32.png",
    "images/logo48.png",
    "images/logo128.png",
    "images/logo256.png",
    "images/pyscope.svg",
    "images/pyscope_transparent.svg"
]"""

extensions.append("sphinx.ext.doctest")

# extensions.append("sphinxcontrib.programoutput")
# extensions.append("sphinx_exec_code")
