'''

***************************************
Telescope Control with Python (pyscope)
***************************************

What is pyscope?
================
:doc:`pyscope </index>` is an open-source Python package for 
controlling astronomical instrumentation.

.. important::
  If you use :doc:`pyscope </index>` for data collection or work 
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
`MaxIm DL <https://diffractionlimited.com/product/maxim-dl/>`_ and 
`TheSkyX <https://www.bisque.com/the-sky-x-professional-edition/>`_. 
:doc:`pyscope </index>` also includes the :doc:`~/api/pyscope.telrun` 
module, which provides a simple interface for fully-robotic observatory 
control.

:doc:`pyscope </index>` is aiming to become an 
`Astropy <https://www.astropy.org/>`_ 
`affiliated package <https://www.astropy.org/affiliated/>`_.

Features
========
* Control observatory hardware with Python
* Support for both ASCOM and non-ASCOM devices
* :doc:`~/api/pyscope.Observatory` convenience methods like 
  :doc:`~/api/pyscope.Observatory._autofocus and 
  :doc:`~/api/pyscope.Observatory._recenter`
* :doc:`~/api/pyscope.telrun` module for fully-robotic operation of 
  an observatory
* Basic data reduction tools like
* Powered by `Astropy <https://www.astropy.org/>`_, 
  `Astropy-affiliated <https://www.astropy.org/affiliated/>`_ 
  packages, and `ASCOM <https://ascom-standards.org/>`_


Getting Started
===============
* :doc:`What's New </whats-new>`
* :doc:`Installation </installation>`
* :doc:`Quickstart </quickstart>`
* :doc:`How-to Guides </how-to>`
* :doc:`Example Gallery </examples>`
* :doc:`Get Help </help>`
* `Report Problems <https://github.com/WWGolay/pyScope/issues>`_
* :doc:`Cite pyscope </cite>`
* :doc:`About pyscope </about>`
* :doc:`License </license>`

User Documentation
==================
How-to Guides
-------------
* :doc:`Set up a robotic observatory </how-to/robotic>`
* :doc:`Set up a remote control server </how-to/remote-server>`

Modules
-------
* :doc:`pyscope.Observatory </api/pyscope.Observatory>`
* :doc:`pyscope.drivers </api/pyscope.drivers>`

  * :doc:`pyscope.drivers.ascom </api/pyscope.drivers.ascom>`

* :doc:`pyscope.telrun </api/pyscope.telrun>`
* :doc:`pyscope.utils </api/pyscope.utils>`

Other Details
-------------
* :doc:`Configuration Files </setup-reference/config>`
* :doc:`Logging setup </setup-reference/logging>`


Developer Documentation
=======================
How to Guides
-------------
* :doc:`Write a custom driver </how-to/custom-driver>`
* :doc:`Contribute to pyscope </how-to/contribute>`

Modules
-------
* :doc:`pyscope.drivers.abstract </api/pyscope.drivers.abstract>`

Authors
=======
* Walter Golay, Former Undergraduate at the University of Iowa and 
  Graduate Student at Harvard University, Department of Astronomy


Acknowledgements
================
* Robert Mutel, Professor Emeritus at University of Iowa, 
  Department of Physics and Astronomy
* The former students and contributors to the 
  Iowa Robotic Telescope Facility (RTF), the Van Allen Observatory 
  (VAO), and the Iowa Robotic Observatory (IRO), including the 
  Rigel Telescope and the Gemini Telescope, now known as the 
  *Robert L. Mutel Telescope* (RLMT).
* The Macalester-Augustana Coe Robotic Observatory 
  (`MACRO <https://macroconsortium.org>`_) 
  Consortium for providing unrestricted access to the 
  *Robert L. Mutel Telescope* for testing the early iterations of 
  this software.

  * John Cannon, Professor at Macalester College, Department of 
    Physics and Astronomy
  * William Peterson, Professor at Augustana College, Department 
    of Physics and Astronomy
  * James Wetzel, Professor at Coe College, Department of Physics

* Mark and Pat Trueblood, Directors of the 
  `Winer Observatory <https://www.winer.org/>`_ where the 
  *Robert L. Mutel Telescope* is located
* Kevin Ivarsen
* The astronomy faculty and staff at the University of Iowa, 
  Department of Physics and Astronomy

'''


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
__version__ = '0.1.0'

from .utils import *
from .observatory import Observatory