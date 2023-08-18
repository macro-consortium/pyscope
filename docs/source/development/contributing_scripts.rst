Contributing scripts
====================

If you have a script that you think would be useful to others, please
consider contributing it to this repository. This page documents the 
procedure  for doing so. The general outline is as follows:


1. Fork `this repository <https://github.com/WWGolay/pyScope>`_ on GitHub. 
   this will create a copy of the repository in your own GitHub account, 
   which you are then free to modify. You can do this by clicking the
   "Fork" button on the top right of the page.

2. Clone your fork to your local machine by running the following command
   in a terminal::

       git clone https://github.com/<YourUsername>/pyScope

3. Decide which module your script belongs in:

   - :py:mod:`~pyscope.analysis` is for scripts that analyze data that has
     already been acquired and calibrated.
   - :py:mod:`~pyscope.reduction` is best-suited for scripts that perform
     a type of calibration or modification to the data that is not intended
     to elucidate any conclusions about the data itself. For example, the 
     :py:func:`~pyscope.reduction.ccd_calib` function applies a set of
     calibration frames to a raw image, but does not perform any analysis
     on the resulting image. Additionally, scripts in this module should
     not depend on any of the hardware modules.
   - :py:mod:`~pyscope.observatory` is a good choice for automating repetitive
     functions of the complete telescope system, such as collecting a set of
     calibration frames or grid-searching a portion of the sky. Scripts in 
     this module should at some point utilize the
     :py:obj:`~pyscope.observatory.Observatory` object.
   - :py:mod:`~pyscope.telrun` support the configuration, setup, and 
     execution of the `~pyscope.telrun.TelrunOperator` class. These scripts
     should assist users as they are configuring the fully-robotic observing
     mode. In general, most user-contributed scripts will not fit into this 
     module, however, there may be exceptions.
   - :py:mod:`~pyscope.utils` is for scripts that do not fit into any of the
     other modules. These scripts should be general-purpose and not depend
     on any of the other modules.

4. Turn your script into a function and isolate it in a single Python file.
   The function should be well-documented and should have a docstring that
   describes the function and its arguments. Your function should use the 
   `click <https://click.palletsprojects.com/>`_ package to define its
   command-line interface behavior. 

5. Add your script to the appropriate module's :file:`__init__.py` file. 
   This will make your script available to users who import the module.
   You should also add your script to the :file:`setup.py` file so that
   it will be installed when users install the package.

6. Commit your changes to your local repository and push them to your fork
   on GitHub. You can do this by running the following commands::

       git add <your_script>.py
       git commit -m "Added <your_script>.py"
       git push origin master

7. Create a pull request on GitHub. This will notify the maintainers of
   :py:mod:`~pyscope` that you have made changes to the repository and
   would like them to be incorporated into the main repository. You can
   do this by clicking the "Pull Request" button on the top right of the
   page. You should include a brief description of your changes in the
   pull request. The maintainers will review your changes and may ask
   you to make some modifications before they are accepted. Once your
   changes are accepted, they will be merged into the main repository
   and will be available to all users.

Congratulations! You have successfully contributed to :py:mod:`~pyscope`!

.. note:: 
    `Here <https://docs.astropy.org/en/stable/development/workflow/development_workflow.html>`_
    is the astropy-written guide to contributing to astropy and affiliated
    packages.

Building the script file
------------------------
For a script to have the full functionality required of it by the
:py:mod:`~pyscope` package, it must be built using some specific tools
and conventions. The :py:mod:`~pyscope` package uses the
`click <https://click.palletsprojects.com/>`_ package to define the
command-line interface of each script. This allows the user to run the
script from the command line with a set of options and arguments. For a 
function to retain its ability to be called as a importable function, the
main function with the :external:py:func:`click.command` decorator must
have a different name. We recommend using the same name as the script file
with the `_cli` suffix. For example::

   def my_script_cli(*args, **kwargs):
      # Do stuff here

The :external:py:func:`click.command` should include an epilog that
references this documentation::

   @click.command(epilog='''Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information.''')

You can also use the :external:py:func:`click.option` and the
:external:py:func:`click.argument` decorators to define the command-line
options and arguments. For example::

   @click.option('--option', '-o', default=1, help='An option')
   @click.argument('argument', type=click.Path(exists=True))
   def my_script_cli(*args, **kwargs):
      # Do stuff here

The script file should end in a line which sets the intended 
name of the script to the  defined function's `callback` attribute::

   my_script = my_script_cli.callback

:py:mod:`~pyscope` also uses the Python :py:mod:`logging` module to
provide a consistent logging interface for all scripts. This allows
the user to specify the verbosity of the script's output and to
redirect the output to a file. To use the logging module, you must
first import it and create a logger object. The logger object should
be the name of the file::

   import logging
   logger = logging.getLogger(__name__)

We recommend using a :external:py:func:`click.option` to set the
verbosity level::

   @click.option('-v', '--verbose', count=True, help='Increase verbosity')

A user can then set the verbosity level by passing the `-v` option multiple
times on the CLI, e.g.::
   
      $ my_script -vvv

We can connect the option to the logger level by adding the following
line to the function::

   logger.setLevel(10 * (3 - verbose))

At this point, the actual content of the function can be added. Once this
is complete, you should write a docstring for the function that describes
the function and its arguments. The docstring should be formatted using
the `numpydoc <https://numpydoc.readthedocs.io/en/latest/format.html>`_
format. The docstring should also include a description of the command-line
interface.

Once you've completed these steps, your function should be complete. 
The outline of your function should look like this::
   
   import click
   import logging

   logger = logging.getLogger(__name__)

   @click.command(epilog='''Check out the documentation at
                  https://pyscope.readthedocs.io/ for more
                  information.''')
   @click.option('--option', '-o', default=1, help='An option')
   @click.argument('argument', type=click.Path(exists=True))
   def my_script_cli(*args, **kwargs):
      '''A description of the function.

      Parameters
      ----------
      argument : str
         A description of the argument.
      option : int
         A description of the option.

      Returns
      -------
      None
      '''

      logger.setLevel(10 * (3 - verbose))
      logger.info('Starting my_script')
      # Do stuff here, logging output as needed
      # using logger.debug, logger.info, logger.warning,
      # logger.error, and logger.exception
      logger.info('Finished my_script')
   
   my_script = my_script_cli.callback

.. note::
   The :py:mod:`~pyscope` package uses the `sphinx <https://www.sphinx-doc.org/en/master/>`_
   package to generate documentation. Sphinx uses the `numpydoc <https://numpydoc.readthedocs.io/en/latest/format.html>`_
   format to parse docstrings. For more information on the numpydoc format,
   see the `numpydoc documentation <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

Preparing the script for distribution
-------------------------------------
Once you have written your script, you must add it to the appropriate
module's :file:`__init__.py` file::
   
      from .my_script import my_script

You should also add your script to the :file:`setup.cfg` file, referencing
the `_cli`-named version of the function and replacing underscores with
dashes::

   [options.entry_points]
   console_scripts =
      ...,
      my-script = pyscope.analysis.my_script:pyscope.module.my_script_cli

You can test your script by running::
   
      $ pip install --editable .

in your repository, then running::

      $ my-script --help

which should return an automatically-generated help message for your
script.