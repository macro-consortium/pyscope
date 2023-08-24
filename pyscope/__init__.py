"""
What is pyscope?
================
:doc:`pyscope </index>` is an open-source Python package for
controlling astronomical instrumentation.

.. important::
  If you use :doc:`pyscope <index>` for data collection or work
  presented in a publication or talk, please help the project by
  properly `acknowledging or citing </cite>`_ the package.

The :doc:`pyscope </index>` open-source package
(:doc:`GNU AGPL-3.0 license </license>`) provides a set of tools
to rapidly and easily control astronomical instrumentation. It is
designed to be modular and extensible, allowing users to easily
add support for new devices and observatories. :doc:`pyscope </index>`
is built on top of the `ASCOM <https://ascom-standards.org/>`_
standard, but also provides support for non-ASCOM devices. Users may
also access their devices through third-party applications such as
`MaxIm DL <https://diffractionlimited.com/product/maxim-dl/>`_.
:doc:`pyscope </index>` also includes the :doc:`/api/pyscope.telrun`
module, which provides a simple interface for fully-robotic observatory
control.

:doc:`pyscope </index>` is aiming to become an
`affiliated package <https://www.astropy.org/affiliated/>`_.

Features
========
* Control observatory hardware with Python
* Support for both ASCOM and non-ASCOM devices
* :py:class:`~pyscope.observatory.Observatory` convenience methods like
  :py:meth:`~pyscope.observatory.Observatory.autofocus` and
  :py:meth:`~pyscope.observatory.Observatory.recenter`
* :py:mod:`pyscope.telrun` module for fully-robotic operation of
  an observatory
* Basic data reduction tools like
* Powered by Astropy,
  `Astropy-affiliated <https://www.astropy.org/affiliated/>`_
  packages, and `ASCOM <https://ascom-standards.org/>`_

"""

# isort: skip_file

import logging

from . import utils
from . import observatory
from . import telrun
from . import reduction
from . import analysis

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__all__ = ["analysis", "observatory", "reduction", "telrun", "utils"]
