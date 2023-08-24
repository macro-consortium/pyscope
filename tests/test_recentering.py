# Only necessary for testing development installations of the package
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt

# Import the package modules we need
import pyscope.analysis
import pyscope.observatory
import pyscope.reduction
import pyscope.telrun
import pyscope.utils

# zmags, zmags_err, fig, (ax0, ax1, ax2) = analysis.calc_zmag('tests/xwg206100c.fts', filt='G', threshold=10,
#                     plot=True, verbose=False)
# fig.savefig('tests/test_recentering.png')
# plt.show()
