import platform

import pytest

from pyscope.observatory import PWIAutofocus


@pytest.mark.skipif(
    platform.node() != "TCC1-MACRO", reason="Only works on TCC1-MACRO"
)
def test_pwi_autofocus():
    a = PWIAutofocus()

    best_position = a.Run(5, 120)
