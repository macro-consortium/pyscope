import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

from sphinx_astropy.conf.v2 import *

from urllib.parse import quote

project = 'pyscope'
copyright = '2023, Walter Golay'
author = 'Walter Golay'
version = release = '0.1.0'

graphviz_dot = '/usr/local/bin/dot'

extensions = list(map(lambda x: x.replace('viewcode', 'linkcode'), extensions))

def linkcode_resolve(domain, info):
    # print(f"domain={domain}, info={info}")
    if domain != 'py':
        return None
    if not info['module']:
        return None
    filename = quote(info['module'].replace('.', '/'))
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

intersphinx_mapping['click'] = ('https://click.palletsprojects.com/en/8.1.x/', None)