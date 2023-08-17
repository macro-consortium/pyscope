from setuptools import setup

setup(
    name = 'pyscope', 
    
    version = '0.1.0',
    
    description = '',
    
    py_modules = ['pyscope'],

    package_dir = {'':'src'},
    
    # If you have many modules included in your package, you want to use the following parameter instead of py_modules.
#     packages = ['ThePackageName1',
#                 'ThePackageName2',
#                 ...
#  ],
    
    author = 'Walter Golay',
    author_email = 'wgolay30@gmail.com',
    

    long_description = open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
    long_description_content_type = "text/markdown",
    
    url='https://github.com/WWGolay/pyScope',
    
    include_package_data=True,
    
    # https://pypi.org/classifiers/
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
    
    install_requires = [
        'Click',
    ],

    entry_points={
        'console_scripts': [
            'init-telrun-dir = pyscope.telrun:init_telrun_dir_cli',
            'init-remote-dir = pyscope.telrun:init_remote_dir_cli',
            'schedtel = pyscope.telrun:schedtel_cli',
            'plot-schedule-gantt = pyscope.telrun:plot_schedule_gantt_cli',
            'start-telrun = pyscope.telrun:start_telrun_cli',
            'start-syncfiles = pyscope.telrun:start_syncfiles_cli',
            'syncfiles = pyscope.telrun:syncfiles_cli',
            'calc-zmag = pyscope.analysis.calc_zmag_cli',
            'collect-calibration-set = pyscope.observatory.collect_calibration_set_cli',
            'avg-fits = pyscope.reduction.avg_fits_cli',
        ],
    },
    
    keywords = ['python', 'automation', 'astronomy',
                'ascom', 'astropy', 'observatory'],
    
)