#from nose.commands import nosetests
from setuptools.extension import Extension
from paver.easy import *
from paver.setuputils import setup
from setuptools import find_packages

try:
    # Optional tasks, only needed for development
    import paver.doctools
    import paver.misctasks
    from paved import *
    from paved.dist import *
    from paved.util import *
    from paved.docs import *
    from paved.pycheck import *
    from sphinxcontrib import paverutils
    ALL_TASKS_LOADED = True
except ImportError, e:
    info("some tasks could not not be imported.")
    debug(str(e))
    ALL_TASKS_LOADED = False

def read_project_version(py=None, where='.', exclude=['bootstrap', 'pavement', 'doc', 'docs', 'test', 'tests', ]):
    if not py:
        py = path(where) / find_packages(where=where, exclude=exclude)[0]
    py = path(py)
    if py.isdir():
        py = py / '__init__.py'
    __version__ = None
    for line in py.lines():
        if '__version__' in line:
            exec line
            break
    return __version__

NAME = 'pysimavr'
URL = 'https://github.com/ponty/pysimavr'
DESCRIPTION = 'python wrapper for simavr which is AVR and arduino simulator.'
VERSION = read_project_version()


classifiers = [
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ]

install_requires = [
    'setuptools',
    'path.py',
    'pyavrutils',
    'entrypoint2',
    'path.py',
    ]

def part(name):
    return Extension(name='pysimavr.swig._' + name,
            sources=map(str, [
           'pysimavr/swig/parts/' + name + '.c'  ,
           'pysimavr/swig/' + name + '.i',
           'pysimavr/swig/sim/sim_cycle_timers.c',
           'pysimavr/swig/sim/sim_irq.c',
           'pysimavr/swig/sim/sim_io.c',
             ]
              ),
            libraries=['elf'],
            include_dirs=[  
                          'pysimavr/swig/sim',
                          'pysimavr/swig/include',
                          'pysimavr/swig/parts',
                         ],
            swig_opts=[
#                       '-modern', 
                       '-Ipysimavr/swig/parts'
                       ],
            extra_compile_args=[
                                '--std=gnu99',
                                ],
            )
    
ext_modules = [
            Extension(name='pysimavr.swig._simavr',
            sources=map(str, [
           'pysimavr/swig/simavr.i',
             ]
           + path('pysimavr/swig/sim').files('*.c')
           + path('pysimavr/swig/cores').files('sim_*.c')
              ),
            libraries=['elf'],
            include_dirs=[  
                          'pysimavr/swig/sim',
                          'pysimavr/swig/include',
                         ],
            swig_opts=[
#                       '-modern', 
                       '-Ipysimavr/swig/sim'
                       ],
            extra_compile_args=[
                                '--std=gnu99',
                                ],
            ),
            part('sgm7'),
            part('ledrow'),
            part('inverter'),
            part('hd44780'),
            part('ac_input'),
            part('button'),
            part('uart_udp'),
            part('spk'),
               ]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.rst', 'r').read(),
    classifiers=classifiers,
    keywords='avr simavr',
    author='ponty',
    #author_email='',
    url=URL,
    license='GPL',
    packages=find_packages(exclude=['bootstrap', 'pavement', ]),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    install_requires=install_requires,
    ext_modules=ext_modules,
    )


options(
    sphinx=Bunch(
        docroot='docs',
        builddir="_build",
        ),
    pdf=Bunch(
        builddir='_build',
        builder='latex',
    ),
    )

if ALL_TASKS_LOADED:
    
    options.paved.clean.patterns += ['*.pickle',
                                     '*.doctree',
                                     '*.gz' ,
                                     'nosetests.xml',
                                     'sloccount.sc',
                                     '*.pdf', '*.tex',
                                     '*.png',
                                     '*.o', '*.os', # object files
                                     '*.so', # libs
                                     '*_wrap.c', # generated by swig      
                                     '*.vcd',
                                     ]

    options.paved.dist.manifest.include.remove('distribute_setup.py')
    options.paved.dist.manifest.recursive_include.add('pysimavr *.h')

        
        
    @task
    @needs('scons', 'sloccount', 'html', 'pdf', 'sdist', 'nose')
    def alltest():
        'all tasks to check'
        pass
    
    @task
    @needs('sphinxcontrib.paverutils.html')
    def html():
        pass

   
    @task
    @needs('sphinxcontrib.paverutils.pdf')
    def pdf():
        'Generate PDF output and copy into html directory'
        fpdf = list(path('docs/_build/latex').walkfiles('*.pdf'))[0]
        d = path('docs/_build/html')
        d.makedirs()
        fpdf.copy(d)

    @task
#    @needs('paved.paved.clean') # this does not work! strange
    def clean(options, info):
        paved.clean(options, info)
        info("Cleaning swig files")
        d = path('pysimavr') / 'swig'
        for x in d.walkfiles('*.py'):            
            if path(x).stripext() + '.i' in d.files('*.i'):
                x.remove()

    @task
    def scons():
        sh('scons', cwd='pysimavr/swig')

    @task
    @needs('bdist_egg', 'sdist', 'distutils.command.upload')
    def upload():
        pass
